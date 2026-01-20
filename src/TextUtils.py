import re
import os
from datetime import datetime
from pypdf import PdfReader

from .exceptions.UtilsException import MetadataExtractionException, InvalidFileFormatException

class TextUtils:
    """Utility class for text processing and metadata extraction"""

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text while preserving important punctuation"""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    
    @staticmethod
    def extract_metadata(file_path: str) -> dict:
        """Extract metadata from a PDF file
        Args:
            file_path: Path to the PDF file
        Returns:
            Dictionary containing metadata
        Raises:
            MetadataExtractionException: If metadata extraction fails
            InvalidFileFormatException: If the file format is invalid
        """
        
        # File existence check
        if not os.path.exists(file_path):
            raise MetadataExtractionException(f"File not found: {file_path}", file_path)
        
        # Check if it's a file (not a directory)
        if not os.path.isfile(file_path):
            raise MetadataExtractionException(f"Path is not a file: {file_path}", file_path)
        
        # Check file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext != '.pdf':
            raise InvalidFileFormatException(file_path, ".pdf")
        
        # Check file is readable
        if not os.access(file_path, os.R_OK):
            raise MetadataExtractionException(f"File is not readable: {file_path}", file_path)

        metadata = {
            "source": os.path.basename(file_path),
            "ingestion_date": datetime.now().isoformat(),
            "file_size_kb": round(os.path.getsize(file_path) / 1024, 2),
        }

        try:
            reader = PdfReader(file_path)
            info = reader.metadata
            
            if info:
                metadata.update({
                    "author": info.get('/Author', 'Unknown'),
                    "creator": info.get('/Creator', 'Unknown'),
                    "creation_date": info.get('/CreationDate', 'Unknown'),
                    "total_pages": len(reader.pages)
                })
        except Exception as e:
            metadata["total_pages"] = 0
            raise MetadataExtractionException(str(e), file_path) from e

        return metadata
