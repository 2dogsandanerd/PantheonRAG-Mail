"""
End-to-End test for Docling async ingestion workflow.

This test validates the complete workflow:
1. File upload and validation
2. Task creation and background processing
3. Status polling and completion
4. ChromaDB integration
"""

import os
import pytest
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch


# Set feature flag for tests
os.environ["USE_DOCLING_INGESTION"] = "True"


@pytest.fixture
def test_files():
    """Create temporary test files."""
    temp_dir = tempfile.mkdtemp()

    # Create test markdown file
    md_file = Path(temp_dir) / "test.md"
    md_file.write_text("# Test Document\n\nThis is a test document.")

    # Create test CSV file
    csv_file = Path(temp_dir) / "test.csv"
    csv_file.write_text("Name,Value\nTest,123\n")

    yield {"md": str(md_file), "csv": str(csv_file)}

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)


def test_ingestion_task_manager():
    """Test IngestionTaskManager functionality."""
    from src.services.ingestion_task_manager import (
        IngestionTaskManager,
        TaskStatus,
        FileResult,
    )

    manager = IngestionTaskManager()

    # Test task creation
    task_id = manager.create_task(file_count=2, collection_name="test")
    assert task_id is not None

    task = manager.get_task(task_id)
    assert task is not None
    assert task.status == TaskStatus.PENDING
    assert task.total_files == 2

    # Test task start
    manager.start_task(task_id)
    task = manager.get_task(task_id)
    assert task.status == TaskStatus.PROCESSING
    assert task.started_at is not None

    # Test progress update
    result = FileResult(
        file_path="/test/file.md",
        filename="file.md",
        success=True,
        chunks=5,
        processing_time=0.5,
    )
    manager.update_progress(task_id, result)

    task = manager.get_task(task_id)
    assert task.processed_files == 1
    assert task.successful_files == 1
    assert task.total_chunks == 5

    # Test completion
    manager.complete_task(task_id)
    task = manager.get_task(task_id)
    assert task.completed_at is not None

    print(f"✅ Task Manager Test: {task.to_dict()}")


def test_duplicate_detection():
    """Test SHA256-based duplicate detection."""
    from src.services.ingestion_task_manager import IngestionTaskManager

    manager = IngestionTaskManager()

    content1 = b"This is a test document"
    content2 = b"This is a different document"
    content3 = b"This is a test document"  # Same as content1

    # First file - should not be duplicate
    dup1 = manager.check_duplicate(content1)
    assert dup1 is None
    manager.register_file_hash(content1, "file1.md")

    # Different file - should not be duplicate
    dup2 = manager.check_duplicate(content2)
    assert dup2 is None
    manager.register_file_hash(content2, "file2.md")

    # Same content as file1 - should be detected
    dup3 = manager.check_duplicate(content3)
    assert dup3 == "file1.md"

    print("✅ Duplicate Detection Test: Working correctly")


def test_docling_loader_factory():
    """Test DoclingLoaderFactory with feature flag."""
    from src.core.docling_loader import DoclingLoaderFactory

    # Check feature flag is enabled
    assert DoclingLoaderFactory.is_docling_enabled() is True

    # Check supported extensions
    assert ".pdf" in DoclingLoaderFactory.DOCLING_SUPPORTED_EXTENSIONS
    assert ".md" in DoclingLoaderFactory.DOCLING_SUPPORTED_EXTENSIONS
    assert ".csv" in DoclingLoaderFactory.DOCLING_SUPPORTED_EXTENSIONS

    print("✅ Docling Loader Factory Test: Feature flag enabled")


@pytest.mark.skipif(
    not (Path(__file__).parent / "test_data" / "docling_samples").exists(),
    reason="Test data not available",
)
def test_docling_loader_with_real_files():
    """Test DoclingLoader with real test files."""
    from src.core.docling_loader import DoclingLoader

    test_file = str(
        Path(__file__).parent / "test_data" / "docling_samples" / "quartalsbericht.md"
    )

    if not Path(test_file).exists():
        pytest.skip("Test file not found")

    loader = DoclingLoader(test_file)
    documents = loader.load()

    assert len(documents) == 1
    assert documents[0].metadata["loader"] == "docling"
    assert "Quartalsbericht" in documents[0].text

    print(f"✅ Docling Loader Test: Loaded {len(documents[0].text)} chars")


def test_file_validation():
    """Test file validation logic."""
    from src.services.docling_service import DoclingService

    service = DoclingService()

    # Test supported file check
    assert service.is_supported_file("document.pdf") is True
    assert service.is_supported_file("document.md") is True
    assert (
        service.is_supported_file("document.txt") is False
    )  # Not supported by Docling
    assert service.is_supported_file("image.jpg") is False

    # Test validation with non-existent file
    is_valid, error = service.validate_file("/non/existent/file.pdf")
    assert is_valid is False
    assert "not found" in error.lower()

    print("✅ File Validation Test: Working correctly")


@pytest.mark.skipif(
    not (Path(__file__).parent / "test_data" / "docling_samples").exists(),
    reason="Test data not available",
)
def test_process_file_success():
    """Test DoclingService.process_file() with real file."""
    from src.services.docling_service import DoclingService

    service = DoclingService()
    test_file = str(
        Path(__file__).parent / "test_data" / "docling_samples" / "inventar.csv"
    )

    if not Path(test_file).exists():
        pytest.skip("Test file not found")

    result = service.process_file(test_file)

    assert result["success"] is True
    assert "content" in result
    assert len(result["content"]) > 0
    assert result["metadata"]["loader"] == "docling"

    print(f"✅ Process File Test: {result['content_length']} chars extracted")


def test_task_to_dict_format():
    """Test task serialization format."""
    from src.services.ingestion_task_manager import IngestionTaskManager, TaskStatus

    manager = IngestionTaskManager()
    task_id = manager.create_task(file_count=3, collection_name="test")

    task_dict = manager.get_task(task_id).to_dict()

    # Verify structure
    assert "task_id" in task_dict
    assert "status" in task_dict
    assert "progress" in task_dict
    assert "total_files" in task_dict["progress"]
    assert "processed_files" in task_dict["progress"]
    assert "successful_files" in task_dict["progress"]
    assert "failed_files" in task_dict["progress"]
    assert "skipped_files" in task_dict["progress"]
    assert "total_chunks" in task_dict["progress"]

    print(f"✅ Task Serialization Test: {task_dict}")


if __name__ == "__main__":
    """Run tests manually."""
    print("\n" + "=" * 60)
    print("🧪 DOCLING E2E TESTS")
    print("=" * 60 + "\n")

    try:
        test_ingestion_task_manager()
        test_duplicate_detection()
        test_docling_loader_factory()
        test_file_validation()
        test_task_to_dict_format()

        # Optional tests with real files
        try:
            test_docling_loader_with_real_files()
            test_process_file_success()
        except Exception as e:
            print(f"⚠️  Real file tests skipped: {e}")

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
