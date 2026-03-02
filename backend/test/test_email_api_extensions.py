
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from src.main import app  # Import the main app
from src.api.v1.dependencies import get_email_client, get_learning_manager, get_current_user
from src.database.models import User, LearningPair
from datetime import datetime

# Mock the dummy user dependency as it requires DB access
@pytest.fixture(autouse=True)
def override_get_current_user():
    dummy_user = User(id=1, username="dummyuser", email="dummy@example.com")
    app.dependency_overrides[get_current_user] = lambda: dummy_user
    yield
    app.dependency_overrides = {}

@pytest.fixture
def mock_email_client():
    mock = MagicMock()
    return mock

@pytest.fixture
def mock_learning_manager():
    mock = MagicMock()
    return mock

@pytest.fixture
def client(mock_email_client, mock_learning_manager):
    app.dependency_overrides[get_email_client] = lambda: mock_email_client
    app.dependency_overrides[get_learning_manager] = lambda: mock_learning_manager
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides = {}


def test_clear_inbox_success(client, mock_email_client):
    """Test successful clearing of the inbox."""
    mock_email_client.clear_inbox.return_value = {"status": "success", "count": 5, "message": "Cleared 5 emails."}
    
    response = client.post("/api/v1/email/clear-inbox")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["count"] == 5
    mock_email_client.clear_inbox.assert_called_once()

def test_clear_inbox_failure(client, mock_email_client):
    """Test failure case for clearing the inbox."""
    mock_email_client.clear_inbox.return_value = {"status": "error", "message": "Failed to connect."}
    
    response = client.post("/api/v1/email/clear-inbox")
    
    assert response.status_code == 500
    assert "Failed to connect" in response.json()["detail"]


def test_get_drafts_all(client, mock_learning_manager):
    """Test fetching all drafts without a status filter."""
    mock_pairs = [
        LearningPair(id=1, thread_id="t1", draft_content="c1", status="DRAFT_CREATED", created_at=datetime.now(), draft_message_id="d1"),
        LearningPair(id=2, thread_id="t2", draft_content="c2", status="PAIR_COMPLETED", created_at=datetime.now(), draft_message_id="d2")
    ]
    mock_learning_manager.get_user_drafts.return_value = mock_pairs
    
    response = client.get("/api/v1/email/drafts")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["drafts"]) == 2
    assert data["drafts"][0]["id"] == 1
    mock_learning_manager.get_user_drafts.assert_called_once_with(user_id=1, status=None)

def test_get_drafts_with_status_filter(client, mock_learning_manager):
    """Test fetching drafts filtered by status."""
    mock_pairs = [
        LearningPair(id=1, thread_id="t1", draft_content="c1", status="DRAFT_CREATED", created_at=datetime.now(), draft_message_id="d1")
    ]
    mock_learning_manager.get_user_drafts.return_value = mock_pairs
    
    response = client.get("/api/v1/email/drafts?status=DRAFT_CREATED")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["drafts"]) == 1
    assert data["drafts"][0]["status"] == "DRAFT_CREATED"
    mock_learning_manager.get_user_drafts.assert_called_once_with(user_id=1, status="DRAFT_CREATED")

def test_delete_draft_success(client, mock_learning_manager):
    """Test successful deletion of a draft."""
    mock_learning_manager.delete_draft.return_value = True
    
    response = client.delete("/api/v1/email/draft/123")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Draft deleted successfully."
    mock_learning_manager.delete_draft.assert_called_once_with(draft_id=123, user_id=1)

def test_delete_draft_not_found(client, mock_learning_manager):
    """Test attempting to delete a draft that does not exist."""
    mock_learning_manager.delete_draft.return_value = False
    
    response = client.delete("/api/v1/email/draft/999")
    
    assert response.status_code == 404
    assert "Draft not found" in response.json()["detail"]
