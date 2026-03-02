import pytest
from httpx import AsyncClient
from unittest.mock import Mock, patch
from src.main import app
from src.api.v1.dependencies import get_query_service
from src.core.models.rag_types import RankedNode

# Mock QueryService for testing
@pytest.fixture
def mock_query_service():
    mock = Mock()
    mock.answer_query.return_value = {
        "response": "Synthesized LLM answer.",
        "context": [
            RankedNode(
                content="context_chunk_1",
                source_collection="test_collection",
                relevance_score=0.9,
                metadata={"source": "doc1"},
                distance=0.1,
                source="doc1",
                page_number=1
            ).to_dict(), # Ensure it's a dict for API response
            RankedNode(
                content="context_chunk_2",
                source_collection="test_collection",
                relevance_score=0.8,
                metadata={"source": "doc2"},
                distance=0.2,
                source="doc2",
                page_number=2
            ).to_dict() # Ensure it's a dict for API response
        ],
        "metadata": {
            "success": True,
            "error": None,
            "collections_queried": ["test_collection"],
            "total_candidates": 20,
            "final_k": 2,
            "model_used": "test-llm-model"
        }
    }
    return mock

# Override the dependency for testing
app.dependency_overrides[get_query_service] = mock_query_service

@pytest.mark.asyncio
async def test_query_rag_success(mock_query_service):
    """Test the /rag/query endpoint for a successful RAG query."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/rag/query",
            json={
                "query": "What is the capital of France?",
                "collections": ["test_collection"],
                "k": 5
            }
        )

    assert response.status_code == 200
    data = response.json()

    assert "llm_response" in data
    assert data["llm_response"] == "Synthesized LLM answer."
    assert "context_chunks" in data
    assert len(data["context_chunks"]) == 2
    assert data["context_chunks"][0]["content"] == "context_chunk_1"
    assert "query" in data
    assert data["query"] == "What is the capital of France?"

    mock_query_service.answer_query.assert_called_once_with(
        query_text="What is the capital of France?",
        collection_names=["test_collection"],
        final_k=5,
        system_prompt="You are a helpful assistant. Answer the user's query based on the provided context.",
        temperature=0.1
    )

@pytest.mark.asyncio
async def test_query_rag_failure(mock_query_service):
    """Test the /rag/query endpoint for a failed RAG query."""
    mock_query_service.answer_query.return_value = {
        "response": None,
        "context": [],
        "metadata": {
            "success": False,
            "error": "Failed to retrieve context.",
            "collections_queried": ["test_collection"],
            "total_candidates": 0,
            "final_k": 0,
            "model_used": "test-llm-model"
        }
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/rag/query",
            json={
                "query": "This query will fail.",
                "collections": ["test_collection"],
                "k": 5
            }
        )

    assert response.status_code == 500 # Expecting HTTPException from ChromaDBError
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Failed to retrieve context."
    mock_query_service.answer_query.assert_called_once()
