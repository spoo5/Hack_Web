"""
Query Parser Module
Parses natural language queries and maps to database operations
FULLY DATASET-AGNOSTIC - No hardcoded column names or business logic
Integrates Mistral AI LLM for NL-to-SQL with rule-based fallback.
"""

import os
import re
from typing import Dict, List, Any, Optional
from difflib import get_close_matches

# LLM integration (optional – falls back gracefully if unavailable)
try:
    from llm import get_client, nl_to_sql as _nl_to_sql

    _api_key = os.environ.get("MISTRAL_API_KEY", "")
    _llm_client = get_client(_api_key) if _api_key else None
    _llm_model = os.environ.get("MISTRAL_MODEL", "mistral-large-latest")
except Exception:
    _llm_client = None
    _llm_model = "mistral-large-latest"


class QueryParser:
    """Parses natural language queries into structured operations - 100% dynamic"""
    
    def __init__(self):
        # Operation keywords
        self.count_keywords = ['count', 'how many', 'number of', 'total number']
        self.sum_keywords = ['sum', 'total', 'aggregate', 'combined']
        self.avg_keywords = ['average', 'avg', 'mean']
        self.percentage_keywords = ['percentage', 'percent', 'rate', 'ratio', '%']
        self.groupby_keywords = ['by', 'per', 'for each', 'across', 'breakdown', 'grouped by']
        self.filter_keywords = ['where', 'with', 'having', 'only', 'just', 'filter']
        self.compare_keywords = ['compare', 'comparison', 'vs', 'versus', 'difference', 'against']
        self.trend_keywords = ['trend', 'over time', 'time series', 'timeline', 'progression']
        self.distribution_keywords = ['distribution', 'spread', 'breakdown']
        self.max_keywords = ['highest', 'maximum', 'max', 'largest', 'top', 'most']
        self.min_keywords = ['lowest', 'minimum', 'min', 'smallest', 'bottom', 'least']

    # ------------------------------------------------------------------
    # LLM-assisted SQL generation (returns a SQL string, or None)
    # ------------------------------------------------------------------
    def _try_llm_sql(self, query: str, schema: Dict[str, Any]) -> Optional[str]:
        """
        Attempt to get a SQL string from the Mistral LLM.
        Returns None on any failure so callers can fall back to rule-based parsing.
        """
        try:
            if _llm_client is None:
                return None
            # Build the profile dict expected by nl_to_sql
            profile = {
                "columns": [
                    {"name": col["name"], "dtype": col.get("dtype", col.get("type", "text"))}
                    for col in schema.get("columns", [])
                ],
                "sample": [],
            }
            sql = _nl_to_sql(query, profile, _llm_client, model=_llm_model)
            return sql if sql and sql.strip() else None
        except Exception:
            return None


    def parse(self, query: str, schema: Dict[str, Any], context: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Parse natural language query - tries LLM first, falls back to rule-based.
        
        Args:
            query: User's natural language question
            schema: Dataset schema information
            context: Previous conversation context
            
        Returns:
            Structured query dictionary (may include 'llm_sql' key when LLM is used)
        """
        # Try LLM-assisted SQL generation first
        llm_sql = self._try_llm_sql(query, schema)

        query_lower = query.lower()
        
        parsed = {
            "original_query": query,
            "operation": self._detect_operation(query_lower),
            "target_columns": [],
            "groupby_column": None,
            "filter_conditions": [],
            "aggregation": None,
            "sort_order": None
        }

        # Attach LLM-generated SQL if available (used by analytics_engine)
        if llm_sql:
            parsed["llm_sql"] = llm_sql

        # Extract column references from schema
        columns = schema.get("columns", [])
        column_names = [col["name"] for col in columns]
        numeric_columns = schema.get("numeric_columns", [])
        categorical_columns = schema.get("categorical_columns", [])
        date_columns = schema.get("date_columns", [])
        
        # Find columns mentioned in query
        mentioned_columns = self._find_columns_in_query(query, column_names)
        parsed["target_columns"] = mentioned_columns
        
        # Detect grouping column (categorical)
        groupby_col = self._detect_groupby(query_lower, categorical_columns, mentioned_columns)
        if groupby_col:
            parsed["groupby_column"] = groupby_col
        
        # Detect aggregation type for rate/percentage calculations
        if parsed["operation"] == "percentage":
            # Look for binary columns (Yes/No, True/False, 0/1) in mentioned columns
            rate_info = self._detect_rate_calculation(query_lower, mentioned_columns, schema)
            if rate_info:
                parsed["aggregation"] = rate_info
        
        # Detect sorting (highest/lowest)
        if any(kw in query_lower for kw in self.max_keywords):
            parsed["sort_order"] = "desc"
        elif any(kw in query_lower for kw in self.min_keywords):
            parsed["sort_order"] = "asc"
        
        # Detect comparison queries
        if any(kw in query_lower for kw in self.compare_keywords):
            parsed["operation"] = "compare"
        
        # Detect trend/time series queries
        if any(kw in query_lower for kw in self.trend_keywords):
            parsed["operation"] = "trend"
            # Ensure date column is in target
            if date_columns and not any(dc in mentioned_columns for dc in date_columns):
                parsed["target_columns"].append(date_columns[0])
        
        # Detect distribution queries
        if any(kw in query_lower for kw in self.distribution_keywords):
            if not groupby_col and categorical_columns:
                parsed["groupby_column"] = categorical_columns[0]
        
        # If no specific columns mentioned, infer from operation
        if not parsed["target_columns"]:
            parsed["target_columns"] = self._infer_columns(parsed["operation"], schema)
        
        return parsed
    
    
    def _detect_operation(self, query: str) -> str:
        """Detect primary operation type from query"""
        if any(kw in query for kw in self.count_keywords):
            return "count"
        elif any(kw in query for kw in self.avg_keywords):
            return "average"
        elif any(kw in query for kw in self.sum_keywords):
            return "sum"
        elif any(kw in query for kw in self.percentage_keywords):
            return "percentage"
        elif any(kw in query for kw in self.compare_keywords):
            return "compare"
        elif any(kw in query for kw in self.trend_keywords):
            return "trend"
        elif any(kw in query for kw in self.max_keywords + self.min_keywords):
            return "extremes"
        else:
            return "describe"
    
    def _find_columns_in_query(self, query: str, column_names: List[str]) -> List[str]:
        """Find column names mentioned in query using fuzzy matching"""
        found_columns = []
        query_lower = query.lower()
        
        for col in column_names:
            col_lower = col.lower()
            
            # Exact match
            if col_lower in query_lower:
                found_columns.append(col)
                continue
            
            # Fuzzy match (handles typos)
            matches = get_close_matches(col_lower, [query_lower], n=1, cutoff=0.75)
            if matches:
                found_columns.append(col)
                continue
            
            # Word-by-word match for multi-word columns
            col_words = col_lower.split()
            if len(col_words) > 1 and all(word in query_lower for word in col_words):
                found_columns.append(col)
                continue
            
            # Check for partial matches with underscores/camelCase
            col_parts = re.split(r'[_\s]+|(?<=[a-z])(?=[A-Z])', col_lower)
            if all(part in query_lower for part in col_parts if len(part) > 2):
                found_columns.append(col)
        
        return list(set(found_columns))
    
    def _detect_groupby(self, query: str, categorical_columns: List[str], mentioned_columns: List[str]) -> Optional[str]:
        """Detect groupby column - prefer categorical columns"""
        
        # Look for explicit "by X" pattern
        by_match = re.search(r'\bby\s+(\w+(?:\s+\w+)?)', query)
        if by_match:
            potential_col = by_match.group(1).strip()
            # Find matching column in categorical list
            matches = get_close_matches(potential_col, categorical_columns, n=1, cutoff=0.6)
            if matches:
                return matches[0]
        
        # If categorical columns are mentioned, use the first one
        categorical_mentioned = [col for col in mentioned_columns if col in categorical_columns]
        if categorical_mentioned:
            return categorical_mentioned[0]
        
        # Default to first categorical column if operation requires grouping
        if categorical_columns:
            return categorical_columns[0]
        
        return None
    
    def _detect_rate_calculation(self, query: str, mentioned_columns: List[str], schema: Dict) -> Optional[Dict]:
        """
        Detect rate/percentage calculation for binary columns (Yes/No, True/False, 0/1)
        GENERIC - works for any binary field, not just churn
        """
        # Look for mentioned columns that are binary (2 unique values)
        columns_info = schema.get("columns", [])
        
        for col_info in columns_info:
            col_name = col_info["name"]
            col_type = col_info["type"]
            unique_count = col_info.get("unique_count", 0)
            
            # Check if this column is mentioned and is binary
            if col_name in mentioned_columns and unique_count == 2:
                # Get the actual unique values
                sample_values = col_info.get("sample_values", [])
                
                # Determine which value represents the "positive" case
                positive_value = self._determine_positive_value(sample_values)
                
                return {
                    "type": "binary_rate",
                    "target_column": col_name,
                    "positive_value": positive_value,
                    "description": f"{col_name} rate"
                }
        
        # If no binary column found in mentioned, check if query contains rate/percentage keywords
        # and there are any binary columns in schema
        if any(kw in query for kw in ['rate', 'percentage', 'percent', '%']):
            for col_info in columns_info:
                if col_info.get("unique_count") == 2:
                    col_name = col_info["name"]
                    sample_values = col_info.get("sample_values", [])
                    positive_value = self._determine_positive_value(sample_values)
                    
                    return {
                        "type": "binary_rate",
                        "target_column": col_name,
                        "positive_value": positive_value,
                        "description": f"{col_name} rate"
                    }
        
        return None
    
    def _determine_positive_value(self, sample_values: List[str]) -> str:
        """
        Determine which value in a binary column represents the positive case
        Yes/True/1/Active/Success = positive
        No/False/0/Inactive/Failure = negative
        """
        if not sample_values:
            return sample_values[0] if sample_values else "Yes"
        
        positive_indicators = ['yes', 'true', '1', 'active', 'success', 'completed', 'approved']
        
        for val in sample_values:
            val_lower = str(val).lower().strip()
            if val_lower in positive_indicators:
                return str(val)
        
        # Default to first value
        return str(sample_values[0]) if sample_values else "Yes"
    
    def _infer_columns(self, operation: str, schema: Dict) -> List[str]:
        """Infer which columns to use based on operation type"""
        numeric_cols = schema.get("numeric_columns", [])
        categorical_cols = schema.get("categorical_columns", [])
        date_cols = schema.get("date_columns", [])
        
        if operation in ["average", "sum"]:
            # Return first numeric column
            return numeric_cols[:1] if numeric_cols else []
        
        elif operation == "count":
            # Count doesn't need specific columns
            return []
        
        elif operation == "trend":
            # Trend needs date + numeric
            result = []
            if date_cols:
                result.append(date_cols[0])
            if numeric_cols:
                result.append(numeric_cols[0])
            return result
        
        elif operation == "compare":
            # Compare needs categorical for grouping
            return categorical_cols[:1] if categorical_cols else []
        
        return []
