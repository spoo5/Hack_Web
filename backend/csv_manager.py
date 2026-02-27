"""
CSV Manager Module
Handles CSV file upload, validation, and storage
"""

import pandas as pd
import io
from typing import Dict, Any, Optional


class CSVManager:
    """Manages CSV dataset storage and access"""
    
    def __init__(self):
        self.dataframe: Optional[pd.DataFrame] = None
        self.filename: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
    
    def load_csv(self, content: bytes, filename: str) -> Dict[str, Any]:
        """
        Load CSV from bytes content
        
        Args:
            content: Raw CSV file content as bytes
            filename: Original filename
            
        Returns:
            Dictionary with dataset information
        """
        try:
            # Parse CSV
            self.dataframe = pd.read_csv(io.BytesIO(content))
            self.filename = filename
            
            # Store metadata
            self.metadata = {
                "filename": filename,
                "row_count": len(self.dataframe),
                "column_count": len(self.dataframe.columns),
                "columns": list(self.dataframe.columns),
                "size_bytes": len(content)
            }
            
            # Generate preview (first 5 rows)
            preview = self.dataframe.head(5).to_dict(orient="records")
            
            return {
                "row_count": self.metadata["row_count"],
                "column_count": self.metadata["column_count"],
                "columns": self.metadata["columns"],
                "preview": preview
            }
        
        except Exception as e:
            raise Exception(f"Failed to parse CSV: {str(e)}")
    
    def has_dataset(self) -> bool:
        """Check if dataset is loaded"""
        return self.dataframe is not None and not self.dataframe.empty
    
    def get_dataframe(self) -> pd.DataFrame:
        """Get the loaded DataFrame"""
        if not self.has_dataset():
            raise Exception("No dataset loaded")
        return self.dataframe
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get dataset metadata"""
        return self.metadata
    
    def get_column_names(self):
        """Get list of column names"""
        if not self.has_dataset():
            return []
        return list(self.dataframe.columns)
    
    def get_row_count(self) -> int:
        """Get total row count"""
        if not self.has_dataset():
            return 0
        return len(self.dataframe)
    
    def clear(self):
        """Clear loaded dataset"""
        self.dataframe = None
        self.filename = None
        self.metadata = {}
