"""
Analytics Engine Module
Executes queries using Pandas - ALL COMPUTATIONS ARE DETERMINISTIC
NO HALLUCINATION - All numbers computed from actual data
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


class AnalyticsEngine:
    """Executes data analytics operations using Pandas"""
    
    def execute(self, df: pd.DataFrame, parsed_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute parsed query on DataFrame
        
        Args:
            df: Source DataFrame
            parsed_query: Parsed query structure
            
        Returns:
            Result dictionary with computed values
        """
        operation = parsed_query.get("operation", "describe")
        
        # Apply filters first
        filtered_df = self._apply_filters(df, parsed_query.get("filter_conditions", []))
        
        # Route to appropriate operation
        if operation == "count":
            return self._execute_count(filtered_df, parsed_query)
        
        elif operation == "average":
            return self._execute_average(filtered_df, parsed_query)
        
        elif operation == "sum":
            return self._execute_sum(filtered_df, parsed_query)
        
        elif operation == "percentage":
            return self._execute_percentage(filtered_df, parsed_query, df)
        
        elif operation == "compare":
            return self._execute_comparison(filtered_df, parsed_query)
        
        else:
            return self._execute_describe(filtered_df, parsed_query)
    
    def _apply_filters(self, df: pd.DataFrame, filters: List[Dict]) -> pd.DataFrame:
        """Apply filter conditions to DataFrame"""
        filtered = df.copy()
        
        for filter_cond in filters:
            column = filter_cond.get("column")
            operator = filter_cond.get("operator", "==")
            value = filter_cond.get("value")
            
            if column not in filtered.columns:
                continue
            
            if operator == "==":
                filtered = filtered[filtered[column] == value]
            elif operator == "!=":
                filtered = filtered[filtered[column] != value]
            elif operator == ">":
                filtered = filtered[filtered[column] > value]
            elif operator == "<":
                filtered = filtered[filtered[column] < value]
            elif operator == ">=":
                filtered = filtered[filtered[column] >= value]
            elif operator == "<=":
                filtered = filtered[filtered[column] <= value]
            elif operator == "in":
                filtered = filtered[filtered[column].isin(value)]
        
        return filtered
    
    def _execute_count(self, df: pd.DataFrame, parsed: Dict) -> Dict[str, Any]:
        """Execute count operation"""
        groupby_col = parsed.get("groupby_column")
        
        if groupby_col and groupby_col in df.columns:
            # Grouped count
            result = df.groupby(groupby_col).size().reset_index(name='count')
            
            return {
                "type": "grouped_count",
                "groupby": groupby_col,
                "results": result.to_dict(orient='records'),
                "total": len(df),
                "groups": len(result)
            }
        else:
            # Simple count
            return {
                "type": "simple_count",
                "count": len(df),
                "total": len(df)
            }
    
    def _execute_average(self, df: pd.DataFrame, parsed: Dict) -> Dict[str, Any]:
        """Execute average operation"""
        target_cols = parsed.get("target_columns", [])
        groupby_col = parsed.get("groupby_column")
        
        # Find numeric columns
        numeric_cols = [col for col in target_cols if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
        
        if not numeric_cols:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()[:1]
        
        if not numeric_cols:
            return {"type": "error", "message": "No numeric columns found for average calculation"}
        
        target_col = numeric_cols[0]
        
        if groupby_col and groupby_col in df.columns:
            # Grouped average
            result = df.groupby(groupby_col)[target_col].mean().reset_index()
            result.columns = [groupby_col, 'average']
            
            return {
                "type": "grouped_average",
                "column": target_col,
                "groupby": groupby_col,
                "results": result.to_dict(orient='records'),
                "overall_average": float(df[target_col].mean())
            }
        else:
            # Simple average
            return {
                "type": "simple_average",
                "column": target_col,
                "average": float(df[target_col].mean()),
                "count": len(df)
            }
    
    def _execute_sum(self, df: pd.DataFrame, parsed: Dict) -> Dict[str, Any]:
        """Execute sum operation"""
        target_cols = parsed.get("target_columns", [])
        groupby_col = parsed.get("groupby_column")
        
        # Find numeric columns
        numeric_cols = [col for col in target_cols if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
        
        if not numeric_cols:
            return {"type": "error", "message": "No numeric columns found for sum calculation"}
        
        target_col = numeric_cols[0]
        
        if groupby_col and groupby_col in df.columns:
            # Grouped sum
            result = df.groupby(groupby_col)[target_col].sum().reset_index()
            result.columns = [groupby_col, 'sum']
            
            return {
                "type": "grouped_sum",
                "column": target_col,
                "groupby": groupby_col,
                "results": result.to_dict(orient='records'),
                "total_sum": float(df[target_col].sum())
            }
        else:
            # Simple sum
            return {
                "type": "simple_sum",
                "column": target_col,
                "sum": float(df[target_col].sum()),
                "count": len(df)
            }
    
    def _execute_percentage(self, df: pd.DataFrame, parsed: Dict, original_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Execute percentage/rate calculation - FULLY GENERIC
        Works for any binary column, not just churn
        """
        
        # Check if this is a binary rate query (Yes/No, True/False, 0/1)
        aggregation = parsed.get("aggregation", {})
        if aggregation.get("type") == "binary_rate":
            return self._calculate_binary_rate(df, parsed)
        
        # Generic percentage distribution
        groupby_col = parsed.get("groupby_column")
        
        if groupby_col and groupby_col in df.columns:
            # Calculate percentage distribution
            counts = df[groupby_col].value_counts()
            total = len(df)
            
            results = []
            for value, count in counts.items():
                percentage = (count / total) * 100
                results.append({
                    groupby_col: str(value),
                    "count": int(count),
                    "percentage": round(percentage, 2)
                })
            
            return {
                "type": "percentage_distribution",
                "groupby": groupby_col,
                "results": results,
                "total": total
            }
        
        return {"type": "error", "message": "Could not calculate percentage. Please specify a grouping column or binary field."}
    
    def _calculate_binary_rate(self, df: pd.DataFrame, parsed: Dict) -> Dict[str, Any]:
        """
        Calculate rate for any binary column (Yes/No, True/False, Active/Inactive, etc.)
        GENERIC - no hardcoded column names
        """
        aggregation = parsed.get("aggregation", {})
        target_col = aggregation.get("target_column")
        positive_value = aggregation.get("positive_value", "Yes")
        groupby_col = parsed.get("groupby_column")
        
        # Validate target column exists
        if not target_col or target_col not in df.columns:
            return {
                "type": "error",
                "message": f"Column '{target_col}' not found in dataset. Available columns: {', '.join(df.columns)}"
            }
        
        if groupby_col and groupby_col in df.columns:
            # Calculate rate by group
            results = []
            
            for group_value in df[groupby_col].unique():
                group_df = df[df[groupby_col] == group_value]
                total_in_group = len(group_df)
                positive_in_group = len(group_df[group_df[target_col].astype(str) == str(positive_value)])
                rate = (positive_in_group / total_in_group * 100) if total_in_group > 0 else 0
                
                results.append({
                    groupby_col: str(group_value),
                    "total": total_in_group,
                    "positive_count": positive_in_group,
                    "rate": round(rate, 2),
                    "formula": f"{positive_in_group} ÷ {total_in_group} × 100"
                })
            
            # Overall rate
            total_overall = len(df)
            positive_overall = len(df[df[target_col].astype(str) == str(positive_value)])
            overall_rate = (positive_overall / total_overall * 100) if total_overall > 0 else 0
            
            return {
                "type": "binary_rate_analysis",
                "target_column": target_col,
                "positive_value": positive_value,
                "groupby": groupby_col,
                "results": results,
                "overall": {
                    "total": total_overall,
                    "positive_count": positive_overall,
                    "rate": round(overall_rate, 2),
                    "formula": f"{positive_overall} ÷ {total_overall} × 100"
                }
            }
        else:
            # Simple rate (no grouping)
            total = len(df)
            positive_count = len(df[df[target_col].astype(str) == str(positive_value)])
            rate = (positive_count / total * 100) if total > 0 else 0
            
            return {
                "type": "simple_binary_rate",
                "target_column": target_col,
                "positive_value": positive_value,
                "total": total,
                "positive_count": positive_count,
                "rate": round(rate, 2),
                "formula": f"{positive_count} ÷ {total} × 100"
            }
    
    def _execute_comparison(self, df: pd.DataFrame, parsed: Dict) -> Dict[str, Any]:
        """Execute comparison operation"""
        groupby_col = parsed.get("groupby_column")
        target_cols = parsed.get("target_columns", [])
        
        if not groupby_col or groupby_col not in df.columns:
            return {"type": "error", "message": "No grouping column specified for comparison"}
        
        # Find numeric column for comparison
        numeric_cols = [col for col in target_cols if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
        
        if not numeric_cols:
            # Use count
            result = df.groupby(groupby_col).size().reset_index(name='count')
            
            return {
                "type": "count_comparison",
                "groupby": groupby_col,
                "results": result.to_dict(orient='records')
            }
        else:
            # Compare numeric values
            target_col = numeric_cols[0]
            result = df.groupby(groupby_col)[target_col].agg(['mean', 'sum', 'count']).reset_index()
            
            return {
                "type": "numeric_comparison",
                "column": target_col,
                "groupby": groupby_col,
                "results": result.to_dict(orient='records')
            }
    
    def _execute_describe(self, df: pd.DataFrame, parsed: Dict) -> Dict[str, Any]:
        """Execute description/summary operation"""
        target_cols = parsed.get("target_columns", [])
        
        if target_cols:
            # Describe specific columns
            valid_cols = [col for col in target_cols if col in df.columns]
            if valid_cols:
                description = df[valid_cols].describe().to_dict()
                return {
                    "type": "description",
                    "columns": valid_cols,
                    "statistics": description
                }
        
        # General summary
        return {
            "type": "summary",
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns)
        }
