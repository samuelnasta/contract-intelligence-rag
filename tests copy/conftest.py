import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock
import pytest

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.DatabaseManager import DatabaseManager
from src.DocumentIngestor import DocumentIngestor
from src.QueryEngine import QueryEngine
from src.App import App
from src.Logger import get_logger


# ==================== FIXTURES FOR TextUtils ====================

@pytest.fixture
def sample_text():
    """Fixture providing sample text for cleaning tests."""
    return "This   is   a   test   with   multiple   spaces\n\nand   newlines."


@pytest.fixture
def cleaned_text():
    """Fixture providing expected cleaned text."""
    return "This is a test with multiple spaces and newlines."


@pytest.fixture
def temp_pdf_file():
    """Fixture providing a temporary PDF file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        # Write minimal PDF structure
        tmp.write(b'%PDF-1.4\n')
        tmp.write(b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n')
        tmp.write(b'2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n')
        tmp.write(b'3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n')
        tmp.write(b'xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n')
        tmp.write(b'trailer\n<< /Size 4 /Root 1 0 R >>\n')
        tmp.write(b'startxref\n200\n%%EOF\n')
        tmp_path = tmp.name
    
    yield tmp_path
    
    # Cleanup
    if os.path.exists(tmp_path):
        os.remove(tmp_path)


@pytest.fixture
def invalid_file_path():
    """Fixture providing path to non-existent file."""
    return "/tmp/nonexistent_file_12345.pdf"


@pytest.fixture
def invalid_format_file():
    """Fixture providing a non-PDF file."""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
        tmp.write(b"This is a text file, not a PDF")
        tmp_path = tmp.name
    
    yield tmp_path
    
    if os.path.exists(tmp_path):
        os.remove(tmp_path)


# ==================== FIXTURES FOR DocumentIngestor ====================

@pytest.fixture
def temp_directory():
    """Fixture providing a temporary directory for testing."""
    tmp_dir = tempfile.mkdtemp()
    yield tmp_dir
    
    # Cleanup
    import shutil
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)


@pytest.fixture
def document_ingestor(temp_pdf_file, temp_directory):
    """Fixture providing a DocumentIngestor instance."""
    # Mock the database manager to avoid actual DB calls
    ingestor = DocumentIngestor(file_path=temp_pdf_file, db_path=temp_directory)
    ingestor.db_manager = MagicMock()
    ingestor.db_manager.create_ingestion_table = MagicMock()
    ingestor.db_manager.clean_ingestion_table = MagicMock()
    ingestor.db_manager.register_ingestion = MagicMock(return_value=1)
    ingestor.db_manager.update_ingestion_status = MagicMock()
    return ingestor


# ==================== FIXTURES FOR App ====================

@pytest.fixture
def app_instance(temp_directory):
    """Fixture providing an App instance with temporary directories."""
    return App(raw_data_dir=temp_directory, db_path=os.path.join(temp_directory, "chroma"))


@pytest.fixture
def app_with_pdf_files(temp_directory):
    """Fixture providing an App instance with sample PDF files."""
    app = App(raw_data_dir=temp_directory, db_path=os.path.join(temp_directory, "chroma"))
    
    # Create sample PDF files
    for i in range(3):
        pdf_path = os.path.join(temp_directory, f"sample_{i}.pdf")
        with open(pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\ntrailer\n<< /Size 1 >>\nstartxref\n0\n%%EOF\n')
    
    return app


# ==================== FIXTURES FOR QueryEngine ====================

@pytest.fixture
def query_engine_mock():
    """Fixture providing a QueryEngine instance with mocked ChromaDB connection."""
    query_engine = QueryEngine(chroma_host="localhost", chroma_port=8001)
    query_engine.client = MagicMock()
    return query_engine


# ==================== FIXTURES FOR DatabaseManager ====================

@pytest.fixture
def database_manager_mock():
    """Fixture providing a DatabaseManager instance with mocked connection."""
    db_manager = DatabaseManager()
    db_manager._get_connection = MagicMock()
    return db_manager


# ==================== FIXTURES FOR JSON processed data ====================

@pytest.fixture
def processed_data_sample():
    """Fixture providing sample processed data."""
    return {
        "metadata": {
            "source": "sample.pdf",
            "ingestion_date": "2024-01-19T10:00:00.000000",
            "file_size_kb": 100.5,
            "author": "Test Author",
            "creator": "Test Creator",
            "creation_date": "2024-01-19",
            "total_pages": 5
        },
        "content_per_page": [
            {"page": 1, "content": "This is page 1 content"},
            {"page": 2, "content": "This is page 2 content"}
        ],
        "full_text_length": 45
    }


# ==================== LOGGER FIXTURE ====================

@pytest.fixture
def logger():
    """Fixture providing a logger instance."""
    return get_logger()
