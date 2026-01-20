"""Custom exceptions for document ingestion operations."""

from .BaseProjectException import BaseProjectException


class DocumentLoadingException(BaseProjectException):
    """Exception raised when document loading fails."""
    
    def __init__(self, message: str, file_path: str):
        self.file_path = file_path
        error_msg = f"Failed to load document {file_path}: {message}" if file_path else message
        super().__init__(error_msg, error_code="DOCUMENT_LOAD_ERROR")


class DocumentSplittingException(BaseProjectException):
    """Exception raised when document splitting fails."""
    
    def __init__(self, message: str, file_path: str):
        self.file_path = file_path
        error_msg = f"Failed to split document {file_path}: {message}" if file_path else message
        super().__init__(error_msg, error_code="DOCUMENT_SPLIT_ERROR")


class VectorStorageException(BaseProjectException):
    """Exception raised when vector storage operation fails."""
    
    def __init__(self, message: str):
        super().__init__(message, error_code="VECTOR_STORAGE_ERROR")

class SaveDataException(BaseProjectException):
    """Exception raised when saving processed data fails."""
    
    def __init__(self, message: str):
        super().__init__(message, error_code="SAVE_DATA_ERROR")
