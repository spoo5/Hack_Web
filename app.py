"""Streamlit CSV Query UI backed by DuckDB."""

import tempfile
import os

import duckdb
import streamlit as st

from engine import (
    load_csv,
    run_query,
    build_filter_sql,
    build_agg_sql,
    FILTER_OPS,
    AGG_FUNCS,
    QueryResult,
)
from profiling import profile_table, profile_to_dataframe, validate_table

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


# ── Shared result display ──────────────────────────────────────────────────────
def _show_result(result: QueryResult, download_name: str = "query_results.csv") -> None:
    """Render query metadata, result table, and download button."""
    meta_cols = st.columns(3)
    meta_cols[0].metric("Rows returned", result.row_count)
    meta_cols[1].metric("Execution time", f"{result.execution_time_ms:.1f} ms")
    meta_cols[2].metric("Columns", len(result.columns))

    if result.error:
        st.error(result.error)
        return

    if result.warnings:
        for w in result.warnings:
            st.warning(w)

    if result.columns:
        st.caption(f"Result columns: {', '.join(result.columns)}")

    st.dataframe(result.df, use_container_width=True)

    csv_bytes = result.df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇ Download results as CSV",
        data=csv_bytes,
        file_name=download_name,
        mime="text/csv",
    )


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
    col_names_list = [c.name for c in profile.columns]
    col_type_map = {c.name: c.dtype for c in profile.columns}

    st.subheader("📊 Dataset Overview")
    c1, c2 = st.columns(2)
    c1.metric("Rows", f"{profile.row_count:,}")
    c2.metric("Columns", len(profile.columns))

    with st.expander("Schema & Null Counts", expanded=True):
        st.dataframe(profile_to_dataframe(profile), use_container_width=True)

    with st.expander(f"Data Preview (first {PREVIEW_ROWS} rows)", expanded=False):
        preview_df = st.session_state.con.execute(
            f"SELECT * FROM data LIMIT {int(PREVIEW_ROWS)}"
        ).df()
        st.dataframe(preview_df, use_container_width=True)

    # ── Data Validation ────────────────────────────────────────────────────────
    with st.expander("🔎 Data Validation", expanded=False):
        with st.spinner("Validating…"):
            vreport = validate_table(st.session_state.con, profile)

        v1, v2, v3 = st.columns(3)
        v1.metric("Duplicate rows", vreport.duplicate_row_count)
        v2.metric("All-null columns", len(vreport.all_null_columns))
        v3.metric("High-null columns (>50 %)", len(vreport.high_null_columns))

        if vreport.duplicate_row_count > 0:
            st.warning(f"⚠ {vreport.duplicate_row_count} duplicate row(s) detected.")
        if vreport.all_null_columns:
            st.error(f"Columns with **all nulls**: {', '.join(vreport.all_null_columns)}")
        if vreport.high_null_columns:
            st.warning(
                f"Columns with **>50 % nulls**: {', '.join(vreport.high_null_columns)}"
            )
        if (
            vreport.duplicate_row_count == 0
            and not vreport.all_null_columns
            and not vreport.high_null_columns
        ):
            st.success("✅ No validation issues found.")

    # ── Filter Data ────────────────────────────────────────────────────────────
    st.subheader("🔽 Filter Data")
    fc1, fc2, fc3 = st.columns([2, 2, 3])
    filter_col = fc1.selectbox("Column", col_names_list, key="filter_col")
    filter_op = fc2.selectbox("Operator", FILTER_OPS, key="filter_op")
    filter_val = ""
    if filter_op not in {"IS NULL", "IS NOT NULL"}:
        filter_val = fc3.text_input("Value", key="filter_val")

    if st.button("▶ Apply Filter"):
        fsql, ferr = build_filter_sql(
            filter_col,
            filter_op,
            filter_val,
            col_names_list,
            col_type_map.get(filter_col, ""),
        )
        if ferr:
            st.error(ferr)
        else:
            with st.spinner("Filtering…"):
                fresult = run_query(fsql, st.session_state.con)
            st.subheader("Filter Results")
            _show_result(fresult, download_name="filtered_results.csv")

    # ── Aggregate Data ─────────────────────────────────────────────────────────
    st.subheader("📈 Aggregate Data")
    ag1, ag2, ag3 = st.columns([3, 2, 2])
    group_cols = ag1.multiselect(
        "Group By (optional)", col_names_list, key="group_cols"
    )
    agg_func = ag2.selectbox("Function", AGG_FUNCS, key="agg_func")
    # COUNT(*) does not need a target column; disable selector in that case
    agg_col = ag3.selectbox(
        "Aggregate Column",
        col_names_list,
        key="agg_col",
        disabled=(agg_func == "COUNT"),
    ) if col_names_list else None

    if st.button("▶ Run Aggregation"):
        asql, aerr = build_agg_sql(
            group_cols,
            agg_col or "",
            agg_func,
            col_names_list,
        )
        if aerr:
            st.error(aerr)
        else:
            with st.spinner("Aggregating…"):
                aresult = run_query(asql, st.session_state.con)
            st.subheader("Aggregation Results")
            _show_result(aresult, download_name="aggregation_results.csv")

    # ── SQL Query ──────────────────────────────────────────────────────────────
    st.subheader("🔍 Run SQL Query")
    col_names_display = ", ".join(f"`{c}`" for c in col_names_list)
    st.caption(f"Available columns: {col_names_display}")

    default_sql = "SELECT * FROM data LIMIT 10"
    sql = st.text_area("DuckDB SQL (SELECT / WITH only)", value=default_sql, height=120)

    if st.button("▶ Run Query"):
        with st.spinner("Executing…"):
            result = run_query(sql, st.session_state.con)
        st.subheader("Query Results")
        _show_result(result)

