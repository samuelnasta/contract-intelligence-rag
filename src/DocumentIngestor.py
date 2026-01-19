import os 
import json
import hashlib
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from chromadb import HttpClient

from .exceptions.DocumentIngestorException import (
    DocumentLoadingException,
    DocumentSplittingException,
    VectorStorageException,
    SaveDataException)

from .Logger import get_logger
from .DatabaseManager import DatabaseManager
from .TextUtils import TextUtils

class DocumentIngestor:
    """Class for PDF reading, processing, and storage with embeddings and metadata tracking."""

    def __init__(self, file_path: str, db_path: str) -> None:
        """Initialize the DocumentIngestor with file path and database configuration.
        
        Args:
            file_path: Absolute or relative path to the PDF file to ingest.
            db_path: Path to the vector database directory for storing embeddings.
            
        Returns:
            None
            
        Raises:
            None (errors handled during run_ingestion)
        """
        self.logger = get_logger()
        self.file_path = file_path
        self.db_path = db_path
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.db_manager = DatabaseManager()

    def run_ingestion(self) -> None:
        """
        Run the complete document ingestion pipeline.
        
        Performs: PDF loading, text cleaning, chunking, embedding generation,
        and vector storage in Chroma database. Tracks progress in PostgreSQL.
        
        Args:
            None
            
        Returns:
            None
            
        Raises:
            DocumentLoadingException: If PDF loading fails.
            DocumentSplittingException: If text chunking fails.
            VectorStorageException: If embedding/storage fails.
            SaveDataException: If saving processed data to JSON fails.
        """
        # create the db if not exists
        self.db_manager.clean_ingestion_table() # TODO
        self.db_manager.create_ingestion_table()
        
        # create the file hasj
        file_hash = self._calculate_hash()
        doc_id = self.db_manager.register_ingestion(os.path.basename(self.file_path),
                                                    file_hash)

        if doc_id == -1:
            self.logger.warning(f"File already ingested (hash match): {self.file_path}")
            return
    
        # get the metadata
        custom_metadata = TextUtils.extract_metadata(self.file_path)
        self.logger.info(f"Extracted metadata: {custom_metadata}")

        # Load the PDF documents
        try:
            self.logger.info(f"Starting ingestion for {self.file_path}.")
            loader = PyPDFLoader(self.file_path)
            docs = loader.load()

            for doc in docs:
                doc.metadata.update(custom_metadata)
                doc.page_content = TextUtils.clean_text(doc.page_content)

            self.logger.info(f"Loaded {len(docs)} documents from {self.file_path}.")

        except Exception as e:
            self.logger.error(f"Error loading documents {self.file_path}: {e}")
            raise DocumentLoadingException(str(e), self.file_path) from e

        try:
            # Chunk the data. Transforming.
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
            chunks = text_splitter.split_documents(docs)
            self.logger.info(f"Split into {len(chunks)} chunks.")
            self.db_manager.update_ingestion_status(doc_id, "SUCCESS", chunks_count=len(chunks))

        except Exception as e:
            self.logger.error(f"Error splitting document {self.file_path}: {e}")
            self.db_manager.update_ingestion_status(doc_id, "FAILED", error_msg=str(e))
            raise DocumentSplittingException(str(e), self.file_path) from e
        
        # Save a copy to processed for auditing and re-ingestion
        self._save_processed_data(chunks, custom_metadata)

        try:
            self.logger.info("Generating embeddings and storing in vector database.")

            client = HttpClient(host="localhost", port=8001)

            chroma_db = Chroma(
                    client=client,
                    collection_name="documents",
                    embedding_function=self.embeddings
                )
            
            chroma_db.add_documents(documents=chunks)

            self.logger.info(f"Ingestion completed: {len(chunks)} chunks stored.")
            
        except Exception as e:
            self.logger.error(f"Error during embedding/storage for {self.file_path}: {e}")
            raise VectorStorageException(str(e)) from e


    def _save_processed_data(self, cleaned_docs: list, metadata: dict) -> str:
        """
        Save a checkpoint of the processed document to the processed folder.
        
        Stores cleaned document chunks and metadata as JSON for auditing
        and potential re-ingestion.
        
        Args:
            cleaned_docs: List of processed LangChain Document objects with cleaned content.
            metadata: Dictionary containing document metadata (title, date, etc.).
            
        Returns:
            str: Absolute path to the saved JSON file.
            
        Raises:
            SaveDataException: If file writing or directory creation fails.
        """
        base_name = os.path.basename(self.file_path)
        json_name = f"{os.path.splitext(base_name)[0]}.json"
        output_path = os.path.join("data/processed", json_name)

        processed_data = {
            "metadata": metadata,
            "content_per_page": [
                {"page": i + 1, "content": doc.page_content} 
                for i, doc in enumerate(cleaned_docs)
            ],
            "full_text_length": sum(len(doc.page_content) for doc in cleaned_docs)
        }

        try:
            os.makedirs("data/processed", exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=4)
            
            self.logger.info(f"Cleaned data stored in: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Could not store the processed data into JSON: {e}")
            raise SaveDataException(str(e)) from e
        

    def _calculate_hash(self):
        """
        Calculate SHA-256 hash of the file for deduplication purposes.
        
        Reads file in 4KB blocks to handle large files efficiently.
        
        Args:
            None
            
        Returns:
            str: Hexadecimal SHA-256 hash of the file.
            
        Raises:
            None (file reading errors propagate to caller)
        """
        sha256_hash = hashlib.sha256()
        with open(self.file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        file_hash = sha256_hash.hexdigest()
        self.logger.info(f"Calculated file hash: {file_hash}")
        return file_hash