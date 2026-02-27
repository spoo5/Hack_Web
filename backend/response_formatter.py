"""
Response Formatter Module
Formats analytics results into structured 4-section output:
1. Natural Language Answer
2. SQL/Query Logic
3. Derivation Explanation
4. Visualization Data

When the analytics engine returns a DuckDB result (type == 'duckdb_result'),
the LLM's format_answer() is tried first for richer natural-language output.
"""

import os
from typing import Dict, Any, List

# LLM-enhanced formatting (optional – falls back gracefully)
try:
    from llm import get_client, format_answer as _format_answer

    _api_key = os.environ.get("MISTRAL_API_KEY", "")
    _llm_client = get_client(_api_key) if _api_key else None
    _llm_model = os.environ.get("MISTRAL_MODEL", "mistral-large-latest")
except Exception:
    _llm_client = None
    _llm_model = "mistral-large-latest"


class ResponseFormatter:
    """Formats raw analytics results into user-friendly structured responses"""
    
    def format(self, result: Dict[str, Any], parsed_query: Dict[str, Any], total_rows: int) -> Dict[str, Any]:
        """
        Format analytics result into structured response - FULLY DYNAMIC
        
        Returns structured response with:
        - answer: Natural language answer
        - sql_logic: SQL-style query representation
        - derivation: How answer was derived
        - visualization_type: Chart type
        - chart_data: Data for visualization
        - row_count: Total rows in dataset
        - confidence_score: Confidence percentage
        - grounding_info: Data grounding statement
        """
        result_type = result.get("type", "unknown")

        # DuckDB result path – try LLM formatting, fall back to generic
        if result_type == "duckdb_result":
            return self._format_duckdb_result(result, parsed_query, total_rows)
        
        # Route to appropriate formatter - ALL GENERIC
        if result_type == "binary_rate_analysis":
            return self._format_binary_rate(result, parsed_query, total_rows)
        
        elif result_type == "simple_binary_rate":
            return self._format_simple_binary_rate(result, parsed_query, total_rows)
        
        elif result_type == "percentage_distribution":
            return self._format_percentage_distribution(result, parsed_query, total_rows)
        
        elif result_type == "grouped_count":
            return self._format_grouped_count(result, parsed_query, total_rows)
        
        elif result_type == "grouped_average":
            return self._format_grouped_average(result, parsed_query, total_rows)
        
        elif result_type == "grouped_sum":
            return self._format_grouped_sum(result, parsed_query, total_rows)
        
        elif result_type == "simple_count":
            return self._format_simple_count(result, parsed_query, total_rows)
        
        elif result_type == "simple_average":
            return self._format_simple_average(result, parsed_query, total_rows)
        
        elif result_type == "count_comparison" or result_type == "numeric_comparison":
            return self._format_comparison(result, parsed_query, total_rows)
        
        elif result_type == "error":
            return {
                "answer": f"❌ **Error:** {result.get('message', 'Unknown error occurred')}",
                "sql_logic": "-- Error occurred during query execution",
                "derivation": {"error": result.get('message')},
                "visualization_type": "none",
                "chart_data": {},
                "row_count": total_rows,
                "confidence_score": 0.0,
                "grounding_info": "No data processed due to error."
            }
        
        else:
            return self._format_generic(result, parsed_query, total_rows)

    # ------------------------------------------------------------------
    # DuckDB result formatter
    # ------------------------------------------------------------------
    def _format_duckdb_result(
        self, result: Dict, parsed_query: Dict, total_rows: int
    ) -> Dict[str, Any]:
        """Format a DuckDB query result, using LLM if available."""
        sql = result.get("sql", "")
        result_df = result.get("df")
        question = parsed_query.get("original_query", "")
        rows = result.get("rows", [])
        columns = result.get("columns", [])

        # Try LLM-enhanced formatting
        if _llm_client is not None and result_df is not None:
            try:
                llm_fmt = _format_answer(question, sql, result_df, _llm_client, model=_llm_model)
                chart = llm_fmt.get("chart", {})
                chart_type = chart.get("type", "none")
                x_col = chart.get("x", "")
                y_col = chart.get("y", "")

                # Build chart_data from result rows if columns are present
                chart_data: Dict[str, Any] = {}
                if chart_type != "none" and x_col and y_col and rows:
                    chart_data = {
                        "labels": [str(r.get(x_col, "")) for r in rows],
                        "datasets": [{
                            "label": y_col,
                            "data": [r.get(y_col) for r in rows],
                            "backgroundColor": self._generate_colors(len(rows)),
                        }]
                    }

                return {
                    "answer": llm_fmt.get("answer", "Analysis complete."),
                    "sql_logic": sql,
                    "derivation": {
                        "rows_analyzed": total_rows,
                        "columns_used": columns,
                        "reasoning": llm_fmt.get("reasoning", ""),
                        "calculation_steps": [llm_fmt.get("reasoning", "")] if llm_fmt.get("reasoning") else [],
                    },
                    "visualization_type": chart_type,
                    "chart_data": chart_data,
                    "row_count": total_rows,
                    "confidence_score": float(llm_fmt.get("confidence", 85)),
                    "grounding_info": (
                        f"Computed by DuckDB from {total_rows} rows. "
                        "All numbers are deterministic."
                    ),
                }
            except Exception:
                pass  # Fall through to generic formatting

        # Generic formatting for DuckDB results (no LLM)
        answer_lines = [f"Query returned {len(rows)} row(s)."]
        if rows:
            for row in rows[:5]:
                answer_lines.append("  " + ", ".join(f"{k}: {v}" for k, v in row.items()))

        # Attempt simple chart if 2 columns
        chart_data = {}
        vis_type = "none"
        if len(columns) == 2 and rows:
            x_col, y_col = columns[0], columns[1]
            vis_type = "bar"
            chart_data = {
                "labels": [str(r.get(x_col, "")) for r in rows],
                "datasets": [{
                    "label": y_col,
                    "data": [r.get(y_col) for r in rows],
                    "backgroundColor": self._generate_colors(len(rows)),
                }]
            }

        return {
            "answer": "\n".join(answer_lines),
            "sql_logic": sql,
            "derivation": {
                "rows_analyzed": total_rows,
                "columns_used": columns,
                "result_rows": len(rows),
            },
            "visualization_type": vis_type,
            "chart_data": chart_data,
            "row_count": total_rows,
            "confidence_score": 85.0,
            "grounding_info": (
                f"Computed by DuckDB from {total_rows} rows. "
                "All numbers are deterministic."
            ),
        }


    def _format_binary_rate(self, result: Dict, parsed: Dict, total_rows: int) -> Dict[str, Any]:
        """
        Format binary rate analysis with grouping - FULLY GENERIC
        Works for ANY binary column (churn, conversion, success, active, etc.)
        """
        target_col = result.get("target_column")
        positive_value = result.get("positive_value")
        groupby = result.get("groupby")
        results = result.get("results", [])
        overall = result.get("overall", {})
        
        # 1. Natural Language Answer
        answer_parts = [f"**{target_col} Rate Analysis by {groupby}:**\n"]
        for item in results:
            group_name = item.get(groupby)
            rate = item.get("rate")
            answer_parts.append(f"• {group_name}: {rate}% ({item.get('positive_count')}/{item.get('total')})")
        
        answer_parts.append(f"\n**Overall {target_col} rate: {overall.get('rate')}%**")
        answer = "\n".join(answer_parts)
        
        # 2. SQL Logic
        sql_logic = f"""SELECT {groupby},
       COUNT(*) as total,
       SUM(CASE WHEN {target_col} = '{positive_value}' THEN 1 ELSE 0 END) as positive_count,
       ROUND(SUM(CASE WHEN {target_col} = '{positive_value}' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as rate
FROM dataset
GROUP BY {groupby}"""
        
        # 3. Derivation
        derivation = {
            "rows_analyzed": overall.get("total"),
            "columns_used": [target_col, groupby],
            "formula": f"rate = (count_where_{target_col}='{positive_value}' ÷ total_count) × 100",
            "calculations": [
                {
                    "group": item.get(groupby),
                    "calculation": item.get("formula"),
                    "result": f"{item.get('rate')}%"
                }
                for item in results
            ],
            "filters_applied": parsed.get("filter_conditions", [])
        }
        
        # 4. Visualization - Dynamic colors
        chart_data = {
            "labels": [str(item.get(groupby)) for item in results],
            "datasets": [
                {
                    "label": f"{target_col} Rate (%)",
                    "data": [item.get("rate") for item in results],
                    "backgroundColor": self._generate_colors(len(results))
                }
            ]
        }
        
        # Confidence Score
        confidence = self._calculate_confidence(result, parsed, total_rows)
        
        # Grounding Info
        grounding = f"This answer is derived strictly from {overall.get('total')} rows in your uploaded dataset. No external data used."
        
        return {
            "answer": answer,
            "sql_logic": sql_logic,
            "derivation": derivation,
            "visualization_type": "bar",
            "chart_data": chart_data,
            "row_count": total_rows,
            "confidence_score": confidence,
            "grounding_info": grounding
        }
    
    def _format_simple_binary_rate(self, result: Dict, parsed: Dict, total_rows: int) -> Dict[str, Any]:
        """Format simple binary rate - GENERIC"""
        target_col = result.get("target_column")
        positive_value = result.get("positive_value")
        total = result.get("total")
        positive_count = result.get("positive_count")
        rate = result.get("rate")
        formula = result.get("formula")
        
        answer = f"**Overall {target_col} Rate: {rate}%**\n\n{positive_count} out of {total} records have {target_col} = {positive_value}."
        
        sql_logic = f"""SELECT 
       COUNT(*) as total,
       SUM(CASE WHEN {target_col} = '{positive_value}' THEN 1 ELSE 0 END) as positive_count,
       ROUND(SUM(CASE WHEN {target_col} = '{positive_value}' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as rate
FROM dataset"""
        
        derivation = {
            "rows_analyzed": total,
            "columns_used": [target_col],
            "formula": formula,
            "calculation_steps": [
                f"Total records: {total}",
                f"Records with {target_col}='{positive_value}': {positive_count}",
                f"Rate: {formula} = {rate}%"
            ]
        }
        
        # Pie chart showing split
        chart_data = {
            "labels": [positive_value, f"Not {positive_value}"],
            "datasets": [{
                "data": [positive_count, total - positive_count],
                "backgroundColor": ["#EAAB00", "#4ECDC4"]
            }]
        }
        
        return {
            "answer": answer,
            "sql_logic": sql_logic,
            "derivation": derivation,
            "visualization_type": "doughnut",
            "chart_data": chart_data,
            "row_count": total_rows,
            "confidence_score": self._calculate_confidence(result, parsed, total_rows),
            "grounding_info": f"Derived from {total} rows in your dataset."
        }
    
    def _generate_colors(self, count: int) -> List[str]:
        """Generate color palette for visualizations"""
        base_colors = ["#EAAB00", "#FFC94D", "#FFD700", "#FFED4E", "#4ECDC4", "#FF6B6B", "#95E1D3", "#F38181"]
        return base_colors[:count] if count <= len(base_colors) else base_colors * ((count // len(base_colors)) + 1)
    
    def _format_percentage_distribution(self, result: Dict, parsed: Dict, total_rows: int) -> Dict[str, Any]:
        """Format percentage distribution"""
        groupby = result.get("groupby")
        results = result.get("results", [])
        total = result.get("total")
        
        answer_parts = [f"**Distribution by {groupby}:**\n"]
        for item in results:
            answer_parts.append(f"• {item.get(groupby)}: {item.get('percentage')}% ({item.get('count')} records)")
        answer = "\n".join(answer_parts)
        
        sql_logic = f"""SELECT {groupby},
       COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dataset), 2) as percentage
FROM dataset
GROUP BY {groupby}"""
        
        derivation = {
            "rows_analyzed": total,
            "columns_used": [groupby],
            "formula": "percentage = (group_count ÷ total_count) × 100",
            "breakdown": results
        }
        
        chart_data = {
            "labels": [str(item.get(groupby)) for item in results],
            "datasets": [{
                "data": [item.get("percentage") for item in results],
                "backgroundColor": ["#EAAB00", "#FFC94D", "#FFD700", "#FFED4E"]
            }]
        }
        
        return {
            "answer": answer,
            "sql_logic": sql_logic,
            "derivation": derivation,
            "visualization_type": "pie",
            "chart_data": chart_data,
            "row_count": total_rows,
            "confidence_score": self._calculate_confidence(result, parsed, total_rows),
            "grounding_info": f"Calculated from {total} rows."
        }
    
    def _format_grouped_count(self, result: Dict, parsed: Dict, total_rows: int) -> Dict[str, Any]:
        """Format grouped count"""
        groupby = result.get("groupby")
        results = result.get("results", [])
        total = result.get("total")
        
        answer_parts = [f"**Count by {groupby}:**\n"]
        for item in results:
            answer_parts.append(f"• {item.get(groupby)}: {item.get('count')} records")
        answer = "\n".join(answer_parts)
        
        sql_logic = f"""SELECT {groupby}, COUNT(*) as count
FROM dataset
GROUP BY {groupby}"""
        
        derivation = {
            "rows_analyzed": total,
            "columns_used": [groupby],
            "operation": "COUNT with GROUP BY",
            "results": results
        }
        
        chart_data = {
            "labels": [str(item.get(groupby)) for item in results],
            "datasets": [{
                "label": "Count",
                "data": [item.get("count") for item in results],
                "backgroundColor": "#EAAB00"
            }]
        }
        
        return {
            "answer": answer,
            "sql_logic": sql_logic,
            "derivation": derivation,
            "visualization_type": "bar",
            "chart_data": chart_data,
            "row_count": total_rows,
            "confidence_score": self._calculate_confidence(result, parsed, total_rows),
            "grounding_info": f"Computed from {total} rows."
        }
    
    def _format_grouped_average(self, result: Dict, parsed: Dict, total_rows: int) -> Dict[str, Any]:
        """Format grouped average"""
        column = result.get("column")
        groupby = result.get("groupby")
        results = result.get("results", [])
        
        answer_parts = [f"**Average {column} by {groupby}:**\n"]
        for item in results:
            answer_parts.append(f"• {item.get(groupby)}: {round(item.get('average'), 2)}")
        answer = "\n".join(answer_parts)
        
        sql_logic = f"""SELECT {groupby}, AVG({column}) as average
FROM dataset
GROUP BY {groupby}"""
        
        derivation = {
            "rows_analyzed": total_rows,
            "columns_used": [column, groupby],
            "operation": "AVG with GROUP BY",
            "results": results
        }
        
        chart_data = {
            "labels": [str(item.get(groupby)) for item in results],
            "datasets": [{
                "label": f"Average {column}",
                "data": [item.get("average") for item in results],
                "backgroundColor": "#EAAB00"
            }]
        }
        
        return {
            "answer": answer,
            "sql_logic": sql_logic,
            "derivation": derivation,
            "visualization_type": "bar",
            "chart_data": chart_data,
            "row_count": total_rows,
            "confidence_score": self._calculate_confidence(result, parsed, total_rows),
            "grounding_info": f"Calculated from {total_rows} rows."
        }
    
    def _format_grouped_sum(self, result: Dict, parsed: Dict, total_rows: int) -> Dict[str, Any]:
        """Format grouped sum"""
        column = result.get("column")
        groupby = result.get("groupby")
        results = result.get("results", [])
        
        answer_parts = [f"**Total {column} by {groupby}:**\n"]
        for item in results:
            answer_parts.append(f"• {item.get(groupby)}: {round(item.get('sum'), 2)}")
        answer = "\n".join(answer_parts)
        
        sql_logic = f"""SELECT {groupby}, SUM({column}) as total
FROM dataset
GROUP BY {groupby}"""
        
        derivation = {
            "rows_analyzed": total_rows,
            "columns_used": [column, groupby],
            "operation": "SUM with GROUP BY",
            "results": results
        }
        
        chart_data = {
            "labels": [str(item.get(groupby)) for item in results],
            "datasets": [{
                "label": f"Total {column}",
                "data": [item.get("sum") for item in results],
                "backgroundColor": "#EAAB00"
            }]
        }
        
        return {
            "answer": answer,
            "sql_logic": sql_logic,
            "derivation": derivation,
            "visualization_type": "bar",
            "chart_data": chart_data,
            "row_count": total_rows,
            "confidence_score": self._calculate_confidence(result, parsed, total_rows),
            "grounding_info": f"Summed from {total_rows} rows."
        }
    
    def _format_simple_count(self, result: Dict, parsed: Dict, total_rows: int) -> Dict[str, Any]:
        """Format simple count"""
        count = result.get("count")
        
        return {
            "answer": f"**Total Records: {count}**",
            "sql_logic": "SELECT COUNT(*) FROM dataset",
            "derivation": {
                "rows_analyzed": count,
                "operation": "COUNT(*)",
                "result": count
            },
            "visualization_type": "kpi",
            "chart_data": {"value": count},
            "row_count": total_rows,
            "confidence_score": 100.0,
            "grounding_info": f"Total count from dataset."
        }
    
    def _format_simple_average(self, result: Dict, parsed: Dict, total_rows: int) -> Dict[str, Any]:
        """Format simple average"""
        column = result.get("column")
        average = result.get("average")
        
        return {
            "answer": f"**Average {column}: {round(average, 2)}**",
            "sql_logic": f"SELECT AVG({column}) FROM dataset",
            "derivation": {
                "rows_analyzed": total_rows,
                "column": column,
                "operation": "AVG",
                "result": round(average, 2)
            },
            "visualization_type": "kpi",
            "chart_data": {"value": round(average, 2)},
            "row_count": total_rows,
            "confidence_score": 95.0,
            "grounding_info": f"Calculated from {total_rows} rows."
        }
    
    def _format_comparison(self, result: Dict, parsed: Dict, total_rows: int) -> Dict[str, Any]:
        """Format comparison results"""
        groupby = result.get("groupby")
        results = result.get("results", [])
        
        answer = f"**Comparison by {groupby}:**\n" + "\n".join([
            f"• {item.get(groupby)}: {item}" for item in results
        ])
        
        return {
            "answer": answer,
            "sql_logic": f"SELECT {groupby}, COUNT(*) FROM dataset GROUP BY {groupby}",
            "derivation": {
                "rows_analyzed": total_rows,
                "groupby": groupby,
                "results": results
            },
            "visualization_type": "bar",
            "chart_data": {
                "labels": [str(item.get(groupby)) for item in results],
                "datasets": [{
                    "data": [item.get("count", 0) for item in results],
                    "backgroundColor": "#EAAB00"
                }]
            },
            "row_count": total_rows,
            "confidence_score": 90.0,
            "grounding_info": f"Compared across {total_rows} rows."
        }
    
    def _format_generic(self, result: Dict, parsed: Dict, total_rows: int) -> Dict[str, Any]:
        """Generic formatter for unknown types"""
        return {
            "answer": f"Analysis complete. Result: {result}",
            "sql_logic": "-- Query executed successfully",
            "derivation": {
                "rows_analyzed": total_rows,
                "result": result
            },
            "visualization_type": "none",
            "chart_data": {},
            "row_count": total_rows,
            "confidence_score": 75.0,
            "grounding_info": f"Based on {total_rows} rows."
        }
    
    def _calculate_confidence(self, result: Dict, parsed: Dict, total_rows: int) -> float:
        """Calculate confidence score based on query clarity and execution - GENERIC"""
        base_confidence = 80.0
        
        # Boost for deterministic operations
        result_type = result.get("type", "")
        if result_type in ["binary_rate_analysis", "simple_binary_rate", "grouped_count", "simple_count", 
                          "grouped_average", "grouped_sum", "simple_average"]:
            base_confidence += 15.0
        
        # Boost for column matches
        if parsed.get("target_columns"):
            base_confidence += 5.0
        
        # Cap at 100
        return min(base_confidence, 100.0)
