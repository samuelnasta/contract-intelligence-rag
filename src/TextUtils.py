import re
import os
from datetime import datetime
from typing import List
from pypdf import PdfReader

from .Logger import get_logger
from .exceptions.UtilsException import MetadataExtractionException, InvalidFileFormatException

class TextUtils:
    """Utility class for text processing and metadata extraction"""

    def __init__(self, name: str, text: str, file_path: str, response: str) -> None:
        self.name = name
        self.logger = get_logger()
        self.text = text
        self.file_path = file_path
        self.response = response
        

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters
        text = re.sub(r'[^\w\s.,;:]', '', text)
        return text.strip()
    

    def split_text_by_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        return [p.strip() for p in text.split('\n\n') if p.strip()]


    def format_response(self, response: str) -> str:
        """Format LLM response for presentation"""
        return response.strip()
    
    def extract_metadata(self, file_path: str) -> dict:
        """Extract metadata from a PDF file"""
        
        # File existence check
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            raise MetadataExtractionException(f"File not found: {file_path}", file_path)
        
        # Check if it's a file (not a directory)
        if not os.path.isfile(file_path):
            self.logger.error(f"Path is not a file: {file_path}")
            raise MetadataExtractionException(f"Path is not a file: {file_path}", file_path)
        
        # Check file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext != '.pdf':
            self.logger.error(f"Invalid file format: {file_ext}. Expected: .pdf")
            raise InvalidFileFormatException(file_path, ".pdf")
        
        # Check file is readable
        if not os.access(file_path, os.R_OK):
            self.logger.error(f"File is not readable: {file_path}")
            raise MetadataExtractionException(f"File is not readable: {file_path}", file_path)

        metadata = {
            "source": os.path.basename(file_path),
            "file_path": file_path,
            "ingestion_date": datetime.now().isoformat(),
            "file_size_kb": round(os.path.getsize(file_path) / 1024, 2),
            "extension": os.path.splitext(file_path)[1]
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
            self.logger.error(f"Error extracting internal metadata from {file_path}: {e}")
            metadata["total_pages"] = 0
            raise MetadataExtractionException(str(e), file_path) from e

        return metadata
