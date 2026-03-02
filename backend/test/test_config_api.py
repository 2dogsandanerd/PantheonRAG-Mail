
from fastapi.testclient import TestClient
from src.services.config_service import config_service
import os

def test_get_config_initial(client: TestClient):
    """Test retrieving initial configuration."""
    response = client.get("/api/v1/config")
    assert response.status_code == 200
    assert "TEST_VAR" in response.json()
    assert response.json()["TEST_VAR"] == "initial_value"

def test_post_config_and_get(client: TestClient):
    """Test posting new configuration and retrieving it."""
    new_config = {"LLM_PROVIDER": "openai", "LLM_MODEL": "gpt-4"}
    response = client.post("/api/v1/config", json=new_config)
    assert response.status_code == 200
    assert response.json() == {"message": "Configuration saved successfully."}

    response = client.get("/api/v1/config")
    assert response.status_code == 200
    assert response.json()["LLM_PROVIDER"] == "openai"
    assert response.json()["LLM_MODEL"] == "gpt-4"

def test_post_config_test(client: TestClient):
    """Test the connection test endpoint."""
    # For this test, we'll use a dummy config that should ideally pass for Ollama/Chroma
    # In a real scenario, you might mock the external calls in connection_service
    test_config = {
        "OLLAMA_HOST": "http://localhost:33343",
        "CHROMA_HOST": "http://localhost:33801"
    }
    response = client.post("/api/v1/config/test", json=test_config)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    # We can't assert success without running external services, so just check structure
    assert "component" in response.json()[0]
    assert "success" in response.json()[0]

