import os
from unittest.mock import MagicMock, patch

from src.App import App


class TestAppInitialization:
    """Test suite for App initialization."""
    
    def test_app_init_default_params(self):
        """Test App initialization with default parameters."""
        app = App()
        assert app.raw_data_dir == "data/raw"
        assert app.db_path == "chroma/data"
        assert app.logger is not None
    
    def test_app_init_custom_params(self, temp_directory):
        """Test App initialization with custom parameters."""
        custom_raw = os.path.join(temp_directory, "custom_raw")
        custom_db = os.path.join(temp_directory, "custom_db")
        
        app = App(raw_data_dir=custom_raw, db_path=custom_db)
        assert app.raw_data_dir == custom_raw
        assert app.db_path == custom_db
    
    def test_app_stores_raw_data_dir(self, app_instance):
        """Test that App stores raw data directory."""
        assert app_instance.raw_data_dir is not None
        assert isinstance(app_instance.raw_data_dir, str)
    
    def test_app_stores_db_path(self, app_instance):
        """Test that App stores database path."""
        assert app_instance.db_path is not None
        assert isinstance(app_instance.db_path, str)
    
    def test_app_initializes_logger(self, app_instance):
        """Test that App initializes logger."""
        assert app_instance.logger is not None


class TestAppGetPDFFiles:
    """Test suite for get_pdf_files method."""
    
    def test_get_pdf_files_empty_directory(self, app_instance):
        """Test get_pdf_files with empty directory."""
        result = app_instance.get_pdf_files()
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_get_pdf_files_with_pdfs(self, app_with_pdf_files):
        """Test get_pdf_files finds PDF files."""
        result = app_with_pdf_files.get_pdf_files()
        assert isinstance(result, list)
        assert len(result) == 3
    
    def test_get_pdf_files_returns_absolute_paths(self, app_with_pdf_files):
        """Test that get_pdf_files returns absolute paths."""
        result = app_with_pdf_files.get_pdf_files()
        
        for path in result:
            assert os.path.isabs(path)
    
    def test_get_pdf_files_returns_only_pdfs(self, temp_directory):
        """Test that get_pdf_files returns only PDF files."""
        # Create mixed file types
        pdf_path = os.path.join(temp_directory, "document.pdf")
        txt_path = os.path.join(temp_directory, "readme.txt")
        doc_path = os.path.join(temp_directory, "document.docx")
        
        # Create files
        open(pdf_path, 'w').close()
        open(txt_path, 'w').close()
        open(doc_path, 'w').close()
        
        app = App(raw_data_dir=temp_directory, db_path=os.path.join(temp_directory, "db"))
        result = app.get_pdf_files()
        
        assert len(result) == 1
        assert result[0].endswith('.pdf')
    
    def test_get_pdf_files_nonexistent_directory(self):
        """Test get_pdf_files with non-existent directory."""
        app = App(raw_data_dir="/nonexistent/directory", db_path="db")
        result = app.get_pdf_files()
        
        assert result == []
    
    def test_get_pdf_files_returns_list(self, app_with_pdf_files):
        """Test that get_pdf_files always returns a list."""
        result = app_with_pdf_files.get_pdf_files()
        assert isinstance(result, list)
    
    def test_get_pdf_files_finds_multiple_pdfs(self, temp_directory):
        """Test finding multiple PDF files."""
        # Create multiple PDFs
        for i in range(5):
            pdf_path = os.path.join(temp_directory, f"document_{i}.pdf")
            open(pdf_path, 'w').close()
        
        app = App(raw_data_dir=temp_directory, db_path=os.path.join(temp_directory, "db"))
        result = app.get_pdf_files()
        
        assert len(result) == 5
    
    def test_get_pdf_files_case_insensitive(self, temp_directory):
        """Test that get_pdf_files finds PDFs regardless of case."""
        # Create PDFs with different cases
        paths = [
            os.path.join(temp_directory, "document.pdf"),
            os.path.join(temp_directory, "report.PDF"),
            os.path.join(temp_directory, "contract.Pdf")
        ]
        
        for path in paths:
            open(path, 'w').close()
        
        app = App(raw_data_dir=temp_directory, db_path=os.path.join(temp_directory, "db"))
        result = app.get_pdf_files()
        
        assert len(result) == 3


class TestAppProcessDocument:
    """Test suite for process_document method."""
    
    def test_process_document_returns_boolean(self, app_instance, temp_pdf_file):
        """Test that process_document returns a boolean."""
        with patch('src.App.DocumentIngestor') as mock_ingestor_class:
            mock_ingestor = MagicMock()
            mock_ingestor_class.return_value = mock_ingestor
            
            result = app_instance.process_document(temp_pdf_file)
            assert isinstance(result, bool)
    
    def test_process_document_success(self, app_instance, temp_pdf_file):
        """Test successful document processing."""
        with patch('src.App.DocumentIngestor') as mock_ingestor_class:
            mock_ingestor = MagicMock()
            mock_ingestor.run_ingestion = MagicMock()
            mock_ingestor_class.return_value = mock_ingestor
            
            result = app_instance.process_document(temp_pdf_file)
            
            assert result is True
            mock_ingestor.run_ingestion.assert_called_once()

    
    def test_process_document_creates_ingestor(self, app_instance, temp_pdf_file):
        """Test that process_document creates DocumentIngestor."""
        with patch('src.App.DocumentIngestor') as mock_ingestor_class:
            mock_ingestor = MagicMock()
            mock_ingestor_class.return_value = mock_ingestor
            
            app_instance.process_document(temp_pdf_file)
            
            # Verify DocumentIngestor was instantiated with correct parameters
            mock_ingestor_class.assert_called_once()
            call_kwargs = mock_ingestor_class.call_args.kwargs
            assert call_kwargs['file_path'] == temp_pdf_file
            assert call_kwargs['db_path'] == app_instance.db_path
    
    def test_process_document_calls_run_ingestion(self, app_instance, temp_pdf_file):
        """Test that process_document calls run_ingestion."""
        with patch('src.App.DocumentIngestor') as mock_ingestor_class:
            mock_ingestor = MagicMock()
            mock_ingestor_class.return_value = mock_ingestor
            
            app_instance.process_document(temp_pdf_file)
            
            mock_ingestor.run_ingestion.assert_called_once()


