"""Data profiling utilities using DuckDB."""

import re
from dataclasses import dataclass

import duckdb
import pandas as pd

_SAFE_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
HIGH_NULL_THRESHOLD = 0.5  # columns with null_count > this fraction are flagged


@dataclass
class ColumnProfile:
    name: str
    dtype: str
    null_count: int
    non_null_count: int


@dataclass
class TableProfile:
    row_count: int
    columns: list[ColumnProfile]


def _validate_identifier(name: str) -> None:
    if not _SAFE_IDENTIFIER.match(name):
        raise ValueError(f"Invalid identifier: {name!r}")


def profile_table(con: duckdb.DuckDBPyConnection, table: str = "data") -> TableProfile:
    """Return basic profiling info for *table* in the given DuckDB connection."""
    _validate_identifier(table)

    row_count: int = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]  # type: ignore[index]

    schema_rows = con.execute(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_name=? ORDER BY ordinal_position",
        [table],
    ).fetchall()

    if not schema_rows:
        return TableProfile(row_count=row_count, columns=[])

    # Build a single query to count NULLs for all columns in one pass
    null_exprs = ", ".join(
        f'COUNT(*) FILTER (WHERE "{col}" IS NULL) AS "{col}"'
        for col, _ in schema_rows
    )
    null_counts_row = con.execute(f"SELECT {null_exprs} FROM {table}").fetchone() or []
    null_counts = {col: int(null_counts_row[i]) for i, (col, _) in enumerate(schema_rows)}

    columns: list[ColumnProfile] = [
        ColumnProfile(
            name=col_name,
            dtype=data_type,
            null_count=null_counts[col_name],
            non_null_count=row_count - null_counts[col_name],
        )
        for col_name, data_type in schema_rows
    ]

    return TableProfile(row_count=row_count, columns=columns)


def profile_to_dataframe(profile: TableProfile) -> pd.DataFrame:
    """Convert a TableProfile to a pandas DataFrame for display."""
    return pd.DataFrame(
        [
            {
                "Column": c.name,
                "Type": c.dtype,
                "Non-Null": c.non_null_count,
                "Null": c.null_count,
            }
            for c in profile.columns
        ]
    )


@dataclass
class ValidationReport:
    duplicate_row_count: int
    all_null_columns: list[str]   # null_count == row_count
    high_null_columns: list[str]  # null_count > 50 % of rows (excluding all-null)


def generate_profile_json(
    con: duckdb.DuckDBPyConnection,
    table: str = "data",
    sample_rows: int = 3,
) -> dict:
    """Return a profile dict with column names, dtypes, and a sample of *sample_rows* rows."""
    _validate_identifier(table)
    schema_rows = con.execute(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_name=? ORDER BY ordinal_position",
        [table],
    ).fetchall()
    sample_df = con.execute(f"SELECT * FROM {table} LIMIT {int(sample_rows)}").df()
    return {
        "columns": [{"name": col, "dtype": dtype} for col, dtype in schema_rows],
        "sample": sample_df.to_dict(orient="records"),
    }


def validate_table(
    con: duckdb.DuckDBPyConnection,
    profile: TableProfile,
    table: str = "data",
) -> ValidationReport:
    """Return a ValidationReport for *table*."""
    _validate_identifier(table)

    # Duplicate rows: total rows minus distinct rows
    distinct_count: int = con.execute(
        f"SELECT COUNT(*) FROM (SELECT DISTINCT * FROM {table})"
    ).fetchone()[0]  # type: ignore[index]
    dup_count = profile.row_count - distinct_count

    threshold = profile.row_count * HIGH_NULL_THRESHOLD if profile.row_count > 0 else 0
    all_null = [
        c.name
        for c in profile.columns
        if profile.row_count > 0 and c.null_count == profile.row_count
    ]
    high_null = [
        c.name
        for c in profile.columns
        if c.null_count > threshold and c.name not in all_null
    ]

    return ValidationReport(
        duplicate_row_count=dup_count,
        all_null_columns=all_null,
        high_null_columns=high_null,
    )
