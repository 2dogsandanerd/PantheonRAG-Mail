"""
E2E Test Configuration and Fixtures

This module provides fixtures for E2E testing with real services.
"""

import pytest
import asyncio
import httpx
from pathlib import Path
import tempfile
import shutil
from typing import AsyncGenerator, Generator
import time
import os

# Test Configuration
TEST_BASE_URL = "http://localhost:33801"
TEST_API_URL = f"{TEST_BASE_URL}/api/v1"

# GreenMail Test Configuration (must match docker-compose.e2e.yml)
IMAP_HOST = "localhost"
IMAP_PORT = 3143
SMTP_HOST = "localhost"
SMTP_PORT = 3025
TEST_EMAIL_USER = "test@example.com"
TEST_EMAIL_PASS = "testpass"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide an async HTTP client for API testing."""
    async with httpx.AsyncClient(base_url=TEST_API_URL, timeout=30.0) as client:
        yield client


@pytest.fixture
async def http_client_sync():
    """Provide a sync HTTP client for simpler tests."""
    with httpx.Client(base_url=TEST_API_URL, timeout=30.0) as client:
        yield client


@pytest.fixture
def test_data_dir() -> Path:
    """Return the path to test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    tmp_path = Path(tempfile.mkdtemp(prefix="mailmodul_e2e_"))
    yield tmp_path
    # Cleanup
    shutil.rmtree(tmp_path, ignore_errors=True)


@pytest.fixture
def sample_pdf_path(test_data_dir: Path) -> Path:
    """Return path to sample PDF file."""
    pdf_path = test_data_dir / "sample.pdf"
    if not pdf_path.exists():
        pytest.skip(f"Sample PDF not found at {pdf_path}")
    return pdf_path


@pytest.fixture
def sample_txt_path(test_data_dir: Path) -> Path:
    """Return path to sample text file."""
    txt_path = test_data_dir / "sample.txt"
    if not txt_path.exists():
        pytest.skip(f"Sample TXT not found at {txt_path}")
    return txt_path


@pytest.fixture(scope="module")
def ensure_services():
    """Ensure all required services are running before running tests."""
    import requests

    services_to_check = [
        ("Backend API", f"{TEST_BASE_URL}/api/health"),
    ]

    failed = []
    for name, url in services_to_check:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                failed.append(f"{name}: HTTP {response.status_code}")
        except Exception as e:
            failed.append(f"{name}: {e}")

    if failed:
        pytest.skip(f"Required services not available: {', '.join(failed)}")


@pytest.fixture
def wait_for_processing():
    """Helper to wait for async processing."""

    async def _wait(seconds: float = 2.0):
        await asyncio.sleep(seconds)

    return _wait


@pytest.fixture
def generate_unique_id():
    """Generate unique IDs for test resources."""
    return lambda prefix: f"{prefix}_{int(time.time())}_{os.getpid()}"


# RAG-specific fixtures
@pytest.fixture
async def test_collection(http_client: httpx.AsyncClient, generate_unique_id) -> str:
    """Create a test collection and return its name."""
    collection_name = generate_unique_id("test_collection")

    # Create collection via API
    response = await http_client.post(
        "/api/v1/rag/collections", data={"collection_name": collection_name}
    )

    if response.status_code != 200:
        pytest.skip(f"Failed to create test collection: {response.text}")

    yield collection_name

    # Cleanup: delete collection
    try:
        await http_client.delete(f"/api/v1/rag/collections/{collection_name}")
    except:
        pass  # Ignore cleanup errors


# Email-specific fixtures
@pytest.fixture
async def imap_client():
    """Provide a connected IMAP client for GreenMail."""
    from src.core.email_clients.imap_client import IMAPClient

    config = {
        "EMAIL_USER": TEST_EMAIL_USER,
        "EMAIL_PASSWORD": TEST_EMAIL_PASS,
        "IMAP_HOST": IMAP_HOST,
        "IMAP_PORT": IMAP_PORT,
        "SMTP_HOST": SMTP_HOST,
        "SMTP_PORT": SMTP_PORT,
    }

    client = IMAPClient(session_state={}, config=config)

    # Try to connect
    try:
        connected = await client.is_authenticated()
        if not connected:
            pytest.skip("Cannot connect to GreenMail IMAP")
    except Exception as e:
        pytest.skip(f"IMAP connection failed: {e}")

    yield client

    # Cleanup
    await client.close()


@pytest.fixture
async def smtp_client():
    """Provide an SMTP client configuration."""
    return {
        "host": SMTP_HOST,
        "port": SMTP_PORT,
        "user": TEST_EMAIL_USER,
        "password": TEST_EMAIL_PASS,
    }


# Test data generators
@pytest.fixture
def create_test_document(temp_dir: Path):
    """Create a test document with sample content."""

    def _create(filename: str, content: str) -> Path:
        file_path = temp_dir / filename
        file_path.write_text(content, encoding="utf-8")
        return file_path

    return _create


@pytest.fixture
def sample_document_content():
    """Return sample document content for testing."""
    return """
    # Projektdokumentation: Kundenmanagement System
    
    ## Überblick
    Das Kundenmanagement System wurde entwickelt, um alle Kundeninteraktionen 
    zu zentralisieren und zu optimieren. Es ermöglicht eine 360-Grad-Sicht 
    auf alle Kundenbeziehungen.
    
    ## Hauptfunktionen
    - Kontaktverwaltung mit vollständiger Historie
    - Aufgaben- und Terminmanagement
    - Automatische E-Mail-Integration
    - Leistungsstarke Suche und Filterung
    - Berichterstattung und Analytics
    
    ## Technische Details
    - Backend: Python FastAPI
    - Datenbank: PostgreSQL mit Redis Cache
    - Frontend: React mit Material-UI
    - Deployment: Docker und Kubernetes
    
    ## Kontakt
    Support: support@example.com
    Tel: +49 123 456789
    """
