import pytest
from unittest.mock import Mock, MagicMock, patch
from src.services.learning_manager import LearningManager
from src.services.draft_service import DraftService
from src.core.models.rag_types import RankedNode # Import RankedNode

# Mock DB Session
@pytest.fixture
def mock_db():
    """This is a fake database session for testing."""
    fake_db_session = MagicMock()
    return fake_db_session

# Test Learning Manager
def test_learning_manager_add_fake_draft(mock_db):
    """Test adding a fake draft to the learning DB."""
    manager = LearningManager(db=mock_db)

    # Mock a fake pair object
    fake_pair = Mock()
    fake_pair.id = 1
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    result = manager.add_draft(
        user_id=1,
        thread_id="fake_thread_123",
        draft_message_id="fake_draft_456",
        draft_content="This is fake content for a test draft.",
        status="FAKE_DRAFT_CREATED"
    )

    assert mock_db.add.called
    assert mock_db.commit.called

# Test Draft Service
@pytest.mark.asyncio # Mark as async test
async def test_draft_service_generate_fake_draft():
    """Test fake draft generation (MOCKED)."""
    # Create a fake RAG client mock (still needed for list_collections)
    mock_rag_client_fake = Mock()
    mock_rag_client_fake.list_collections.return_value = Mock(is_success=True, data=["collection1", "collection2"])

    # Create a fake QueryService mock
    mock_query_service_fake = Mock()
    mock_query_service_fake.answer_query.return_value = {
        "response": "This is a fake generated draft from QueryService.",
        "context": [
            RankedNode(
                content="fake_context_1",
                source_collection="collection1",
                relevance_score=0.9,
                metadata={"source": "doc1"},
                distance=0.1,
                source="doc1",
                page_number=1
            ),
            RankedNode(
                content="fake_context_2",
                source_collection="collection2",
                relevance_score=0.8,
                metadata={"source": "doc2"},
                distance=0.2,
                source="doc2",
                page_number=2
            )
        ],
        "metadata": {
            "success": True,
            "error": None,
            "collections_queried": ["collection1", "collection2"],
            "total_candidates": 20,
            "final_k": 2,
            "model_used": "fake-llm-model"
        }
    }

    # Create a fake Learning Manager mock
    mock_learning_manager_fake = Mock()

    # Patch the get_llm function to return a fake LLM (no longer directly called by DraftService for draft generation)
    with patch('src.services.draft_service.get_llm') as mock_get_llm_fake:
        mock_llm_fake = Mock()
        mock_llm_fake.acomplete.return_value = "This is a fake generated draft from LLM." # Mock acomplete
        mock_llm_fake.model = "fake-test-model" # Use 'model' attribute
        mock_get_llm_fake.return_value = mock_llm_fake

        service = DraftService(
            rag_client=mock_rag_client_fake,
            query_service=mock_query_service_fake, # Pass QueryService mock
            learning_manager=mock_learning_manager_fake
        )

        fake_email_data = {
            "subject": "Fake Subject", 
            "body": "Hello, this is a fake email body."
        }

        result = await service.generate_draft( # Await the async method
            email_data=fake_email_data,
            user_id=1
        )

        # Assertions
        mock_query_service_fake.answer_query.assert_called_once() # Ensure answer_query was called
        assert "draft" in result
        assert result["draft"] == "This is a fake generated draft from QueryService." # Draft comes from QueryService now
        assert "rag_context" in result
        assert "fake_context_1" in result["rag_context"]
        assert "collection1 - Relevanz: 0.90" in result["rag_context"] # Check formatted context
        assert "model" in result
        assert result["model"] == "fake-llm-model"
        assert result["rag_status"] == "success"
        assert result["rag_collection_count"] == 2
        assert result["rag_result_count"] == 2
