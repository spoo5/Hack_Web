"""Streamlit CSV Query UI backed by DuckDB."""

import io
import tempfile
import os

import duckdb
import streamlit as st

from engine import load_csv, run_query
from profiling import profile_table, profile_to_dataframe

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="CSV Query UI", page_icon="🦆", layout="wide")
st.title("🦆 CSV Query UI")
st.caption("Upload a CSV, explore its schema, and run DuckDB SQL queries.")

# ── Session state ──────────────────────────────────────────────────────────────
if "con" not in st.session_state:
    st.session_state.con = duckdb.connect()
if "table_loaded" not in st.session_state:
    st.session_state.table_loaded = False

PREVIEW_ROWS = 100  # configurable default for the preview section

# ── Upload ─────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded is not None:
    # Write to a temp file so DuckDB can read it directly (avoids full pandas load)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(uploaded.getvalue())
        tmp_path = tmp.name

    with st.spinner("Ingesting CSV into DuckDB…"):
        warnings = load_csv(tmp_path, st.session_state.con)
    os.unlink(tmp_path)

    st.session_state.table_loaded = True
    if warnings:
        for w in warnings:
            st.warning(w)
    st.success(f"File **{uploaded.name}** loaded successfully.")

# ── Profile / Schema ───────────────────────────────────────────────────────────
if st.session_state.table_loaded:
    profile = profile_table(st.session_state.con)

    st.subheader("📊 Dataset Overview")
    col1, col2 = st.columns(2)
    col1.metric("Rows", f"{profile.row_count:,}")
    col2.metric("Columns", len(profile.columns))

    with st.expander("Schema & Null Counts", expanded=True):
        st.dataframe(profile_to_dataframe(profile), use_container_width=True)

    with st.expander(f"Data Preview (first {PREVIEW_ROWS} rows)", expanded=False):
        preview_df = st.session_state.con.execute(
            f"SELECT * FROM data LIMIT {int(PREVIEW_ROWS)}"
        ).df()
        st.dataframe(preview_df, use_container_width=True)

    # ── Query ──────────────────────────────────────────────────────────────────
    st.subheader("🔍 Run SQL Query")
    col_names = ", ".join(f"`{c.name}`" for c in profile.columns)
    st.caption(f"Available columns: {col_names}")

    default_sql = "SELECT * FROM data LIMIT 10"
    sql = st.text_area("DuckDB SQL (SELECT / WITH only)", value=default_sql, height=120)

    if st.button("▶ Run Query"):
        with st.spinner("Executing…"):
            result = run_query(sql, st.session_state.con)

        st.subheader("Query Metadata")
        meta_cols = st.columns(3)
        meta_cols[0].metric("Rows returned", result.row_count)
        meta_cols[1].metric("Execution time", f"{result.execution_time_ms:.1f} ms")
        meta_cols[2].metric("Columns", len(result.columns))

        if result.error:
            st.error(result.error)
        else:
            if result.warnings:
                for w in result.warnings:
                    st.warning(w)

            if result.columns:
                st.caption(f"Result columns: {', '.join(result.columns)}")

            st.subheader("Query Results")
            st.dataframe(result.df, use_container_width=True)

            # Download button
            csv_bytes = result.df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇ Download results as CSV",
                data=csv_bytes,
                file_name="query_results.csv",
                mime="text/csv",
            )
