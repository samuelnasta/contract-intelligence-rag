"""Custom exceptions module."""

from .UtilsException import (
    MetadataExtractionException,
    InvalidFileFormatException
)

from .DocumentIngestorException import (
    DocumentLoadingException,
    DocumentSplittingException,
    EmbeddingGenerationException,
    VectorStorageException
)

__all__ = [
    "UtilsException",
    "MetadataExtractionException",
    "DocumentLoadingException",
    "DocumentSplittingException",
    "EmbeddingGenerationException",
    "VectorStorageException",
    "InvalidFileFormatException"
]
