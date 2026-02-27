"""Streamlit CSV Query UI backed by DuckDB."""

import tempfile
import os

import duckdb
import streamlit as st

from engine import (
    load_csv,
    run_query,
    run_cleaning_sql,
    build_filter_sql,
    build_agg_sql,
    FILTER_OPS,
    AGG_FUNCS,
    QueryResult,
)
from profiling import profile_table, profile_to_dataframe, validate_table, generate_profile_json
from llm import get_client, llm_handshake, nl_to_sql, format_answer, generate_weekly_report

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="CSV Query UI", page_icon="🦆", layout="wide")
st.title("🦆 CSV Query UI")
st.caption("Upload a CSV, explore its schema, run DuckDB SQL queries, and get AI-powered insights.")

# ── Sidebar — Mistral settings ──────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    mistral_api_key = st.text_input(
        "Mistral API Key",
        type="password",
        placeholder="your-mistral-api-key",
        help="Get your key from https://console.mistral.ai/api-keys",
    )
    llm_model = st.selectbox(
        "Model",
        ["mistral-large-latest", "mistral-small-latest", "open-mistral-nemo"],
        index=0,
    )

    st.divider()
    st.caption("Table name: **data**  |  Only SELECT/WITH queries are allowed in the SQL editor.")

# ── Session state ──────────────────────────────────────────────────────────────
if "con" not in st.session_state:
    st.session_state.con = duckdb.connect()
if "table_loaded" not in st.session_state:
    st.session_state.table_loaded = False
if "profile_json" not in st.session_state:
    st.session_state.profile_json = None
if "cleaning_steps" not in st.session_state:
    st.session_state.cleaning_steps = []

# Cache the Mistral client; recreate only when the key changes
_cached_key = st.session_state.get("mistral_api_key_cached", "")
if mistral_api_key and mistral_api_key != _cached_key:
    st.session_state.mistral_client = get_client(mistral_api_key)
    st.session_state.mistral_api_key_cached = mistral_api_key
_llm_client = st.session_state.get("mistral_client") if mistral_api_key else None

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

    st.dataframe(result.df, width="stretch")

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
    st.session_state.profile_json = None   # reset profile when a new file is loaded
    st.session_state.cleaning_steps = []
    if warnings:
        for w in warnings:
            st.warning(w)
    st.success(f"File **{uploaded.name}** loaded successfully.")

