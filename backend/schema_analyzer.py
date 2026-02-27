"""
Schema Analyzer Module
Detects and categorizes column types in datasets
"""

import pandas as pd
from typing import Dict, List, Any
import numpy as np


class SchemaAnalyzer:
    """Analyzes dataset schema and categorizes columns"""
    
    def __init__(self):
        self.schema = {}
    
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze DataFrame schema
        
        Returns:
            Dictionary with categorized columns and type information
        """
        schema = {
            "columns": [],
            "numeric_columns": [],
            "categorical_columns": [],
            "date_columns": [],
            "boolean_columns": [],
            "total_columns": len(df.columns),
            "total_rows": len(df)
        }
        
        for column in df.columns:
            col_info = self._analyze_column(df[column], column)
            schema["columns"].append(col_info)
            
            # Categorize
            if col_info["type"] == "numeric":
                schema["numeric_columns"].append(column)
            elif col_info["type"] == "categorical":
                schema["categorical_columns"].append(column)
            elif col_info["type"] == "date":
                schema["date_columns"].append(column)
            elif col_info["type"] == "boolean":
                schema["boolean_columns"].append(column)
        
        self.schema = schema
        return schema
    
    def _analyze_column(self, series: pd.Series, column_name: str) -> Dict[str, Any]:
        """Analyze individual column"""
        
        col_info = {
            "name": column_name,
            "type": "unknown",
            "dtype": str(series.dtype),
            "null_count": int(series.isnull().sum()),
            "null_percentage": round(series.isnull().sum() / len(series) * 100, 2),
            "unique_count": int(series.nunique()),
            "sample_values": []
        }
        
        # Get sample values (non-null)
        non_null = series.dropna()
        if len(non_null) > 0:
            col_info["sample_values"] = [str(v) for v in non_null.head(3).tolist()]
        
        # Determine type
        if pd.api.types.is_numeric_dtype(series):
            col_info["type"] = "numeric"
            col_info["min"] = float(series.min()) if not series.isnull().all() else None
            col_info["max"] = float(series.max()) if not series.isnull().all() else None
            col_info["mean"] = float(series.mean()) if not series.isnull().all() else None
        
        elif pd.api.types.is_datetime64_any_dtype(series):
            col_info["type"] = "date"
            if not series.isnull().all():
                col_info["min_date"] = str(series.min())
                col_info["max_date"] = str(series.max())
        
        elif pd.api.types.is_bool_dtype(series):
            col_info["type"] = "boolean"
        
        else:
            # Check if it's categorical
            unique_ratio = series.nunique() / len(series)
            
            # Try to detect boolean-like strings
            unique_vals = set(series.dropna().astype(str).str.lower().unique())
            if unique_vals.issubset({'yes', 'no', 'true', 'false', '1', '0', 'y', 'n'}):
                col_info["type"] = "boolean"
            
            # Try to detect dates in string format
            elif self._is_date_string(series):
                col_info["type"] = "date"
            
            # Categorical if unique ratio is low
            elif unique_ratio < 0.5:
                col_info["type"] = "categorical"
                # Get value counts for top categories
                top_values = series.value_counts().head(5).to_dict()
                col_info["top_categories"] = {str(k): int(v) for k, v in top_values.items()}
            
            else:
                col_info["type"] = "text"
        
        return col_info
    
    def _is_date_string(self, series: pd.Series) -> bool:
        """Check if string column contains dates"""
        try:
            # Sample a few values
            sample = series.dropna().head(10)
            if len(sample) == 0:
                return False
            
            # Try to parse as dates
            parsed = pd.to_datetime(sample, errors='coerce')
            success_rate = parsed.notna().sum() / len(sample)
            
            return success_rate > 0.8
        except:
            return False
    
    def get_numeric_columns(self) -> List[str]:
        """Get list of numeric columns"""
        return self.schema.get("numeric_columns", [])
    
    def get_categorical_columns(self) -> List[str]:
        """Get list of categorical columns"""
        return self.schema.get("categorical_columns", [])
    
    def get_date_columns(self) -> List[str]:
        """Get list of date columns"""
        return self.schema.get("date_columns", [])
    
    def get_column_type(self, column_name: str) -> str:
        """Get type of specific column"""
        for col in self.schema.get("columns", []):
            if col["name"] == column_name:
                return col["type"]
        return "unknown"
    
    def generate_suggested_questions(self) -> List[str]:
        """
        Generate smart suggested questions based on detected schema
        
        Rules:
        - If numeric + categorical: "What is average [numeric] by [categorical]?"
        - If datetime + numeric: "Show trend of [numeric] over time"
        - If categorical only: "What is distribution of [categorical]?"
        - If binary column (Yes/No, True/False): "What is the [column] rate?"
        """
        suggestions = []
        
        numeric_cols = self.schema.get("numeric_columns", [])
        categorical_cols = self.schema.get("categorical_columns", [])
        date_cols = self.schema.get("date_columns", [])
        boolean_cols = self.schema.get("boolean_columns", [])
        
        # Basic count question
        suggestions.append("How many total records are in the dataset?")
        
        # Numeric + Categorical combinations
        if numeric_cols and categorical_cols:
            num_col = numeric_cols[0]
            cat_col = categorical_cols[0]
            suggestions.append(f"What is the average {num_col} by {cat_col}?")
            suggestions.append(f"Show me the total {num_col} by {cat_col}")
            if len(categorical_cols) > 1:
                suggestions.append(f"Compare {num_col} across {categorical_cols[1]}")
        
        # Date + Numeric (time series)
        if date_cols and numeric_cols:
            date_col = date_cols[0]
            num_col = numeric_cols[0]
            suggestions.append(f"Show {num_col} trend over {date_col}")
            suggestions.append(f"What is the {num_col} distribution over time?")
        
        # Categorical distribution
        if categorical_cols:
            cat_col = categorical_cols[0]
            suggestions.append(f"What is the distribution of {cat_col}?")
            suggestions.append(f"Count records by {cat_col}")
        
        # Boolean/Binary analysis (detect rate calculations)
        if boolean_cols:
            bool_col = boolean_cols[0]
            suggestions.append(f"What is the {bool_col} rate?")
            if categorical_cols:
                suggestions.append(f"What is the {bool_col} rate by {categorical_cols[0]}?")
        
        # Check for binary-like categories (Yes/No, True/False, 0/1)
        for col_info in self.schema.get("columns", []):
            if col_info["type"] == "categorical" and col_info.get("unique_count", 0) == 2:
                # This might be a binary outcome column
                col_name = col_info["name"]
                # Check if it looks like a rate/outcome
                rate_keywords = ['churn', 'convert', 'success', 'fail', 'active', 'status', 'flag']
                if any(keyword in col_name.lower() for keyword in rate_keywords):
                    suggestions.append(f"What is the {col_name} rate?")
                    if categorical_cols and col_name not in categorical_cols[:1]:
                        suggestions.append(f"Compare {col_name} rate by {categorical_cols[0]}")
                    break
        
        # Multiple categorical comparisons
        if len(categorical_cols) >= 2:
            suggestions.append(f"Compare {categorical_cols[0]} vs {categorical_cols[1]}")
        
        # Numeric comparisons
        if len(numeric_cols) >= 2:
            suggestions.append(f"What is the correlation between {numeric_cols[0]} and {numeric_cols[1]}?")
        
        # Return top 5-6 most relevant suggestions
        return suggestions[:6]
