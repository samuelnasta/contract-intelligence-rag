from unittest.mock import MagicMock, patch
import pytest
import psycopg2

from src.DatabaseManager import DatabaseManager
from src.exceptions.DatabaseManagerException import (
    DatabaseConnectionException,
    IngestionRegistrationException,
    IngestionStatusUpdateException,
    DatabaseTableCreationException,
    IngestionTableCleanException
)


class TestDatabaseManagerConnection:
    """Test suite for DatabaseManager connection methods."""
    
    def test_database_manager_init(self):
        """Test DatabaseManager initialization."""
        db_manager = DatabaseManager()
        assert db_manager.logger is not None
        assert db_manager.conn_params is not None
        assert db_manager.conn_params["host"] == "localhost"
        assert db_manager.conn_params["database"] == "contract_rag"
        assert db_manager.conn_params["port"] == "5432"
    
    def test_get_connection_raises_exception_on_failure(self, database_manager_mock):
        """Test that _get_connection raises DatabaseConnectionException on failure."""
        database_manager_mock._get_connection.side_effect = psycopg2.Error("Connection failed")
        
        with pytest.raises(DatabaseConnectionException):
            # We need to test actual behavior, so we'll test with a fresh instance
            db = DatabaseManager()
            with patch('psycopg2.connect', side_effect=psycopg2.Error("Connection failed")):
                db._get_connection()


class TestDatabaseManagerTableCreation:
    """Test suite for table creation methods."""
    
    def test_create_ingestion_table_success(self, database_manager_mock):
        """Test successful table creation."""
        # Mock the connection and cursor
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        
        database_manager_mock._get_connection = MagicMock(return_value=mock_conn)
        
        # Should not raise exception
        database_manager_mock.create_ingestion_table()
        mock_cursor.execute.assert_called_once()
    
    def test_create_ingestion_table_error_handling(self):
        """Test that create_ingestion_table raises DatabaseTableCreationException on error."""
        db = DatabaseManager()
        with patch.object(db, '_get_connection', side_effect=Exception("Table creation failed")):
            with pytest.raises(DatabaseTableCreationException):
                db.create_ingestion_table()


class TestDatabaseManagerIngestionRegistration:
    """Test suite for ingestion registration methods."""
    
    def test_register_ingestion_new_file(self, database_manager_mock):
        """Test registering a new ingestion."""
        # Setup mocks
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        
        # Mock cursor context manager
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        
        # Mock connection context manager
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        
        # Mock cursor behavior
        mock_cursor.fetchone.side_effect = [None, (1,)]  # First: no existing hash, Second: return ID
        
        database_manager_mock._get_connection = MagicMock(return_value=mock_conn)
        
        result = database_manager_mock.register_ingestion(
            filename="test.pdf",
            file_hash="abc123",
            status="PROCESSING"
        )
        
        # Should return a document ID
        assert result == 1
    
    def test_register_ingestion_duplicate_file(self, database_manager_mock):
        """Test registering ingestion with existing hash returns -1."""
        # Setup mocks
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        
        # Mock cursor to return existing hash
        mock_cursor.fetchone.return_value = (1,)  # Hash already exists
        
        database_manager_mock._get_connection = MagicMock(return_value=mock_conn)
        
        result = database_manager_mock.register_ingestion(
            filename="test.pdf",
            file_hash="abc123",
            status="PROCESSING"
        )
        
        # Should return -1 for duplicate
        assert result == -1
    
    def test_register_ingestion_error_handling(self):
        """Test that register_ingestion raises IngestionRegistrationException on error."""
        db = DatabaseManager()
        with patch.object(db, '_get_connection', side_effect=Exception("Registration failed")):
            with pytest.raises(IngestionRegistrationException):
                db.register_ingestion("test.pdf", "hash123")


