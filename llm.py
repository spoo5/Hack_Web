"""LLM integration: cleaning handshake, NL-to-SQL, and answer formatting."""

import json
from typing import Any

import pandas as pd

# ── Prompt templates ──────────────────────────────────────────────────────────

_HANDSHAKE_PROMPT = (
    "You are a data cleaning expert. Here is the schema and a sample of a CSV dataset:\n\n"
    "{profile_json}\n\n"
    "List all specific data cleaning steps needed (e.g., date formatting, null handling, "
    "type casting, stripping unwanted characters). For every step also provide the DuckDB SQL "
    "statement (UPDATE or ALTER TABLE) that would apply the fix. "
    "Respond with ONLY a JSON object in this exact shape:\n"
    '{{ "steps": [ {{ "description": "...", "sql": "..." }}, ... ] }}'
)

_NL_TO_SQL_PROMPT = (
    "You are a DuckDB SQL expert. The table is named `data` and has this schema and sample:\n\n"
    "{profile_json}\n\n"
    "Convert the following question into a single DuckDB SQL SELECT (or WITH) query.\n"
    "Question: {question}\n\n"
    "Rules:\n"
    "- Return ONLY the SQL, no markdown fences, no explanation.\n"
    "- Use only SELECT or WITH statements.\n"
    "- For churn rate use: "
    "(COUNT(*) FILTER (WHERE <churned_col> = true) * 100.0 / NULLIF(COUNT(*), 0)) "
    "when the dataset has a churn column.\n"
)

_FORMAT_ANSWER_PROMPT = (
    "You are a senior data analyst. The user asked: \"{question}\"\n\n"
    "SQL query used:\n```sql\n{sql}\n```\n\n"
    "Query result (up to 50 rows):\n{result_json}\n\n"
    "Respond with ONLY a JSON object in this exact shape:\n"
    '{{\n'
    '  "answer": "<clear English answer with the key number/finding>",\n'
    '  "reasoning": "<one or two sentences explaining the logic>",\n'
    '  "confidence": <0-100 integer representing how confident you are given the data>,\n'
    '  "chart": {{\n'
    '    "type": "<bar|line|pie|none>",\n'
    '    "x": "<column name or empty string>",\n'
    '    "y": "<column name or empty string>"\n'
    '  }}\n'
    "}}"
)

_WEEKLY_REPORT_PROMPT = (
    "You are a business analyst. Here is the schema and sample of a dataset:\n\n"
    "{profile_json}\n\n"
    "Generate a concise weekly data report. Include:\n"
    "1. A summary of what kind of data this is.\n"
    "2. Key metrics to track (list up to 5, with the DuckDB SQL SELECT to compute each).\n"
    "3. Any data quality concerns.\n\n"
    "Respond with ONLY a JSON object:\n"
    '{{\n'
    '  "summary": "...",\n'
    '  "metrics": [ {{"name": "...", "sql": "...", "description": "..."}}, ... ],\n'
    '  "quality_notes": ["...", ...]\n'
    "}}"
)


# ── Public API ─────────────────────────────────────────────────────────────────

def get_client(api_key: str):
    """Create and return an OpenAI client."""
    from openai import OpenAI  # local import so the module loads without the package
    return OpenAI(api_key=api_key)


def llm_handshake(profile: dict, client, model: str = "gpt-4o-mini") -> list[dict]:
    """
    Send the profile JSON to the LLM and ask for cleaning steps.
    Returns a list of dicts, each with 'description' and 'sql' keys.
    """
    prompt = _HANDSHAKE_PROMPT.format(
        profile_json=json.dumps(profile, indent=2, default=str)
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    return json.loads(raw).get("steps", [])


def nl_to_sql(question: str, profile: dict, client, model: str = "gpt-4o-mini") -> str:
    """Convert a natural language question to a DuckDB SELECT query."""
    prompt = _NL_TO_SQL_PROMPT.format(
        profile_json=json.dumps(profile, indent=2, default=str),
        question=question,
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    sql = response.choices[0].message.content.strip()
    # Strip markdown code fences if the model wrapped the SQL
    if sql.startswith("```"):
        lines = sql.splitlines()
        sql = "\n".join(line for line in lines if not line.startswith("```")).strip()
    return sql


def format_answer(
    question: str,
    sql: str,
    result_df: pd.DataFrame,
    client,
    model: str = "gpt-4o-mini",
) -> dict[str, Any]:
    """
    Format the SQL result into a structured response.
    Returns a dict with 'answer', 'reasoning', 'confidence', and 'chart' keys.
    """
    result_json = result_df.head(50).to_json(orient="records", default_handler=str)
    prompt = _FORMAT_ANSWER_PROMPT.format(
        question=question,
        sql=sql,
        result_json=result_json,
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    return json.loads(raw)


def generate_weekly_report(profile: dict, client, model: str = "gpt-4o-mini") -> dict[str, Any]:
    """
    Ask the LLM to produce a structured weekly report template for the dataset.
    Returns a dict with 'summary', 'metrics', and 'quality_notes' keys.
    """
    prompt = _WEEKLY_REPORT_PROMPT.format(
        profile_json=json.dumps(profile, indent=2, default=str)
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    return json.loads(raw)
