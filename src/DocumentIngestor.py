import os 
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


from .exceptions.DocumentIngestorException import (
    DocumentLoadingException,
    DocumentSplittingException,
    VectorStorageException,
    SaveDataException)

from .Logger import get_logger

from .TextUtils import TextUtils

class DocumentIngestor:
    """Clase for the PDF reading and storage."""

    def __init__(self, file_path: str, db_path: str) -> None:
        """Initialize the DocumentIngestor with the file path.
        Args:
            file_path: Path to the PDF file to ingest.
            db_path: Path to the vector database directory.
        """
        self.logger = get_logger()
        self.file_path = file_path
        self.db_path = db_path
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


    def run_ingestion(self) -> None:
        """
        Run the document ingestion process.

        """
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

        except Exception as e:
            self.logger.error(f"Error splitting document {self.file_path}: {e}")
            raise DocumentSplittingException(str(e), self.file_path) from e
        
        # Save a copy to processed for auditing and re-ingestion
        self._save_processed_data(chunks, custom_metadata)

        try:
            self.logger.info("Generating embeddings and storing in vector database.")
            # Store in vector database
            Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.db_path
            )
            self.logger.info(f"Ingestion completed: {len(chunks)} chunks stored.")
            
        except Exception as e:
            self.logger.error(f"Error during embedding/storage for {self.file_path}: {e}")
            raise VectorStorageException(str(e)) from e


    def _save_processed_data(self, cleaned_docs: list, metadata: dict) -> str:
        """
        Save a checkpoint of the processed document to the processed folder.
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
            self.logger.error(f"Couldn't store the processed data into json.: {e}")
            raise SaveDataException(str(e)) from e
        