# ── Profile / Schema ───────────────────────────────────────────────────────────
if st.session_state.table_loaded:
    profile = profile_table(st.session_state.con)
    col_names_list = [c.name for c in profile.columns]
    col_type_map = {c.name: c.dtype for c in profile.columns}

    # Generate (or reuse) profile JSON for LLM features
    if st.session_state.profile_json is None:
        st.session_state.profile_json = generate_profile_json(st.session_state.con)

    st.subheader("📊 Dataset Overview")
    c1, c2 = st.columns(2)
    c1.metric("Rows", f"{profile.row_count:,}")
    c2.metric("Columns", len(profile.columns))

    with st.expander("Schema & Null Counts", expanded=True):
        st.dataframe(profile_to_dataframe(profile), width="stretch")

    with st.expander(f"Data Preview (first {PREVIEW_ROWS} rows)", expanded=False):
        preview_df = st.session_state.con.execute(
            f"SELECT * FROM data LIMIT {int(PREVIEW_ROWS)}"
        ).df()
        st.dataframe(preview_df, width="stretch")

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

    # ── AI Cleaning Suggestions (LLM Handshake) ────────────────────────────────
    st.divider()
    st.subheader("🤖 AI Cleaning Suggestions")
    if not mistral_api_key:
        st.info("Enter your Mistral API key in the sidebar to enable AI features.")
    else:
        if st.button("🔍 Analyse & Suggest Cleaning Steps"):
            with st.spinner("Sending schema to LLM…"):
                try:
                    _client = _llm_client
                    st.session_state.cleaning_steps = llm_handshake(
                        st.session_state.profile_json, _client, model=llm_model
                    )
                except Exception as exc:  # noqa: BLE001
                    st.error(f"LLM error: {exc}")

        if st.session_state.cleaning_steps:
            st.success(
                f"Found **{len(st.session_state.cleaning_steps)}** suggested cleaning step(s)."
            )
            for i, step in enumerate(st.session_state.cleaning_steps, 1):
                with st.expander(f"Step {i}: {step.get('description', '(no description)')}", expanded=True):
                    suggested_sql = step.get("sql", "")
                    edited_sql = st.text_area(
                        "SQL (editable)",
                        value=suggested_sql,
                        height=80,
                        key=f"clean_sql_{i}",
                    )
                    if st.button(f"▶ Apply Step {i}", key=f"apply_clean_{i}"):
                        err = run_cleaning_sql(edited_sql, st.session_state.con)
                        if err:
                            st.error(f"Error: {err}")
                        else:
                            # Verify schema is intact after cleaning
                            verify = st.session_state.con.execute(
                                "SELECT * FROM data LIMIT 0"
                            ).df()
                            # Refresh profile JSON after cleaning
                            st.session_state.profile_json = generate_profile_json(
                                st.session_state.con
                            )
                            st.success("✅ Cleaning step applied. Schema verified.")
                            st.caption(f"Columns after cleaning: {', '.join(verify.columns)}")

    # ── Natural Language Query ─────────────────────────────────────────────────
    st.divider()
    st.subheader("💬 Ask a Question About Your Data")
    if not mistral_api_key:
        st.info("Enter your Mistral API key in the sidebar to enable this feature.")
    else:
        nl_question = st.text_input(
            "Question",
            placeholder="e.g. What is the churn rate?  |  What was total revenue in March?",
            key="nl_question",
        )
        if st.button("▶ Get Answer", key="nl_run"):
            if not nl_question.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Translating question to SQL…"):
                    try:
                        _client = _llm_client
                        generated_sql = nl_to_sql(
                            nl_question,
                            st.session_state.profile_json,
                            _client,
                            model=llm_model,
                        )
                    except Exception as exc:  # noqa: BLE001
                        st.error(f"LLM error: {exc}")
                        generated_sql = ""

                if generated_sql:
                    with st.expander("Generated SQL", expanded=True):
                        st.code(generated_sql, language="sql")

                    with st.spinner("Executing query…"):
                        nl_result = run_query(generated_sql, st.session_state.con)

                    if nl_result.error:
                        st.error(nl_result.error)
                    else:
                        with st.spinner("Formatting answer…"):
                            try:
                                _client = _llm_client
                                answer = format_answer(
                                    nl_question,
                                    generated_sql,
                                    nl_result.df,
                                    _client,
                                    model=llm_model,
                                )
                            except Exception as exc:  # noqa: BLE001
                                st.error(f"LLM error: {exc}")
                                answer = {}

                        if answer:
                            st.markdown(f"### 📝 Answer\n{answer.get('answer', '')}")
                            st.caption(f"**Reasoning:** {answer.get('reasoning', '')}")
                            confidence = answer.get("confidence")
                            if confidence is not None:
                                st.metric("Confidence", f"{confidence}%")

                            # Raw result table
                            with st.expander("Raw query result", expanded=False):
                                st.dataframe(nl_result.df, width="stretch")

                            # Render chart if suggested
                            chart_info = answer.get("chart", {})
                            chart_type = chart_info.get("type", "none")
                            x_col = chart_info.get("x", "")
                            y_col = chart_info.get("y", "")
                            if (
                                chart_type != "none"
                                and x_col in nl_result.df.columns
                                and y_col in nl_result.df.columns
                            ):
                                chart_df = nl_result.df.set_index(x_col)[[y_col]]
                                st.subheader(f"📊 Chart ({chart_type})")
                                if chart_type == "line":
                                    st.line_chart(chart_df)
                                elif chart_type == "bar":
                                    st.bar_chart(chart_df)
                                elif chart_type == "area":
                                    st.area_chart(chart_df)
                                else:
                                    st.bar_chart(chart_df)

    # ── Weekly Report ──────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📅 Generate Weekly Report")
    if not mistral_api_key:
        st.info("Enter your Mistral API key in the sidebar to enable this feature.")
    else:
        if st.button("📋 Generate Weekly Report Template"):
            with st.spinner("Generating report template…"):
                try:
                    _client = _llm_client
                    report = generate_weekly_report(
                        st.session_state.profile_json, _client, model=llm_model
                    )
                except Exception as exc:  # noqa: BLE001
                    st.error(f"LLM error: {exc}")
                    report = {}

            if report:
                st.markdown(f"**Dataset Summary:** {report.get('summary', '')}")
                metrics = report.get("metrics", [])
                if metrics:
                    st.markdown("#### Key Metrics")
                    for m in metrics:
                        with st.expander(f"📌 {m.get('name', 'Metric')}", expanded=False):
                            st.caption(m.get("description", ""))
                            st.code(m.get("sql", ""), language="sql")
                            if st.button(f"▶ Run: {m.get('name', '')}", key=f"rpt_{m.get('name','')}"):
                                with st.spinner("Running…"):
                                    rpt_result = run_query(m.get("sql", ""), st.session_state.con)
                                _show_result(rpt_result)

                notes = report.get("quality_notes", [])
                if notes:
                    st.markdown("#### ⚠️ Data Quality Notes")
                    for note in notes:
                        st.warning(note)

