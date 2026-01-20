"""Database Manager exceptions."""

from .BaseProjectException import BaseProjectException


class DatabaseConnectionException(BaseProjectException):
    """Exception raised when database connection fails."""
    
    def __init__(self, message: str):
        super().__init__(message, "DB_CONNECTION_ERROR")

class IngestionRegistrationException(BaseProjectException):
    """Exception raised when registering document ingestion fails."""
    
    def __init__(self, message: str):
        super().__init__(message, "INGESTION_REGISTRATION_ERROR")


class IngestionStatusUpdateException(BaseProjectException):
    """Exception raised when updating ingestion status fails."""
    
    def __init__(self, message: str):
        super().__init__(message, "INGESTION_STATUS_UPDATE_ERROR")


class DatabaseTableCreationException(BaseProjectException):
    """Exception raised when creating database table fails."""
    
    def __init__(self, message: str):
        super().__init__(message, "TABLE_CREATION_ERROR")


class IngestionTableCleanException(BaseProjectException):
    """Exception raised when cleaning ingestion table fails."""
    
    def __init__(self, message: str):
        super().__init__(message, "TABLE_CLEAN_ERROR")
