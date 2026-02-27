"""Data profiling utilities using DuckDB."""

import re
from dataclasses import dataclass

import duckdb
import pandas as pd

_SAFE_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


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
