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

from .ModelQueryException import (
   DocumentRetrieveException,
    ModelResponseException, 
    RAGQueryException,
    DBConnectionException
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
    "DBConnectionException"
]