class TestDatabaseManagerStatusUpdate:
    """Test suite for status update methods."""
    
    def test_update_ingestion_status_success(self, database_manager_mock):
        """Test successful status update."""
        # Setup mocks
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        
        database_manager_mock._get_connection = MagicMock(return_value=mock_conn)
        
        # Should not raise exception
        database_manager_mock.update_ingestion_status(
            doc_id=1,
            status="SUCCESS",
            chunks_count=10
        )
        
        mock_cursor.execute.assert_called_once()
    
    def test_update_ingestion_status_with_error_message(self, database_manager_mock):
        """Test status update with error message."""
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        
        database_manager_mock._get_connection = MagicMock(return_value=mock_conn)
        
        database_manager_mock.update_ingestion_status(
            doc_id=1,
            status="FAILED",
            chunks_count=0,
            error_msg="Processing error"
        )
        
        mock_cursor.execute.assert_called_once()
    
    def test_update_ingestion_status_error_handling(self):
        """Test that update_ingestion_status raises IngestionStatusUpdateException on error."""
        db = DatabaseManager()
        with patch.object(db, '_get_connection', side_effect=Exception("Update failed")):
            with pytest.raises(IngestionStatusUpdateException):
                db.update_ingestion_status(doc_id=1, status="SUCCESS")


class TestDatabaseManagerTableClean:
    """Test suite for table cleaning methods."""
    
    def test_clean_ingestion_table_success(self, database_manager_mock):
        """Test successful table cleaning."""
        # Setup mocks
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        
        database_manager_mock._get_connection = MagicMock(return_value=mock_conn)
        
        # Should not raise exception
        database_manager_mock.clean_ingestion_table()
        
        mock_cursor.execute.assert_called_once()
    
    def test_clean_ingestion_table_error_handling(self):
        """Test that clean_ingestion_table raises IngestionTableCleanException on error."""
        db = DatabaseManager()
        with patch.object(db, '_get_connection', side_effect=Exception("Clean failed")):
            with pytest.raises(IngestionTableCleanException):
                db.clean_ingestion_table()


class TestDatabaseManagerIntegration:
    """Integration tests for DatabaseManager."""
    
    def test_database_manager_initialization_sets_correct_params(self):
        """Test that DatabaseManager properly initializes connection parameters."""
        db = DatabaseManager()
        
        assert db.conn_params["host"] == "localhost"
        assert db.conn_params["database"] == "contract_rag"
        assert db.conn_params["port"] == "5432"
        # User and password come from env variables
        assert isinstance(db.conn_params["user"], (str, type(None)))
        assert isinstance(db.conn_params["password"], (str, type(None)))
    
    def test_database_manager_workflow_sequence(self, database_manager_mock):
        """Test a typical workflow sequence."""
        # Setup mocks
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        
        database_manager_mock._get_connection = MagicMock(return_value=mock_conn)
        
        # Set up return values for sequence
        mock_cursor.fetchone.side_effect = [None, (1,)]  # For register_ingestion
        
        # Simulate workflow
        database_manager_mock.create_ingestion_table()
        doc_id = database_manager_mock.register_ingestion("test.pdf", "hash123")
        assert doc_id == 1
        
        database_manager_mock.update_ingestion_status(doc_id, "SUCCESS", chunks_count=5)
        database_manager_mock.clean_ingestion_table()
    
    def test_connection_parameters_from_environment(self):
        """Test that connection parameters respect environment variables."""
        import os
        original_user = os.environ.get('POSTGRES_USER')
        original_pass = os.environ.get('POSTGRES_PASSWORD')
        
        try:
            os.environ['POSTGRES_USER'] = 'test_user'
            os.environ['POSTGRES_PASSWORD'] = 'test_pass'
            
            db = DatabaseManager()
            assert db.conn_params['user'] == 'test_user'
            assert db.conn_params['password'] == 'test_pass'
        finally:
            # Restore original values
            if original_user:
                os.environ['POSTGRES_USER'] = original_user
            else:
                os.environ.pop('POSTGRES_USER', None)
            if original_pass:
                os.environ['POSTGRES_PASSWORD'] = original_pass
            else:
                os.environ.pop('POSTGRES_PASSWORD', None)
