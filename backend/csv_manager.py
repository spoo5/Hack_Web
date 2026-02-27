"""
CSV Manager Module
Handles CSV file upload, validation, and storage
"""

import io
import os
import tempfile
from typing import Dict, Any, Optional

import duckdb
import pandas as pd


class CSVManager:
    """Manages CSV dataset storage and access"""
    
    def __init__(self):
        self.dataframe: Optional[pd.DataFrame] = None
        self.filename: Optional[str] = None
        self.metadata: Dict[str, Any] = {}
        self._con: Optional[duckdb.DuckDBPyConnection] = None
        self._tmpfile: Optional[str] = None
    
    def load_csv(self, content: bytes, filename: str) -> Dict[str, Any]:
        """
        Load CSV from bytes content into both pandas and DuckDB.
        
        Args:
            content: Raw CSV file content as bytes
            filename: Original filename
            
        Returns:
            Dictionary with dataset information
        """
        try:
            # Parse CSV into pandas DataFrame
            self.dataframe = pd.read_csv(io.BytesIO(content))
            self.filename = filename
            
            # Write content to a temp file so DuckDB can read it
            if self._tmpfile and os.path.exists(self._tmpfile):
                os.unlink(self._tmpfile)
            tmp = tempfile.NamedTemporaryFile(
                delete=False, suffix=".csv", mode="wb"
            )
            tmp.write(content)
            tmp.close()
            self._tmpfile = tmp.name

            # (Re)create in-memory DuckDB connection and load the table
            if self._con is not None:
                try:
                    self._con.close()
                except Exception:
                    pass
            self._con = duckdb.connect()
            self._con.execute("DROP TABLE IF EXISTS data")
            escaped = self._tmpfile.replace("'", "''")
            self._con.execute(
                f"CREATE TABLE data AS SELECT * FROM read_csv('{escaped}', "
                "auto_detect=true, null_padding=true)"
            )

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

    def get_connection(self) -> Optional[duckdb.DuckDBPyConnection]:
        """Get the DuckDB connection (None if no dataset loaded)"""
        return self._con
    
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
        if self._con is not None:
            try:
                self._con.close()
            except Exception:
                pass
            self._con = None
        if self._tmpfile and os.path.exists(self._tmpfile):
            os.unlink(self._tmpfile)
        self._tmpfile = None
