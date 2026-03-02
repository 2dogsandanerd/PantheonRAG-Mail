"""
Integration tests for Docling document processing.

Tests cover:
1. DoclingLoader functionality
2. DoclingService validation and processing
3. Feature flag integration with RAG client
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data" / "docling_samples"


class TestDoclingLoader:
    """Test suite for DoclingLoader."""

    def test_loader_initialization(self):
        """Test DoclingLoader can be initialized with valid file."""
        from src.core.docling_loader import DoclingLoader

        # Use a real test file
        test_file = TEST_DATA_DIR / "quartalsbericht.md"

        if not test_file.exists():
            pytest.skip("Test data not available")

        loader = DoclingLoader(str(test_file))
        assert loader.file_path.exists()
        assert loader.file_path.name == "quartalsbericht.md"

    def test_loader_file_not_found(self):
        """Test DoclingLoader raises error for non-existent file."""
        from src.core.docling_loader import DoclingLoader

        with pytest.raises(FileNotFoundError):
            DoclingLoader("/non/existent/file.pdf")

    @pytest.mark.skipif(
        not (TEST_DATA_DIR / "quartalsbericht.md").exists(),
        reason="Test data not available"
    )
    def test_loader_load_markdown(self):
        """Test loading markdown file with DoclingLoader."""
        from src.core.docling_loader import DoclingLoader

        test_file = TEST_DATA_DIR / "quartalsbericht.md"
        loader = DoclingLoader(str(test_file))
        documents = loader.load()

        assert len(documents) == 1
        assert documents[0].text is not None
        assert len(documents[0].text) > 0
        assert documents[0].metadata["loader"] == "docling"
        assert documents[0].metadata["source_file_path"] == str(test_file)

    @pytest.mark.skipif(
        not (TEST_DATA_DIR / "inventar.csv").exists(),
        reason="Test data not available"
    )
    def test_loader_load_csv(self):
        """Test loading CSV file with DoclingLoader."""
        from src.core.docling_loader import DoclingLoader

        test_file = TEST_DATA_DIR / "inventar.csv"
        loader = DoclingLoader(str(test_file))
        documents = loader.load()

        assert len(documents) == 1
        assert documents[0].text is not None
        assert documents[0].metadata["file_type"] == ".csv"


class TestDoclingLoaderFactory:
    """Test suite for DoclingLoaderFactory."""

    def test_docling_disabled_returns_legacy_loader(self):
        """Test factory returns legacy loader when Docling disabled."""
        from src.core.docling_loader import DoclingLoaderFactory

        with patch.dict(os.environ, {"USE_DOCLING_INGESTION": "False"}):
            # Create temp PDF file for testing
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                temp_pdf = f.name

            try:
                loader = DoclingLoaderFactory.create_loader(temp_pdf)
                # Should be PDFReader (LlamaIndex default)
                assert loader.__class__.__name__ == "PDFReader"
            finally:
                os.unlink(temp_pdf)

    def test_docling_enabled_returns_docling_loader(self):
        """Test factory returns DoclingLoader when Docling enabled."""
        from src.core.docling_loader import DoclingLoaderFactory

        with patch.dict(os.environ, {"USE_DOCLING_INGESTION": "True"}):
            # Create temp PDF file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                temp_pdf = f.name

            try:
                loader = DoclingLoaderFactory.create_loader(temp_pdf)
                assert loader.__class__.__name__ == "DoclingLoader"
            finally:
                os.unlink(temp_pdf)

    def test_txt_file_uses_text_loader(self):
        """Test that .txt files use TextLoader (not Docling)."""
        from src.core.docling_loader import DoclingLoaderFactory

        with patch.dict(os.environ, {"USE_DOCLING_INGESTION": "True"}):
            # Create temp TXT file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
                temp_txt = f.name

            try:
                loader = DoclingLoaderFactory.create_loader(temp_txt)
                # Even with Docling enabled, TXT should use SingleFileWrapper (LlamaIndex default)
                assert loader.__class__.__name__ == "SingleFileWrapper"
            finally:
                os.unlink(temp_txt)


class TestDoclingService:
    """Test suite for DoclingService."""

    def test_service_initialization(self):
        """Test DoclingService can be initialized."""
        from src.services.docling_service import DoclingService

        service = DoclingService()
        assert service is not None
        assert service.SUPPORTED_EXTENSIONS is not None

    def test_supported_file_check(self):
        """Test is_supported_file method."""
        from src.services.docling_service import DoclingService

        service = DoclingService()

        assert service.is_supported_file("document.pdf") is True
        assert service.is_supported_file("document.docx") is True
        assert service.is_supported_file("document.md") is True
        assert service.is_supported_file("document.csv") is True
        assert service.is_supported_file("document.txt") is False  # Not supported!
        assert service.is_supported_file("document.jpg") is False

    def test_validate_file_not_found(self):
        """Test validation fails for non-existent file."""
        from src.services.docling_service import DoclingService

        service = DoclingService()
        is_valid, error = service.validate_file("/non/existent/file.pdf")

        assert is_valid is False
        assert "not found" in error.lower()

    @pytest.mark.skipif(
        not (TEST_DATA_DIR / "quartalsbericht.md").exists(),
        reason="Test data not available"
    )
    def test_validate_file_success(self):
        """Test validation succeeds for valid file."""
        from src.services.docling_service import DoclingService

        service = DoclingService()
        test_file = TEST_DATA_DIR / "quartalsbericht.md"
        is_valid, error = service.validate_file(str(test_file))

        assert is_valid is True
        assert error == ""

    @pytest.mark.skipif(
        not (TEST_DATA_DIR / "quartalsbericht.md").exists(),
        reason="Test data not available"
    )
    @pytest.mark.asyncio
    async def test_process_file_success(self):
        """Test processing a valid file."""
        from src.services.docling_service import DoclingService

        service = DoclingService()
        test_file = TEST_DATA_DIR / "quartalsbericht.md"
        result = await service.process_file(str(test_file))

        assert result["success"] is True
        assert "content" in result
        assert len(result["content"]) > 0
        assert result["metadata"]["loader"] == "docling"


class TestRAGClientIntegration:
    """Test RAG service integration with Docling."""

    @pytest.mark.asyncio
    async def test_rag_service_uses_docling_when_enabled(self):
        """Test that RAG service uses Docling when feature flag is enabled."""
        from src.services.external_rag_connector import get_rag_service
        # This is an integration test - would require full RAG setup
        # Marking as TODO for now
        pytest.skip("Full integration test - requires RAG service setup")

    @pytest.mark.asyncio
    async def test_rag_service_uses_legacy_when_disabled(self):
        """Test that RAG service uses legacy loaders when Docling disabled."""
        pytest.skip("Full integration test - requires RAG service setup")


# Pytest fixtures for test data
@pytest.fixture
def test_markdown_file():
    """Provide path to test markdown file."""
    path = TEST_DATA_DIR / "quartalsbericht.md"
    if path.exists():
        return str(path)
    else:
        pytest.skip("Test data not available")


@pytest.fixture
def test_csv_file():
    """Provide path to test CSV file."""
    path = TEST_DATA_DIR / "inventar.csv"
    if path.exists():
        return str(path)
    else:
        pytest.skip("Test data not available")
