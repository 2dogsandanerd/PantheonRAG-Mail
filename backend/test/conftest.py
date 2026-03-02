

import pytest
import pytest
from fastapi.testclient import TestClient
from src.main import app  # Import the main app instance

# Import all routers and services needed for dependency overrides
from src.api.v1 import auth, email, learning, auto_draft, dashboard, config, services, docs, statistics
from src.api.v1.rag import router as rag_router
from src.services.config_service import ConfigService
from src.services.connection_service import ConnectionService
from src.api.v1.config import get_configuration, save_configuration, test_connections

import os
import httpx # Added for async_test_client_fixture
import asyncio
import time

@pytest.fixture(name="client")
def client_fixture(tmp_path, mocker):
    # Create a temporary .env file for testing
    temp_dotenv_path = tmp_path / ".env"
    with open(temp_dotenv_path, "w") as f:
        f.write("TEST_VAR=initial_value\n")

    # Re-include all routers on the main app instance to ensure they are available for testing
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(email.router, prefix="/api/v1/email", tags=["Email"])
    app.include_router(rag_router, prefix="/api/v1/rag", tags=["RAG"])
    app.include_router(learning.router, prefix="/api/v1/learning", tags=["Learning"])
    app.include_router(auto_draft.router, prefix="/api/v1/auto-draft", tags=["Auto-Draft"])
    app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
    app.include_router(config.router, prefix="/api/v1/config", tags=["Configuration"])
    app.include_router(services.router, prefix="/api/v1/services", tags=["Services"])
    app.include_router(docs.router, prefix="/api/v1/docs", tags=["Documentation"])
    app.include_router(statistics.router, prefix="/api/v1/statistics", tags=["Statistics"])

    # Also include the root and health endpoints
    @app.get("/")
    async def root_test():
        return {"message": "Test Root"}

    @app.get("/api/health")
    async def health_test():
        return {"status": "healthy"}
    
    # Create a test-specific ConfigService instance
    test_config_service = ConfigService(dotenv_path=str(temp_dotenv_path))

    # Create a mock ConnectionService for testing
    mock_connection_service = mocker.Mock(spec=ConnectionService)
    mock_connection_service.test_all_connections.return_value = [
        {"component": "ollama", "success": True, "message": "Mocked success"}
    ]

    # Override the dependencies for the config API endpoints on the main app instance
    app.dependency_overrides[get_configuration] = lambda: test_config_service
    app.dependency_overrides[save_configuration] = lambda: test_config_service
    app.dependency_overrides[test_connections] = lambda: mock_connection_service

    # Yield the TestClient with the main app instance
    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides after the test
    app.dependency_overrides = {}


async def wait_for_backend(url: str, timeout: int = 60, interval: int = 1):
    """Waits for the backend to be available."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{url}/api/health")
                if response.status_code == 200:
                    print(f"\nBackend is ready at {url}")
                    return
        except httpx.ConnectError:
            pass
        print(f"\nWaiting for backend at {url}...", end="", flush=True)
        await asyncio.sleep(interval)
    raise TimeoutError(f"Backend did not become available at {url} within {timeout} seconds.")


@pytest.fixture(scope="session")
async def backend_ready():
    """Ensures the backend is running and accessible before tests start."""
    backend_url = "http://localhost:33800"
    await wait_for_backend(backend_url)
    yield


@pytest.fixture(name="async_test_client")
async def async_test_client_fixture(backend_ready): # Depend on backend_ready
    """
    Asynchronous test client for making requests to the live FastAPI application.
    Assumes the FastAPI app is running on http://localhost:33800.
    """
    async with httpx.AsyncClient(base_url="http://localhost:33800") as client:
        yield client

