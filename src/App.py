import os
from typing import List

from .Logger import get_logger
from .DocumentIngestor import DocumentIngestor
from .exceptions import (
    DocumentLoadingException,
    DocumentSplittingException,
    VectorStorageException,
    SaveDataException
)


class App:
    """Main application class for Contract Intelligence RAG."""

    def __init__(self, raw_data_dir: str = "data/raw", db_path: str = "chroma/data"):
        """
        Initialize the App with configuration parameters.
        
        Args:
            raw_data_dir: Directory containing raw PDF files. Defaults to "data/raw".
            db_path: Path to the vector database directory. Defaults to "chroma/data".
            
        Returns:
            None
        """
        self.logger = get_logger()
        self.raw_data_dir = raw_data_dir
        self.db_path = db_path
        
        self.logger.info(f"Initialized App with raw_data_dir={raw_data_dir}, db_path={db_path}")

    def get_pdf_files(self) -> List[str]:
        """
        Get all PDF files from the raw data directory.
        
        Args:
            None
        
        Returns:
            List[str]: List of absolute paths to PDF files found in raw_data_dir.
            Returns empty list if directory doesn't exist.
        """
        if not os.path.exists(self.raw_data_dir):
            self.logger.error(f"Raw data directory not found: {self.raw_data_dir}")
            return []

        pdf_files = []
        for file in os.listdir(self.raw_data_dir):
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(self.raw_data_dir, file)
                pdf_files.append(full_path)
        
        self.logger.info(f"Found {len(pdf_files)} PDF file(s) in {self.raw_data_dir}")
        return pdf_files

    def process_document(self, file_path: str) -> bool:
        """
        Process a single document using DocumentIngestor.
        
        Args:
            file_path: Absolute or relative path to the PDF file to process.
            
        Returns:
            bool: True if ingestion completed successfully, False otherwise.
            
        Raises:
            None (exceptions are caught and logged internally)
        """
        try:
            self.logger.info(f"Starting processing for: {file_path}")
            ingestor = DocumentIngestor(file_path=file_path, db_path=self.db_path)
            ingestor.run_ingestion()
            self.logger.info(f"Successfully processed: {file_path}")
            return True
        except (DocumentLoadingException, DocumentSplittingException,
                VectorStorageException, SaveDataException) as e:
            self.logger.error(f"Error processing {file_path}: {e}")
            return False

    def run(self) -> None:
        """
        Main execution method that processes all PDF files in the raw data directory.
        
        Args:
            None
            
        Returns:
            None
            
        Raises:
            None (exceptions are logged, returns early if no files found)
        """
        self.logger.info("=" * 60)
        self.logger.info("Starting Contract Intelligence RAG Application")
        self.logger.info("=" * 60)
        
        # Get all PDF files
        pdf_files = self.get_pdf_files()
        
        if not pdf_files:
            self.logger.warning("No PDF files found in the raw data directory")
            return
        
        # Process each file
        successful = 0
        failed = 0
        
        for file_path in pdf_files:
            if self.process_document(file_path):
                successful += 1
            else:
                failed += 1
        
        # Summary
        self.logger.info("=" * 60)
        self.logger.info(f"Processing Complete - Success: {successful}, Failed: {failed}")
        self.logger.info("=" * 60)


def main():
    """
    Entry point for the application.
    
    Args:
        None
        
    Returns:
        None
        
    Raises:
        Exception: Propagates any critical errors encountered during execution.
    """
    try:
        app = App(raw_data_dir="data/raw", db_path="chroma/data")
        app.run()
    except Exception as e:
        logger = get_logger()
        logger.critical(f"Critical error in application: {e}")
        raise


if __name__ == "__main__":
    main()
