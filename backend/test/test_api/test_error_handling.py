"""
Integration tests for the error handling system.

Tests custom exceptions, error responses, HTTP status codes, and logging.
Focus on core functionality rather than comprehensive endpoint coverage.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import logging

from src.main import app
from src.core.exceptions import (
    ValidationError,
    ChromaDBError,
    ServiceUnavailableError,
    DocumentNotFoundError,
    RAGFileNotFoundError,
    CollectionNotFoundError
)
from src.core.error_codes import ErrorCode, ServiceError


@pytest.fixture
def client():
    """Create test client with error handlers registered."""
    with TestClient(app) as test_client:
        yield test_client


class TestBaseException:
    """Test BaseRAGException functionality."""

    def test_exception_to_dict(self):
        """Test that exceptions convert to dict properly."""
        exc = ValidationError(
            "Test error",
            details={"field": "test", "value": 123}
        )

        result = exc.to_dict()

        assert "error" in result
        assert result["error"]["message"] == "Test error"
        assert result["error"]["code"] == ErrorCode.INVALID_INPUT.value
        assert result["error"]["details"]["field"] == "test"
        assert result["error"]["details"]["value"] == 123
        assert result["error"]["retryable"] is False

    def test_exception_status_code(self):
        """Test that exceptions return correct HTTP status codes."""
        # 400 - Bad Request
        val_err = ValidationError("Invalid input")
        assert val_err.status_code == 400

        # 404 - Not Found
        not_found = CollectionNotFoundError("missing")
        assert not_found.status_code == 404

        # 503 - Service Unavailable
        service_err = ServiceUnavailableError("ollama", "Down")
        assert service_err.status_code == 503

        chroma_err = ChromaDBError("Connection failed")
        assert chroma_err.status_code == 503

    def test_retryable_flags(self):
        """Test that retryable flags are set correctly."""
        # Not retryable
        val_err = ValidationError("Invalid")
        assert val_err.retryable is False

        not_found = RAGFileNotFoundError("/missing.pdf")
        assert not_found.retryable is False

        # Retryable
        service_err = ServiceUnavailableError("service", "Temp issue")
        assert service_err.retryable is True

        chroma_err = ChromaDBError("Timeout")
        assert chroma_err.retryable is True


class TestErrorResponseFormat:
    """Test that error responses have consistent JSON structure."""

    def test_validation_error_endpoint_response(self, client):
        """Test ValidationError returns proper JSON format in actual endpoint."""
        # POST to collections with invalid data should trigger validation
        response = client.post(
            "/api/v1/rag/collections",
            json={"name": "te st", "metadata": {}}  # Invalid name with space
        )

        # Response should be 400 or 422 (FastAPI validation)
        assert response.status_code in [400, 422]

        data = response.json()
        # Should have error structure (either custom or FastAPI)
        assert "error" in data or "detail" in data

    def test_chromadb_error_with_mock(self):
        """Test that ChromaDBError creates proper error structure."""
        error = ChromaDBError(
            "Connection timeout",
            details={"host": "localhost:8000", "timeout": 30}
        )

        result = error.to_dict()

        assert result["error"]["code"] == ErrorCode.CHROMADB_ERROR.value
        assert "Connection timeout" in result["error"]["message"]
        assert result["error"]["details"]["host"] == "localhost:8000"
        assert result["error"]["retryable"] is True


class TestHTTPStatusCodes:
    """Test HTTP status code mapping."""

    def test_error_code_to_status_mapping(self):
        """Test ERROR_STATUS_MAP contains expected mappings."""
        from src.core.error_codes import ERROR_STATUS_MAP

        # Check key mappings
        assert ERROR_STATUS_MAP[ErrorCode.INVALID_INPUT] == 400
        assert ERROR_STATUS_MAP[ErrorCode.FILE_NOT_FOUND] == 404
        assert ERROR_STATUS_MAP[ErrorCode.COLLECTION_NOT_FOUND] == 404
        assert ERROR_STATUS_MAP[ErrorCode.CHROMADB_ERROR] == 503
        assert ERROR_STATUS_MAP[ErrorCode.SERVICE_UNAVAILABLE] == 503
        assert ERROR_STATUS_MAP[ErrorCode.TIMEOUT_ERROR] == 504

    def test_validation_error_returns_400(self, client):
        """Test that validation errors return 400."""
        # Try to create collection with empty name
        response = client.post(
            "/api/v1/rag/collections",
            json={"name": "", "metadata": {}}
        )

        assert response.status_code in [400, 422]  # Either custom or FastAPI validation

    def test_health_endpoint_works(self, client):
        """Test that health endpoint works without errors."""
        response = client.get("/api/health")
        assert response.status_code == 200


class TestErrorDetails:
    """Test that error details contain useful information."""

    def test_file_not_found_includes_path(self):
        """Test RAGFileNotFoundError includes file path in details."""
        error = RAGFileNotFoundError("/path/to/missing/file.pdf")

        result = error.to_dict()

        assert result["error"]["details"]["file_path"] == "/path/to/missing/file.pdf"
        assert "/path/to/missing/file.pdf" in result["error"]["message"]

    def test_collection_not_found_includes_name(self):
        """Test CollectionNotFoundError includes collection name."""
        error = CollectionNotFoundError("missing_collection")

        result = error.to_dict()

        assert result["error"]["details"]["collection"] == "missing_collection"
        assert "missing_collection" in result["error"]["message"]

    def test_service_unavailable_includes_service_and_reason(self):
        """Test ServiceUnavailableError includes service name and reason."""
        error = ServiceUnavailableError(
            "ollama",
            "Failed to connect after 3 retries"
        )

        result = error.to_dict()

        assert result["error"]["details"]["service"] == "ollama"
        assert result["error"]["details"]["reason"] == "Failed to connect after 3 retries"
        assert "ollama" in result["error"]["message"]

    def test_validation_error_with_custom_details(self):
        """Test ValidationError can include arbitrary details."""
        error = ValidationError(
            "Embedding mismatch detected",
            details={
                "collection_model": "text-embedding-ada-002",
                "current_model": "all-MiniLM-L6-v2",
                "collection_dims": 1536,
                "current_dims": 384,
                "fix": "Change EMBEDDING_MODEL in .env to match collection"
            }
        )

        result = error.to_dict()

        assert result["error"]["details"]["collection_model"] == "text-embedding-ada-002"
        assert result["error"]["details"]["current_model"] == "all-MiniLM-L6-v2"
        assert result["error"]["details"]["collection_dims"] == 1536
        assert result["error"]["details"]["fix"] is not None


class TestExceptionTypes:
    """Test specific exception types."""

    def test_rag_file_not_found_error(self):
        """Test RAGFileNotFoundError."""
        error = RAGFileNotFoundError("/docs/manual.pdf")

        assert error.status_code == 404
        assert error.code == ErrorCode.FILE_NOT_FOUND
        assert error.retryable is False
        assert "/docs/manual.pdf" in error.message

    def test_collection_not_found_error(self):
        """Test CollectionNotFoundError."""
        error = CollectionNotFoundError("my_docs")

        assert error.status_code == 404
        assert error.code == ErrorCode.COLLECTION_NOT_FOUND
        assert error.retryable is False
        assert "my_docs" in error.message

    def test_document_not_found_error(self):
        """Test DocumentNotFoundError."""
        error = DocumentNotFoundError("doc_123", collection="my_collection")

        assert error.status_code == 404
        assert error.code == ErrorCode.DOCUMENT_NOT_FOUND
        assert error.retryable is False
        assert error.details["document_id"] == "doc_123"
        assert error.details["collection"] == "my_collection"

    def test_service_unavailable_error(self):
        """Test ServiceUnavailableError."""
        error = ServiceUnavailableError("chromadb", "Not responding")

        assert error.status_code == 503
        assert error.code == ErrorCode.SERVICE_UNAVAILABLE
        assert error.retryable is True
        assert "chromadb" in error.message
        assert "Not responding" in error.message

    def test_chromadb_error(self):
        """Test ChromaDBError."""
        error = ChromaDBError("Failed to connect to database")

        assert error.status_code == 503
        assert error.code == ErrorCode.CHROMADB_ERROR
        assert error.retryable is True
        assert "ChromaDB error" in error.message


class TestFastAPIIntegration:
    """Test FastAPI's built-in validation with our error handlers."""

    def test_missing_required_field_returns_error(self, client):
        """Test that missing required fields return validation error."""
        response = client.post(
            "/api/v1/rag/collections",
            json={"metadata": {}}  # Missing 'name' field
        )

        # Can be 400 (custom handler) or 422 (FastAPI default)
        assert response.status_code in [400, 422]
        data = response.json()
        # Should have error info (either custom or FastAPI format)
        assert "detail" in data or "error" in data

    def test_invalid_field_type_returns_error(self, client):
        """Test that invalid field types return validation error."""
        response = client.post(
            "/api/v1/rag/collections",
            json={"name": 12345, "metadata": {}}  # name should be string
        )

        # Can be 400 (custom handler) or 422 (FastAPI default)
        assert response.status_code in [400, 422]
        data = response.json()
        # Should have error info (either custom or FastAPI format)
        assert "detail" in data or "error" in data


