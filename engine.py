"""DuckDB ingestion and safe SQL execution engine."""

import re
import time
from dataclasses import dataclass, field
from typing import Any

import duckdb
import pandas as pd


@dataclass
class QueryResult:
    df: pd.DataFrame
    row_count: int
    columns: list[str]
    execution_time_ms: float
    warnings: list[str] = field(default_factory=list)
    error: str | None = None


_ALLOWED_START = re.compile(r"^\s*(SELECT|WITH)\b", re.IGNORECASE)
_ALLOWED_CLEANING_START = re.compile(
    r"^\s*(UPDATE|ALTER\s+TABLE|CREATE\s+OR\s+REPLACE\s+TABLE)\b", re.IGNORECASE
)
# Match a semicolon that is not inside a single-quoted string.
# We strip single-quoted strings (handling escaped '' inside them) before checking.
_STRIP_STRINGS = re.compile(r"'(?:[^'\\]|\\.)*'", re.DOTALL)
_MULTI_STATEMENT = re.compile(r";\s*\S", re.DOTALL)


def _validate_sql(sql: str) -> str | None:
    """Return an error string if the SQL is not allowed, else None."""
    stripped = sql.strip()
    if not _ALLOWED_START.match(stripped):
        return "Only SELECT or WITH queries are allowed."
    # Strip string literals (handles escaped quotes and backslash escapes)
    cleaned = _STRIP_STRINGS.sub("''", stripped)
    # Also strip double-quoted identifiers
    cleaned = re.sub(r'"(?:[^"\\]|\\.)*"', '""', cleaned)
    if _MULTI_STATEMENT.search(cleaned):
        return "Multi-statement queries are not allowed."
    return None


def load_csv(path: str, con: duckdb.DuckDBPyConnection) -> list[str]:
    """
    Load a CSV file into DuckDB as the table 'data'.
    Returns a list of warning strings.
    """
    warnings: list[str] = []
    con.execute("DROP TABLE IF EXISTS data")
    # Escape single quotes in the path (DuckDB uses '' to escape a literal quote)
    escaped_path = path.replace("'", "''")
    con.execute(
        f"""
        CREATE TABLE data AS
        SELECT * FROM read_csv('{escaped_path}',
            auto_detect=true,
            null_padding=true,
            ignore_errors=false
        )
        """
    )
    return warnings


def run_cleaning_sql(sql: str, con: duckdb.DuckDBPyConnection) -> str | None:
    """
    Execute a cleaning SQL statement (UPDATE / ALTER TABLE / CREATE OR REPLACE TABLE).
    Returns an error string on failure, or None on success.
    Only statements that reference the 'data' table are accepted.
    """
    stripped = sql.strip()
    if not _ALLOWED_CLEANING_START.match(stripped):
        return (
            "Cleaning SQL must start with UPDATE, ALTER TABLE, "
            "or CREATE OR REPLACE TABLE."
        )
    # Require that the statement references 'data' (simple guard)
    if "data" not in stripped.lower():
        return "Cleaning SQL must reference the 'data' table."
    try:
        con.execute(stripped)
        return None
    except Exception as exc:  # noqa: BLE001
        return str(exc)


def run_query(sql: str, con: duckdb.DuckDBPyConnection) -> QueryResult:
    """Execute a validated SQL query and return a QueryResult."""
    error = _validate_sql(sql)
    if error:
        return QueryResult(
            df=pd.DataFrame(),
            row_count=0,
            columns=[],
            execution_time_ms=0.0,
            error=error,
        )

    warnings: list[str] = []
    try:
        start = time.perf_counter()
        rel = con.execute(sql)
        df: pd.DataFrame = rel.df()
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        if df.empty:
            warnings.append("Query returned no rows.")
        return QueryResult(
            df=df,
            row_count=len(df),
            columns=list(df.columns),
            execution_time_ms=elapsed_ms,
            warnings=warnings,
        )
    except duckdb.CatalogException as exc:
        msg = str(exc)
        # Try to extract available columns hint
        col_hint = _column_hint(msg, con)
        return QueryResult(
            df=pd.DataFrame(),
            row_count=0,
            columns=[],
            execution_time_ms=0.0,
            error=msg + (f"\n\nAvailable columns: {col_hint}" if col_hint else ""),
        )
    except Exception as exc:  # noqa: BLE001
        return QueryResult(
            df=pd.DataFrame(),
            row_count=0,
            columns=[],
            execution_time_ms=0.0,
            error=str(exc),
        )


