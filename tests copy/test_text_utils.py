import os
import pytest
from src.TextUtils import TextUtils
from src.exceptions.UtilsException import MetadataExtractionException, InvalidFileFormatException


class TestTextUtilsCleanText:
    """Test suite for TextUtils.clean_text method."""
    
    def test_clean_text_removes_multiple_spaces(self, sample_text):
        """Test that clean_text removes multiple consecutive spaces."""
        result = TextUtils.clean_text(sample_text)
        assert "   " not in result
        assert result.count(" ") <= sample_text.count(" ")
    
    def test_clean_text_removes_newlines(self, sample_text):
        """Test that clean_text removes newlines."""
        result = TextUtils.clean_text(sample_text)
        assert "\n" not in result
    
    def test_clean_text_strips_whitespace(self):
        """Test that clean_text strips leading/trailing whitespace."""
        text = "   text with spaces   "
        result = TextUtils.clean_text(text)
        assert result == result.strip()
        assert result[0] != " "
        assert result[-1] != " "
    
    def test_clean_text_expected_output(self, sample_text, cleaned_text):
        """Test clean_text produces expected output."""
        result = TextUtils.clean_text(sample_text)
        assert result == cleaned_text
    
    def test_clean_text_empty_string(self):
        """Test clean_text with empty string."""
        result = TextUtils.clean_text("")
        assert result == ""
    
    def test_clean_text_only_whitespace(self):
        """Test clean_text with only whitespace."""
        result = TextUtils.clean_text("   \n\n   ")
        assert result == ""
    
    def test_clean_text_single_word(self):
        """Test clean_text with single word."""
        result = TextUtils.clean_text("hello")
        assert result == "hello"


class TestTextUtilsExtractMetadata:
    """Test suite for TextUtils.extract_metadata method."""
    
    def test_extract_metadata_valid_pdf(self, temp_pdf_file):
        """Test extracting metadata from valid PDF file."""
        metadata = TextUtils.extract_metadata(temp_pdf_file)
        
        # Verify required keys exist
        assert "source" in metadata
        assert "ingestion_date" in metadata
        assert "file_size_kb" in metadata
    
    def test_extract_metadata_source_is_filename(self, temp_pdf_file):
        """Test that extracted source is the filename."""
        metadata = TextUtils.extract_metadata(temp_pdf_file)
        filename = os.path.basename(temp_pdf_file)
        assert metadata["source"] == filename
    
    def test_extract_metadata_file_size_positive(self, temp_pdf_file):
        """Test that extracted file size is positive."""
        metadata = TextUtils.extract_metadata(temp_pdf_file)
        assert metadata["file_size_kb"] > 0
    
    def test_extract_metadata_ingestion_date_iso_format(self, temp_pdf_file):
        """Test that ingestion_date is in ISO format."""
        metadata = TextUtils.extract_metadata(temp_pdf_file)
        # ISO format should contain T and numbers
        assert "T" in metadata["ingestion_date"]
    
    def test_extract_metadata_nonexistent_file(self, invalid_file_path):
        """Test that MetadataExtractionException is raised for non-existent file."""
        with pytest.raises(MetadataExtractionException):
            TextUtils.extract_metadata(invalid_file_path)
    
    def test_extract_metadata_invalid_format(self, invalid_format_file):
        """Test that InvalidFileFormatException is raised for non-PDF file."""
        with pytest.raises(InvalidFileFormatException):
            TextUtils.extract_metadata(invalid_format_file)
    
    def test_extract_metadata_directory_raises_exception(self, temp_directory):
        """Test that MetadataExtractionException is raised when path is directory."""
        with pytest.raises(MetadataExtractionException):
            TextUtils.extract_metadata(temp_directory)
    
    def test_extract_metadata_returns_dict(self, temp_pdf_file):
        """Test that extract_metadata returns a dictionary."""
        result = TextUtils.extract_metadata(temp_pdf_file)
        assert isinstance(result, dict)
    
    def test_extract_metadata_error_code_in_exception(self, invalid_file_path):
        """Test that exception contains proper error code."""
        try:
            TextUtils.extract_metadata(invalid_file_path)
        except MetadataExtractionException as e:
            assert e.error_code == "METADATA_ERROR"
    
    def test_extract_metadata_invalid_format_error_code(self, invalid_format_file):
        """Test that invalid format exception contains proper error code."""
        try:
            TextUtils.extract_metadata(invalid_format_file)
        except InvalidFileFormatException as e:
            assert e.error_code == "INVALID_FILE_FORMAT"


class TestTextUtilsIntegration:
    """Integration tests for TextUtils."""
    
    def test_clean_text_and_extract_metadata_together(self, temp_pdf_file, sample_text):
        """Test using clean_text and extract_metadata together."""
        # Get metadata
        metadata = TextUtils.extract_metadata(temp_pdf_file)
        assert "source" in metadata
        
        # Clean text
        cleaned = TextUtils.clean_text(sample_text)
        assert isinstance(cleaned, str)
    
    def test_metadata_has_all_required_fields(self, temp_pdf_file):
        """Test that metadata contains all required fields."""
        metadata = TextUtils.extract_metadata(temp_pdf_file)
        required_fields = ["source", "ingestion_date", "file_size_kb"]
        
        for field in required_fields:
            assert field in metadata, f"Missing field: {field}"
    
    def test_clean_text_multiple_calls_consistent(self, sample_text):
        """Test that clean_text produces consistent results on multiple calls."""
        result1 = TextUtils.clean_text(sample_text)
        result2 = TextUtils.clean_text(sample_text)
        assert result1 == result2
