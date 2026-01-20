import os
import psycopg2
from .Logger import get_logger

from .exceptions.DatabaseManagerException import (
    DatabaseConnectionException,
    IngestionRegistrationException,
    IngestionStatusUpdateException,
    DatabaseTableCreationException,
    IngestionTableCleanException
)


class DatabaseManager:
    """Manages database interactions for document ingestion tracking."""

    def __init__(self):
        """Initialize database manager with docker-compose parameters."""
        self.logger = get_logger()
        self.conn_params = {
            "host": "localhost",
            "database": "contract_rag",
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "port": "5432"
        }

    def _get_connection(self):
        """Establish and return a database connection."""
        try:
            return psycopg2.connect(**self.conn_params)
        except psycopg2.Error as e:
            self.logger.error(f"Failed to connect to database: {str(e)}")
            raise DatabaseConnectionException(str(e)) from e

    def create_ingestion_table(self):
        """Create document ingestion control table if it does not exist."""
        query = """
        CREATE TABLE IF NOT EXISTS document_ingestion (
            id SERIAL PRIMARY KEY,
            filename TEXT NOT NULL,
            file_hash TEXT UNIQUE,
            status TEXT,
            chunks_count INTEGER,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            error_message TEXT
        );
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    conn.commit()
            self.logger.info("Document ingestion table verified/created.")
        except DatabaseConnectionException:
            raise
        except Exception as e:
            self.logger.error(f"Error creating ingestion table: {str(e)}")
            raise DatabaseTableCreationException(str(e)) from e

    def register_ingestion(self, filename, file_hash, status="PROCESSING"):
        """
        Register the start of a document ingestion.
        
        Args:
            filename: Name of the file being ingested
            file_hash: Hash of the file for deduplication
            status: Initial status of the ingestion
            
        Returns:
            Document ID if successful, -1 if hash already exists
            
        Raises:
            IngestionRegistrationException: If registration fails
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Check if hash already exists
                    check_query = "SELECT id FROM document_ingestion WHERE file_hash = %s;"
                    cur.execute(check_query, (file_hash,))
                    existing = cur.fetchone()
                    
                    if existing:
                        self.logger.info(f"Hash already exists for file: {filename}. No ingestion needed.")
                        return -1
                    
                    # Hash doesn't exist, proceed with ingestion
                    query = """
                    INSERT INTO document_ingestion (filename, file_hash, status)
                    VALUES (%s, %s, %s) RETURNING id;
                    """
                    cur.execute(query, (filename, file_hash, status))
                    doc_id = cur.fetchone()[0]
                    conn.commit()
                    self.logger.info(f"Ingestion registered for file: {filename} with ID: {doc_id}")
                    return doc_id
        except DatabaseConnectionException:
            raise
        except Exception as e:
            self.logger.error(f"Error registering ingestion for file {filename}: {str(e)}")
            raise IngestionRegistrationException(str(e)) from e

    def update_ingestion_status(self, doc_id, status, chunks_count=0, error_msg=None):
        """
        Update the final status of the document ingestion.
        
        Args:
            doc_id: Document ID to update
            status: New status of the ingestion
            chunks_count: Number of chunks created
            error_msg: Error message if ingestion failed
            
        Raises:
            IngestionStatusUpdateException: If status update fails
        """
        query = """
        UPDATE document_ingestion 
        SET status = %s, chunks_count = %s, error_message = %s
        WHERE id = %s;
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (status, chunks_count, error_msg, doc_id))
                    conn.commit()
            self.logger.info(f"Ingestion status updated for document ID: {doc_id} to {status}")
        except DatabaseConnectionException:
            raise
        except Exception as e:
            self.logger.error(f"Error updating ingestion status for document ID {doc_id}: {str(e)}")
            raise IngestionStatusUpdateException(str(e)) from e

    def clean_ingestion_table(self):
        """
        Clean all records from the document ingestion table.
        
        Raises:
            IngestionTableCleanException: If cleanup fails
        """
        query = "DELETE FROM document_ingestion;"
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    conn.commit()
            self.logger.info("Document ingestion table cleaned successfully.")
        except DatabaseConnectionException:
            raise
        except Exception as e:
            self.logger.error(f"Error cleaning ingestion table: {str(e)}")
            raise IngestionTableCleanException(str(e)) from e
        