def _column_hint(error_msg: str, con: duckdb.DuckDBPyConnection) -> str | None:
    """Return available column names from the 'data' table if it exists."""
    try:
        cols = con.execute("SELECT column_name FROM information_schema.columns WHERE table_name='data'").fetchall()
        if cols:
            return ", ".join(c[0] for c in cols)
    except Exception:  # noqa: BLE001
        pass
    return None


# ── Filter and Aggregation SQL builders ───────────────────────────────────────

_NUMERIC_TYPES: frozenset[str] = frozenset({
    "BIGINT", "INTEGER", "DOUBLE", "FLOAT", "DECIMAL", "HUGEINT",
    "SMALLINT", "TINYINT", "UBIGINT", "UINTEGER", "REAL", "INT", "INT4",
    "INT8", "FLOAT4", "FLOAT8",
})

FILTER_OPS: list[str] = [
    "=", "!=", ">", ">=", "<", "<=", "LIKE", "NOT LIKE", "IS NULL", "IS NOT NULL",
]
_NO_VALUE_OPS: frozenset[str] = frozenset({"IS NULL", "IS NOT NULL"})

AGG_FUNCS: list[str] = ["COUNT", "COUNT DISTINCT", "SUM", "AVG", "MIN", "MAX"]


def _quote_col(col: str) -> str:
    """Double-quote a column name for use in DuckDB SQL."""
    return '"' + col.replace('"', '""') + '"'


def _quote_str_val(val: str) -> str:
    """Single-quote a string value for use in DuckDB SQL."""
    return "'" + val.replace("'", "''") + "'"


def build_filter_sql(
    col: str,
    op: str,
    value: str,
    valid_cols: list[str],
    col_type: str = "",
) -> tuple[str, str | None]:
    """
    Build a safe ``SELECT * FROM data WHERE ...`` query.
    Returns ``(sql, error)``; error is None on success.
    """
    if col not in valid_cols:
        return "", f"Column {col!r} not found. Available: {', '.join(valid_cols)}"
    if op not in FILTER_OPS:
        return "", f"Operator {op!r} is not allowed."

    qcol = _quote_col(col)

    if op in _NO_VALUE_OPS:
        return f"SELECT * FROM data WHERE {qcol} {op}", None

    base_type = col_type.upper().split("(")[0].strip()
    if base_type in _NUMERIC_TYPES:
        try:
            num = float(value)
            val_sql = str(int(num)) if num == int(num) else str(num)
        except ValueError:
            return (
                "",
                f"Column '{col}' has numeric type {col_type}; "
                f"value {value!r} is not a valid number.",
            )
    else:
        val_sql = _quote_str_val(value)

    return f"SELECT * FROM data WHERE {qcol} {op} {val_sql}", None


def build_agg_sql(
    group_cols: list[str],
    agg_col: str,
    agg_func: str,
    valid_cols: list[str],
) -> tuple[str, str | None]:
    """
    Build a safe aggregation query (GROUP BY … or whole-table aggregate).
    Returns ``(sql, error)``; error is None on success.
    """
    for col in group_cols:
        if col not in valid_cols:
            return "", f"Group-by column {col!r} not found. Available: {', '.join(valid_cols)}"
    if agg_func not in AGG_FUNCS:
        return "", f"Aggregation function {agg_func!r} is not allowed."

    if agg_func == "COUNT":
        agg_expr = "COUNT(*)"
        agg_alias = "count"
    elif agg_func == "COUNT DISTINCT":
        if agg_col not in valid_cols:
            return "", f"Aggregation column {agg_col!r} not found. Available: {', '.join(valid_cols)}"
        agg_expr = f"COUNT(DISTINCT {_quote_col(agg_col)})"
        agg_alias = "count_distinct"
    else:
        if agg_col not in valid_cols:
            return "", f"Aggregation column {agg_col!r} not found. Available: {', '.join(valid_cols)}"
        agg_expr = f"{agg_func}({_quote_col(agg_col)})"
        agg_alias = agg_func.lower()

    agg_alias_quoted = _quote_col(agg_alias)

    if group_cols:
        group_exprs = ", ".join(_quote_col(c) for c in group_cols)
        select_exprs = f"{group_exprs}, {agg_expr} AS {agg_alias_quoted}"
        sql = f"SELECT {select_exprs} FROM data GROUP BY {group_exprs} ORDER BY {group_exprs}"
    else:
        sql = f"SELECT {agg_expr} AS {agg_alias_quoted} FROM data"

    return sql, None
