"""Custom exceptions for TextUtils and utility functions."""
from .BaseProjectException import BaseProjectException

class MetadataExtractionException(BaseProjectException):
    """Exception raised when metadata extraction fails."""
    
    def __init__(self, message: str, file_path: str):
        self.file_path = file_path
        error_msg = f"Failed to extract metadata from {file_path}: {message}" if file_path else message
        super().__init__(error_msg, error_code="METADATA_ERROR")

class InvalidFileFormatException(BaseProjectException):
    """Exception raised for invalid file formats."""
    
    def __init__(self, file_path: str, expected_format: str):
        self.file_path = file_path
        error_msg = f"Invalid file format for {file_path}. Expected format: {expected_format}"
        super().__init__(error_msg, error_code="INVALID_FILE_FORMAT")