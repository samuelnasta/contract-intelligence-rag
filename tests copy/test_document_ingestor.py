import os
import json
from unittest.mock import MagicMock, patch
import pytest

from src.DocumentIngestor import DocumentIngestor
from src.exceptions.DocumentIngestorException import SaveDataException


class TestDocumentIngestorInitialization:
    """Test suite for DocumentIngestor initialization."""
    
    def test_document_ingestor_init(self, document_ingestor):
        """Test DocumentIngestor initialization."""
        assert document_ingestor.file_path is not None
        assert document_ingestor.db_path is not None
        assert document_ingestor.logger is not None
        assert document_ingestor.embeddings is not None
        assert document_ingestor.db_manager is not None
    
    def test_document_ingestor_stores_file_path(self, temp_pdf_file, temp_directory):
        """Test that DocumentIngestor stores the file path."""
        ingestor = DocumentIngestor(file_path=temp_pdf_file, db_path=temp_directory)
        assert ingestor.file_path == temp_pdf_file
    
    def test_document_ingestor_stores_db_path(self, temp_pdf_file, temp_directory):
        """Test that DocumentIngestor stores the database path."""
        ingestor = DocumentIngestor(file_path=temp_pdf_file, db_path=temp_directory)
        assert ingestor.db_path == temp_directory
    
    def test_document_ingestor_has_embeddings(self, document_ingestor):
        """Test that DocumentIngestor initializes embeddings."""
        assert document_ingestor.embeddings is not None
        # Check that it has the expected model
        assert hasattr(document_ingestor.embeddings, 'model_name')


class TestDocumentIngestorCalculateHash:
    """Test suite for document hashing."""
    
    def test_calculate_hash_returns_string(self, document_ingestor):
        """Test that _calculate_hash returns a string."""
        result = document_ingestor._calculate_hash()
        assert isinstance(result, str)
    
    def test_calculate_hash_is_hex_string(self, document_ingestor):
        """Test that hash is hexadecimal."""
        result = document_ingestor._calculate_hash()
        # Should be valid hex
        try:
            int(result, 16)
            is_hex = True
        except ValueError:
            is_hex = False
        assert is_hex
    
    def test_calculate_hash_consistent(self, document_ingestor):
        """Test that hash is consistent for same file."""
        hash1 = document_ingestor._calculate_hash()
        hash2 = document_ingestor._calculate_hash()
        assert hash1 == hash2
    
    def test_calculate_hash_correct_length(self, document_ingestor):
        """Test that SHA-256 hash has correct length (64 hex characters)."""
        result = document_ingestor._calculate_hash()
        assert len(result) == 64  # SHA-256 produces 64 hex characters


