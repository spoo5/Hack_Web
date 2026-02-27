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