class TestAppRun:
    """Test suite for the main run method."""
    
    def test_app_run_empty_directory(self, app_instance):
        """Test run method with empty directory."""
        # Should complete without error
        app_instance.run()
    
    def test_app_run_with_pdfs(self, app_with_pdf_files):
        """Test run method with PDF files."""
        with patch.object(app_with_pdf_files, 'process_document', return_value=True):
            app_with_pdf_files.run()
            
            # process_document should be called for each PDF
            assert app_with_pdf_files.process_document.call_count == 3
    
    def test_app_run_processes_all_files(self, temp_directory):
        """Test that run method processes all PDF files."""
        # Create PDF files
        for i in range(3):
            pdf_path = os.path.join(temp_directory, f"doc_{i}.pdf")
            with open(pdf_path, 'wb') as f:
                f.write(b'%PDF-1.4\nendobj\nxref\ntrailer\nstartxref\n%%EOF\n')
        
        app = App(raw_data_dir=temp_directory, db_path=os.path.join(temp_directory, "db"))
        
        with patch.object(app, 'process_document', return_value=True) as mock_process:
            app.run()
            
            assert mock_process.call_count == 3
    
    def test_app_run_handles_failures(self, temp_directory):
        """Test that run method continues processing despite failures."""
        # Create PDF files
        for i in range(3):
            pdf_path = os.path.join(temp_directory, f"doc_{i}.pdf")
            with open(pdf_path, 'wb') as f:
                f.write(b'%PDF-1.4\nendobj\nxref\ntrailer\nstartxref\n%%EOF\n')
        
        app = App(raw_data_dir=temp_directory, db_path=os.path.join(temp_directory, "db"))
        
        # Mock some successes and some failures
        with patch.object(app, 'process_document', side_effect=[True, False, True]):
            app.run()
    
    def test_app_run_no_files_found(self, app_instance):
        """Test run with no PDF files."""
        # Directory is empty, should handle gracefully
        app_instance.run()


class TestAppIntegration:
    """Integration tests for App class."""
    
    def test_app_initialization_and_get_files(self, app_with_pdf_files):
        """Test initialization followed by getting PDF files."""
        app = app_with_pdf_files
        assert app.raw_data_dir is not None
        
        files = app.get_pdf_files()
        assert len(files) == 3
    
    def test_app_full_workflow(self, temp_directory):
        """Test complete App workflow."""
        # Create test PDFs
        for i in range(2):
            pdf_path = os.path.join(temp_directory, f"contract_{i}.pdf")
            with open(pdf_path, 'wb') as f:
                f.write(b'%PDF-1.4\nendobj\nxref\ntrailer\nstartxref\n%%EOF\n')
        
        app = App(raw_data_dir=temp_directory, db_path=os.path.join(temp_directory, "db"))
        
        # Verify initialization
        assert app.raw_data_dir == temp_directory
        
        # Get files
        files = app.get_pdf_files()
        assert len(files) == 2
        
        # Mock processing
        with patch.object(app, 'process_document', return_value=True):
            app.run()
    
    def test_app_with_multiple_operations(self, app_with_pdf_files):
        """Test multiple operations on App instance."""
        # Get files multiple times
        files1 = app_with_pdf_files.get_pdf_files()
        files2 = app_with_pdf_files.get_pdf_files()
        
        # Results should be consistent
        assert files1 == files2
        assert len(files1) == 3
    
    def test_app_configuration_persistence(self, temp_directory):
        """Test that App configuration persists across operations."""
        custom_raw = os.path.join(temp_directory, "raw")
        custom_db = os.path.join(temp_directory, "db")
        
        os.makedirs(custom_raw, exist_ok=True)
        
        app = App(raw_data_dir=custom_raw, db_path=custom_db)
        
        # Configuration should be accessible
        assert app.raw_data_dir == custom_raw
        assert app.db_path == custom_db
        
        # After operations
        app.get_pdf_files()
        
        # Configuration should remain the same
        assert app.raw_data_dir == custom_raw
        assert app.db_path == custom_db


class TestAppErrorHandling:
    """Test suite for error handling in App."""
    
    def test_app_with_invalid_paths(self):
        """Test App with invalid directory paths."""
        # Should initialize without error
        app = App(raw_data_dir="/invalid/path", db_path="/another/invalid/path")
        
        # get_pdf_files should return empty list
        files = app.get_pdf_files()
        assert files == []

    
    def test_app_run_continues_on_file_error(self, temp_directory):
        """Test that App.run continues processing despite file errors."""
        # Create multiple PDFs
        for i in range(3):
            pdf_path = os.path.join(temp_directory, f"doc_{i}.pdf")
            with open(pdf_path, 'wb') as f:
                f.write(b'%PDF-1.4\n')
        
        app = App(raw_data_dir=temp_directory, db_path=os.path.join(temp_directory, "db"))
        
        # Mock to return mix of successes and failures
        with patch.object(app, 'process_document', side_effect=[True, False, True, False]):
            # Should complete without raising exception
            app.run()
            