class TestEndpointErrorHandling:
    """Test error handling in actual endpoints (smoke tests)."""

    def test_collections_endpoint_exists(self, client):
        """Test that collections endpoint exists and handles requests."""
        # GET collections - should work even if ChromaDB is down
        response = client.get("/api/v1/rag/collections")

        # Should return either 200 (success) or 503 (service unavailable)
        # but not crash with 500
        assert response.status_code in [200, 503]

        # Response should be valid JSON
        try:
            data = response.json()
            assert isinstance(data, (dict, list))
        except Exception:
            pytest.fail("Response is not valid JSON")

    def test_services_status_endpoint(self, client):
        """Test services status endpoint."""
        response = client.get("/api/v1/services/status")

        # Should return status (might be 503 if services are down)
        assert response.status_code in [200, 503]

        # Response should be valid JSON
        data = response.json()
        assert isinstance(data, dict)

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")

        # Health should always return 200
        assert response.status_code == 200

        data = response.json()
        assert "status" in data


class TestLoggingContext:
    """Test that errors are logged with proper context."""

    def test_exception_includes_details_for_logging(self):
        """Test that exceptions include details that would be useful in logs."""
        error = ValidationError(
            "Invalid file upload",
            details={
                "file_path": "/uploads/test.pdf",
                "file_size": 50 * 1024 * 1024,
                "max_size": 10 * 1024 * 1024,
                "user_id": "user_123"
            }
        )

        # Details should be accessible for logging
        assert error.details["file_path"] == "/uploads/test.pdf"
        assert error.details["file_size"] > error.details["max_size"]
        assert error.code == ErrorCode.INVALID_INPUT

    def test_exception_message_is_descriptive(self):
        """Test that exception messages are descriptive."""
        error1 = RAGFileNotFoundError("/documents/report.pdf")
        assert "File not found" in error1.message
        assert "/documents/report.pdf" in error1.message

        error2 = ChromaDBError("Connection refused")
        assert "ChromaDB error" in error2.message
        assert "Connection refused" in error2.message

        error3 = ServiceUnavailableError("ollama", "Model loading timeout")
        assert "ollama" in error3.message
        assert "Model loading timeout" in error3.message


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
