import pandas as pd
import chardet
from fastapi import UploadFile
from typing import Tuple
from io import BytesIO
import os


class FileValidationError(Exception):
    pass

class DatasetRepository:
    MAX_FILE_SIZE_MB = 20
    MAX_ROWS =  500_000
    MAX_COLUMNS = 300

    ALLOWED_EXTENSIONS = { ".csv", ".xlsx", ".xls"}
    ALLOWED_MIME_TYPES = {
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/octet-stream"
    }
    
    def _validate_basic_metadata(self, file: UploadFile):
        
        if not file.filename:
            raise FileValidationError("File has no file name")
        
        ext = os.path.splitext(file.filename)[1].lower()

        if ext not in self.ALLOWED_EXTENSIONS:
            raise FileValidationError("Unsupported file type. Only CSV and Excel files are allowed.")

        if file.content_type not in self.ALLOWED_MIME_TYPES:
            raise FileValidationError(f"Invalid MIME type: {file.content_type}")

        return ext
    
    def _validate_size(self, file_bytes: bytes):
        size_mb = len(file_bytes) / (1024 * 1024)
        if size_mb > self.MAX_FILE_SIZE_MB:
            raise FileValidationError(f"File too large. Max allowed size is {self.MAX_FILE_SIZE_MB}MB.")

    def _detect_encoding(self, raw_bytes: bytes) -> str:
        result = chardet.detect(raw_bytes[:50000])  # sample
        encoding = result.get("encoding") or "utf-8"
        return encoding
    
    def _parse_csv(self, file_bytes: bytes) -> pd.DataFrame:
        encoding = self._detect_encoding(file_bytes)

        try:
            df = pd.read_csv(
                BytesIO(file_bytes),
                encoding=encoding,
                dtype=str,          # prevent dtype chaos
                keep_default_na=False
            )
        except Exception as e:
            raise FileValidationError(f"CSV parsing failed: {str(e)}")

        return df
    
    def _parse_excel(self, file_bytes: bytes) -> pd.DataFrame:
        try:
            excel = pd.ExcelFile(BytesIO(file_bytes))
        except Exception:
            raise FileValidationError("Invalid or corrupted Excel file.")

        if len(excel.sheet_names) == 0:
            raise FileValidationError("Excel file contains no sheets.")

        # Use first sheet by default
        try:
            df = excel.parse(excel.sheet_names[0], dtype=str)
        except Exception as e:
            raise FileValidationError(f"Excel parsing failed: {str(e)}")

        return df
    
    def _validate_dataframe(self, df: pd.DataFrame):
        if df is None:
            raise FileValidationError("No data found.")

        if df.empty:
            raise FileValidationError("Uploaded file contains no rows.")

        if len(df.columns) == 0:
            raise FileValidationError("No columns detected in file.")

        if df.shape[0] > self.MAX_ROWS:
            raise FileValidationError(f"Too many rows. Max allowed is {self.MAX_ROWS}.")

        if df.shape[1] > self.MAX_COLUMNS:
            raise FileValidationError(f"Too many columns. Max allowed is {self.MAX_COLUMNS}.")

        # Normalize headers
        df.columns = [str(col).strip() for col in df.columns]

        # Header sanity
        if any(col == "" for col in df.columns):
            raise FileValidationError("One or more column headers are empty.")

        # Duplicate columns
        if len(set(df.columns)) != len(df.columns):
            raise FileValidationError("Duplicate column names detected.")

        return df
    
    def infer_schema(self, df: pd.DataFrame) -> dict:
        schema = {}
        for col in df.columns:
            schema[col] = "string"  # default
        return schema

    
    def normalize_records(self, df: pd.DataFrame) -> list[dict]:
        records = df.to_dict(orient="records")

        normalized = []
        for row in records:
            clean_row = {}
            for k, v in row.items():
                if pd.isna(v):
                    clean_row[k] = None
                else:
                    clean_row[k] = str(v).strip()
            normalized.append(clean_row)

        return normalized
    
    async def validate_and_parse_upload(self, file: UploadFile) -> pd.DataFrame:
        """
        Validates and parses CSV or Excel upload.
        Returns clean pandas DataFrame.
        Raises HTTPException on failure.
        """

        ext = self._validate_basic_metadata(file)

        file_bytes = await file.read()
        self._validate_size(file_bytes)

        if ext == ".csv":
            df = self._parse_csv(file_bytes)
        else:
            df = self._parse_excel(file_bytes)

        df = self._validate_dataframe(df)

        # Normalize NaN
        df = df.fillna("")

        return df



dataset_repository = DatasetRepository()