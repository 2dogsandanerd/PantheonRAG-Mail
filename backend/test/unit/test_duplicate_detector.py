"""Unit tests for DuplicateDetector."""

import pytest
from src.services.duplicate_detector import DuplicateDetector


def test_check_duplicate_returns_none_for_new_file():
    """Test that new files are not marked as duplicates."""
    detector = DuplicateDetector()
    content = b"This is a test file"

    result = detector.check_duplicate(content)

    assert result is None


def test_check_duplicate_returns_filename_for_duplicate():
    """Test that duplicate files are detected."""
    detector = DuplicateDetector()
    content = b"This is a test file"
    filename = "test.pdf"

    # Register first
    detector.register_file_hash(content, filename)

    # Check for duplicate
    result = detector.check_duplicate(content)

    assert result == filename


def test_register_file_hash():
    """Test that file hashes are registered correctly."""
    detector = DuplicateDetector()
    content = b"Test content"
    filename = "document.pdf"

    detector.register_file_hash(content, filename)

    # Should be found as duplicate now
    assert detector.check_duplicate(content) == filename


def test_different_content_not_duplicate():
    """Test that different content is not marked as duplicate."""
    detector = DuplicateDetector()

    detector.register_file_hash(b"Content 1", "file1.pdf")
    result = detector.check_duplicate(b"Content 2")

    assert result is None


def test_clear_cache():
    """Test that cache clearing works."""
    detector = DuplicateDetector()

    detector.register_file_hash(b"Content", "file.pdf")
    detector.clear_cache()

    # Should not be found after clearing
    assert detector.check_duplicate(b"Content") is None


def test_get_stats():
    """Test statistics reporting."""
    detector = DuplicateDetector()

    detector.register_file_hash(b"Content 1", "file1.pdf")
    detector.register_file_hash(b"Content 2", "file2.pdf")

    stats = detector.get_stats()

    assert stats["total_files_registered"] == 2