class TestDocumentIngestorSaveProcessedData:
    """Test suite for saving processed data."""
    
    def test_save_processed_data_creates_json_file(self, document_ingestor, temp_directory):
        """Test that _save_processed_data creates a JSON file."""
        # Mock document objects
        mock_doc1 = MagicMock()
        mock_doc1.page_content = "This is page 1 content"
        
        mock_doc2 = MagicMock()
        mock_doc2.page_content = "This is page 2 content"
        
        metadata = {
            "source": "test.pdf",
            "ingestion_date": "2024-01-19",
            "file_size_kb": 100.0
        }
        
        # Change directory to temp for this test
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_directory)
            result = document_ingestor._save_processed_data([mock_doc1, mock_doc2], metadata)
            
            # Check file exists
            assert os.path.exists(result)
            assert result.endswith('.json')
        finally:
            os.chdir(original_cwd)
    
    def test_save_processed_data_json_structure(self, document_ingestor, temp_directory):
        """Test that saved JSON has correct structure."""
        mock_doc = MagicMock()
        mock_doc.page_content = "Test content"
        
        metadata = {"source": "test.pdf", "author": "Test"}
        
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_directory)
            result = document_ingestor._save_processed_data([mock_doc], metadata)
            
            with open(result, 'r') as f:
                data = json.load(f)
            
            # Check structure
            assert "metadata" in data
            assert "content_per_page" in data
            assert "full_text_length" in data
            assert data["metadata"] == metadata
        finally:
            os.chdir(original_cwd)
    
    def test_save_processed_data_contains_content_per_page(self, document_ingestor, temp_directory):
        """Test that saved data contains content per page."""
        mock_doc1 = MagicMock()
        mock_doc1.page_content = "Page 1"
        
        mock_doc2 = MagicMock()
        mock_doc2.page_content = "Page 2"
        
        metadata = {"source": "test.pdf"}
        
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_directory)
            result = document_ingestor._save_processed_data([mock_doc1, mock_doc2], metadata)
            
            with open(result, 'r') as f:
                data = json.load(f)
            
            # Check content per page
            assert len(data["content_per_page"]) == 2
            assert data["content_per_page"][0]["page"] == 1
            assert data["content_per_page"][1]["page"] == 2
        finally:
            os.chdir(original_cwd)
    
    def test_save_processed_data_calculates_text_length(self, document_ingestor, temp_directory):
        """Test that full_text_length is calculated correctly."""
        mock_doc = MagicMock()
        mock_doc.page_content = "Test content"
        
        metadata = {"source": "test.pdf"}
        
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_directory)
            result = document_ingestor._save_processed_data([mock_doc], metadata)
            
            with open(result, 'r') as f:
                data = json.load(f)
            
            # Check text length
            assert data["full_text_length"] == len("Test content")
        finally:
            os.chdir(original_cwd)
    
    def test_save_processed_data_returns_path(self, document_ingestor, temp_directory):
        """Test that _save_processed_data returns the file path."""
        mock_doc = MagicMock()
        mock_doc.page_content = "Content"
        
        metadata = {"source": "test.pdf"}
        
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_directory)
            result = document_ingestor._save_processed_data([mock_doc], metadata)
            assert isinstance(result, str)
            assert "data/processed" in result
        finally:
            os.chdir(original_cwd)
    
    def test_save_processed_data_creates_directory(self, document_ingestor, temp_directory):
        """Test that _save_processed_data creates data/processed directory."""
        mock_doc = MagicMock()
        mock_doc.page_content = "Content"
        
        metadata = {"source": "test.pdf"}
        
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_directory)
            document_ingestor._save_processed_data([mock_doc], metadata)
            
            # Check directory was created
            assert os.path.exists("data/processed")
            assert os.path.isdir("data/processed")
        finally:
            os.chdir(original_cwd)
    
    def test_save_processed_data_error_raises_exception(self, document_ingestor):
        """Test that SaveDataException is raised on write error."""
        mock_doc = MagicMock()
        mock_doc.page_content = "Content"
        
        metadata = {"source": "test.pdf"}
        
        with patch('builtins.open', side_effect=IOError("Cannot write file")):
            with pytest.raises(SaveDataException):
                document_ingestor._save_processed_data([mock_doc], metadata)


class TestDocumentIngestorIntegration:
    """Integration tests for DocumentIngestor."""
    
    def test_document_ingestor_initialization_complete(self, document_ingestor):
        """Test complete initialization of DocumentIngestor."""
        # Verify all components are initialized
        assert document_ingestor.logger is not None
        assert document_ingestor.file_path is not None
        assert document_ingestor.db_path is not None
        assert document_ingestor.embeddings is not None
        assert document_ingestor.db_manager is not None
    
    def test_document_ingestor_hash_calculation_flow(self, document_ingestor):
        """Test hash calculation in context of document ingestor."""
        # Hash should be calculated from the PDF file
        hash_value = document_ingestor._calculate_hash()
        
        # Should be a valid SHA-256 hex string
        assert len(hash_value) == 64
        assert isinstance(hash_value, str)
    
    def test_document_ingestor_with_different_file_paths(self, temp_pdf_file, temp_directory):
        """Test DocumentIngestor initialization with different file paths."""
        ingestor1 = DocumentIngestor(file_path=temp_pdf_file, db_path=temp_directory)
        
        # Create another temp PDF
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'%PDF-1.4\nendobj\nxref\ntrailer\nstartxref\n%%EOF\n')
            tmp_path = tmp.name
        
        try:
            ingestor2 = DocumentIngestor(file_path=tmp_path, db_path=temp_directory)
            
            # Both should be properly initialized
            assert ingestor1.file_path == temp_pdf_file
            assert ingestor2.file_path == tmp_path
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class TestDocumentIngestorErrorHandling:
    """Test suite for error handling in DocumentIngestor."""
    
    def test_document_ingestor_with_nonexistent_file(self, temp_directory):
        """Test DocumentIngestor with non-existent file."""
        # Should initialize without error, but fail during run_ingestion
        ingestor = DocumentIngestor(
            file_path="/nonexistent/file.pdf",
            db_path=temp_directory
        )
        assert ingestor.file_path == "/nonexistent/file.pdf"
    
    def test_save_processed_data_with_empty_documents(self, document_ingestor, temp_directory):
        """Test saving processed data with empty document list."""
        metadata = {"source": "test.pdf"}
        
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_directory)
            result = document_ingestor._save_processed_data([], metadata)
            
            with open(result, 'r') as f:
                data = json.load(f)
            
            assert data["full_text_length"] == 0
            assert len(data["content_per_page"]) == 0
        finally:
            os.chdir(original_cwd)
