# Hack_Web — AI-Powered CSV Query UI

A **Streamlit + DuckDB + Google Gemini** web app that lets you upload any CSV,
automatically clean it with AI suggestions, ask plain-English questions about
your data, and generate automated weekly reports — all in the browser.

## Features

| Feature | Description |
|---|---|
| **CSV Upload** | Ingest any CSV into an in-memory DuckDB table with auto-detected types |
| **Data Profiling** | Row count, column types, null counts, duplicate detection |
| **Data Preview** | First 100 rows in an expandable panel |
| **Data Validation** | Flags all-null columns, high-null columns (>50 %), duplicate rows |
| **Filter & Aggregate** | Point-and-click filter and aggregation builder |
| **SQL Editor** | Run any `SELECT` / `WITH` query against the `data` table |
| **🤖 AI Cleaning** | Gemini analyses your schema and suggests DuckDB SQL cleaning steps |
| **💬 Ask a Question** | Type a plain-English question → Gemini generates SQL → shows answer + chart |
| **📅 Weekly Report** | Gemini generates a report template with runnable metric queries |

---

## Project layout

```
app.py           # Streamlit entry-point
engine.py        # DuckDB ingestion, safe SQL execution, cleaning SQL runner
profiling.py     # Schema inference, data profiling, and profile-JSON helper
llm.py           # Google Gemini client, cleaning handshake, NL→SQL, answer formatting
requirements.txt # Python dependencies
```

---

## How to add your Gemini API key

1. Go to **[Google AI Studio](https://aistudio.google.com/app/apikey)** and sign in with your Google account.
2. Click **Create API key** → copy the key (it starts with `AIza…`).
3. When the app is running, paste it into the **"Gemini API Key"** field in the left sidebar.

> The key is only held in your browser session — it is never stored on disk or sent anywhere other than the Gemini API.

---

## Run in VS Code (recommended)

### Prerequisites
- [VS Code](https://code.visualstudio.com/download) installed
- [Python 3.10+](https://www.python.org/downloads/) installed and on your PATH
- The **[Python extension for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-python.python)** installed

### Step-by-step

**1. Open the project folder in VS Code**

```
File → Open Folder… → select the Hack_Web folder
```

Or from a terminal:

```bash
code path/to/Hack_Web
```

**2. Open the integrated terminal**

```
Terminal → New Terminal   (or  Ctrl+` )
```

**3. Create a virtual environment**

```bash
python -m venv .venv
```

**4. Activate the virtual environment**

| OS | Command |
|---|---|
| macOS / Linux | `source .venv/bin/activate` |
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Windows (CMD) | `.venv\Scripts\activate.bat` |

VS Code will detect the new `.venv` and ask *"Do you want to select this environment?"* — click **Yes**.

**5. Install dependencies**

```bash
pip install -r requirements.txt
```

**6. Run the app**

```bash
streamlit run app.py
```

VS Code's terminal will print a local URL — hold **Ctrl** (or **Cmd** on Mac) and click it, or open your browser and go to <http://localhost:8501>.

---

> **Tip — stop the app:** press `Ctrl+C` in the terminal.  
> **Tip — re-run after changes:** Streamlit hot-reloads automatically whenever you save a file.

---

## Run locally (plain terminal, no VS Code)

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

---

## Usage guide

### 1 — Upload a CSV
Click **Browse files** and select any CSV file.  
The file is loaded into DuckDB; the **Dataset Overview** panel shows row/column counts
and the schema with null-count stats.

### 2 — Explore & validate
- Expand **Data Preview** to see the first 100 rows.
- Expand **🔎 Data Validation** to see duplicate rows, all-null columns, and
  high-null columns flagged automatically.

### 3 — Filter and aggregate (no SQL needed)
- Use **🔽 Filter Data** to pick a column, operator, and value, then click **▶ Apply Filter**.
- Use **📈 Aggregate Data** to group by columns and apply COUNT / SUM / AVG / MIN / MAX.

### 4 — Run your own SQL
Type any DuckDB `SELECT` or `WITH` query in the **🔍 Run SQL Query** box.  
The table name is always **`data`**.

### 5 — AI Cleaning Suggestions (requires Gemini key)
1. Paste your Gemini API key in the sidebar and pick a model.
2. Click **🔍 Analyse & Suggest Cleaning Steps**.
3. Gemini inspects the schema and sample rows, then lists cleaning steps with
   ready-made DuckDB SQL (e.g. strip `$` from price columns, cast types, fill nulls).
4. Each step is shown in an editable text box — tweak if needed, then click **▶ Apply Step N**.
5. The schema is verified after every step and the profile is refreshed automatically.

### 6 — Ask a question in plain English (requires Gemini key)
1. Type your question in the **💬 Ask a Question About Your Data** box, e.g.:
   - *"What is the churn rate?"*
   - *"What was the total revenue in March?"*
   - *"Which product had the highest average order value?"*
2. Click **▶ Get Answer**.
3. The app returns:
   - **📝 A clear English answer** with the key number/finding
   - **The exact SQL query** used to produce it
   - **Reasoning** — a short explanation of the logic
   - **Confidence %** — how confident Gemini is given the available data
   - **📊 A chart** (bar, line, or area) when the result has plottable columns

**Churn rate example** — if your dataset has a boolean `churned` column the
generated SQL will be:
```sql
SELECT
  COUNT(*) FILTER (WHERE churned = true) * 100.0 / NULLIF(COUNT(*), 0)
    AS churn_rate_pct
FROM data;
```

### 7 — Generate a Weekly Report (requires Gemini key)
Click **📋 Generate Weekly Report Template**.  
Gemini returns:
- A **summary** of what kind of dataset this is.
- Up to **5 key metric queries** (each with a **▶ Run** button to execute live).
- **Data quality notes** for anything suspicious in the schema.

---

## Notes

- The DuckDB table name is always **`data`**.
- Only `SELECT` and `WITH` are allowed in the SQL editor; everything else is rejected.
- AI cleaning steps are limited to `UPDATE` and `ALTER TABLE` on the `data` table only.
- Large files are fine — DuckDB reads the file natively; pandas is only used for display.
- The Gemini client is cached in the Streamlit session and only re-created when you
  change the API key.
