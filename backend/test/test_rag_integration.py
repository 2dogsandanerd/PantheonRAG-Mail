import pytest
import asyncio
from src.services.external_rag_connector import get_rag_service
from src.core.indexing_service import Document

# Mock config for testing
TEST_CONFIG = {
    "CHROMA_HOST": "127.0.0.1",
    "CHROMA_PORT": 33801,
    "OLLAMA_HOST": "http://127.0.0.1:33343",
    "EMBEDDING_MODEL": "nomic-embed-text:latest",
    "EMBEDDING_PROVIDER": "ollama",
    "EXTERNAL_RAG_ENABLED": "false", # Use local for these integration tests
    "CHROMA_IN_MEMORY": "true"       # Use in-memory for testing to avoid connection issues
}

@pytest.mark.asyncio
async def test_end_to_end_workflow():
    """Test complete RAG workflow: create → index → query → delete"""
    rag = await get_rag_service(config_override=TEST_CONFIG)
    collection_name = "test_collection_e2e"

    # 1. Create collection
    create_resp = await rag.create_collection(
        collection_name,
        embedding_provider="ollama",
        embedding_model="nomic-embed-text:latest"
    )
    assert create_resp.is_success

    # 2. Index documents
    docs = [
        Document(content="Email authentication with OAuth2", metadata={"type": "auth"}),
        Document(content="Security best practices", metadata={"type": "security"})
    ]
    index_resp = await rag.index_documents(docs, collection_name)
    assert index_resp.is_success
    assert index_resp.data["indexed_chunks"] > 0

    # 3. Query
    query_resp = await rag.query("OAuth authentication", [collection_name])
    assert query_resp.is_success
    assert len(query_resp.data) > 0

    # 4. Query with context and get LLM response
    context_resp = await rag.query_with_context(
        "How do I implement OAuth?",
        "You are a helpful assistant.",
        [collection_name]
    )
    assert context_resp["success"] is True
    assert isinstance(context_resp["response"], str)
    assert len(context_resp["response"]) > 0
    assert len(context_resp["context_chunks"]) > 0
    assert "Email authentication with OAuth2" in context_resp["context_chunks"][0]["content"]

    # 5. Delete collection
    delete_resp = await rag.delete_collection(collection_name)
    assert delete_resp.is_success
    
    # 6. Shutdown
    if hasattr(rag, "shutdown"):
        await rag.shutdown()

@pytest.mark.asyncio
async def test_circuit_breaker_integration():
    """Test circuit breaker prevents cascading failures"""
    # This test would require mocking external services to simulate failures
    # For now, it's a placeholder.
    pass
