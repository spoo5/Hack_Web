# Hack_Web — CSV Query UI

A lightweight **Streamlit + DuckDB** web app that lets you upload a CSV file,
inspect its schema and statistics, and run ad-hoc SQL queries — all in the browser.

## Features

- **Upload** any CSV file and have it ingested into an in-memory DuckDB table.
- **Schema inference** — DuckDB auto-detects column types.
- **Data profiling** — row count, column list, inferred types, null counts per column.
- **Data preview** — first 100 rows shown in an expandable panel.
- **SQL editor** — run any `SELECT` / `WITH` query against the `data` table.
- **Safety** — only read-only SQL (`SELECT`/`WITH`) is accepted; multi-statement
  queries are blocked.
- **Query metadata** — returned row count, columns used, execution time (ms).
- **Download** results as CSV.

## Project layout

```
app.py           # Streamlit entry-point
engine.py        # DuckDB ingestion & safe SQL execution
profiling.py     # Schema inference and data profiling helpers
requirements.txt # Python dependencies
```

## Run locally

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the app
streamlit run app.py
```

Then open the URL shown in the terminal (usually <http://localhost:8501>).

## Usage

1. Click **Browse files** and select a CSV.
2. Inspect the **Dataset Overview** panel (row count, column types, null counts).
3. Optionally expand **Data Preview** to see the first 100 rows.
4. Type a DuckDB SQL query in the text box (default: `SELECT * FROM data LIMIT 10`).
5. Click **▶ Run Query**.
6. Review results and metadata, then click **⬇ Download results as CSV** if needed.

## Notes

- The table name is always **`data`**.
- Only `SELECT` and `WITH` statements are allowed; any other SQL is rejected.
- Large files are supported — DuckDB reads the file directly; pandas is only used
  for display and export.
