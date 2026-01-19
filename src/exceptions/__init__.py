"""Custom exceptions module."""

from .UtilsException import (
    MetadataExtractionException,
    InvalidFileFormatException
)

from .DocumentIngestorException import (
    DocumentLoadingException,
    DocumentSplittingException,
    VectorStorageException,
    SaveDataException
)

from .QueryEngineException import (
   DocumentRetrieveException,
    ModelResponseException, 
    RAGQueryException,
    DBConnectionException
)

from .DatabaseManagerException import (
    DatabaseConnectionException,
    IngestionRegistrationException,
    IngestionStatusUpdateException,
    DatabaseTableCreationException,
    IngestionTableCleanException
)

__all__ = [
    "UtilsException",
    "MetadataExtractionException",
    "DocumentLoadingException",
    "DocumentSplittingException",
    "VectorStorageException",
    "SaveDataException",
    "InvalidFileFormatException",
    "DocumentRetrieveException",
    "ModelResponseException",
    "RAGQueryException",
    "DBConnectionException",
    "DatabaseConnectionException",
    "IngestionRegistrationException",
    "IngestionStatusUpdateException",
    "DatabaseTableCreationException",
    "IngestionTableCleanException"
]
