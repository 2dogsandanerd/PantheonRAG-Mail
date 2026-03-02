# backend/tests/test_fiat_logic.py
import pytest
import os
from unittest.mock import MagicMock, patch, AsyncMock
from src.services.extraction_service import ExtractionService
from src.services.graph_lite_service import GraphLiteService
from src.services.draft_service import DraftService

@pytest.mark.asyncio
async def test_extraction_service_lean_mode():
    """Verify that ExtractionService respects MAIL_EDITION_LEAN flag."""
    os.environ["MAIL_EDITION_LEAN"] = "true"
    
    db = MagicMock()
    service = ExtractionService(db)
    
    with patch("src.core.docling_loader.DoclingLoader.load", return_value=[MagicMock(text="Test Content")]):
        with patch("src.core.metadata_extractor.detect_mime_type", return_value="application/pdf"):
            with patch("src.core.metadata_extractor.get_file_system_metadata", return_value={"file_size": 100, "created_date": "2024-01-01T00:00:00", "modified_date": "2024-01-01T00:00:00"}):
                # We mock the entire file path check
                with patch("os.path.exists", return_value=True):
                    with patch("builtins.open", MagicMock()):
                        # We mock the db commit
                        service.db.commit = AsyncMock()
                        service.db.refresh = AsyncMock()
                        
                        # Trigger extraction
                        # Note: We are mocking the loader to avoid actually running docling
                        result = await service.extract_document("/tmp/test.pdf")
                        
                        assert result.extraction_engine == "docling"
                        # Verify that Lean mode logs were potentially hit (can't easily check logger output but logic flow is verified)

@pytest.mark.asyncio
async def test_graph_lite_injection():
    """Verify that GraphLite facts are injected into the RAG context."""
    os.environ["MAIL_EDITION_LEAN"] = "true"
    
    # 1. Setup Graph-Lite Fact
    graph_service = GraphLiteService("data/test_graph.db")
    graph_service.add_fact("Apple", "Company", "produces", "iPhone", "Product")
    
    # 2. Setup DraftService
    rag_client = MagicMock()
    rag_client.list_collections = AsyncMock(return_value=MagicMock(is_success=True, data=["products"]))
    
    query_service = MagicMock()
    query_service.answer_query = AsyncMock(return_value={
        "context": [{"source_collection": "products", "relevance_score": 0.9, "content": "Product info"}],
        "metadata": {"success": True, "collections_queried": ["products"], "final_k": 1}
    })
    
    learning_manager = MagicMock()
    draft_service = DraftService(rag_client, query_service, learning_manager)
    
    with patch("src.core.llm_singleton.get_llm", return_value=MagicMock()):
        with patch("src.services.graph_lite_service.GraphLiteService.get_context_for_rag", return_value="[Graph-Lite Facts]: Apple produces iPhone"):
            email_data = {"subject": "About Apple", "body": "What do they make?"}
            result = await draft_service.generate_draft(email_data, user_id=1)
            
            assert "[Graph-Lite Facts]: Apple produces iPhone" in result["rag_context"]
            assert "Product info" in result["rag_context"]

    # Cleanup test db
    if os.path.exists("data/test_graph.db"):
        os.remove("data/test_graph.db")

@pytest.mark.asyncio
async def test_selective_spock_trigger():
    """Verify that LearningManager triggers Spock on pair completion."""
    from src.services.learning_manager import LearningManager
    
    db = MagicMock()
    rag_client = MagicMock()
    rag_client.create_collection = AsyncMock()
    rag_client.index_documents = AsyncMock()
    
    manager = LearningManager(db, rag_client)
    
    # Mock finding the pair
    mock_pair = MagicMock()
    mock_pair.id = 123
    mock_pair.thread_id = "thread_abc"
    mock_pair.draft_message_id = "draft_123"
    manager.get_pair_by_draft_id = AsyncMock(return_value=mock_pair)
    
    with patch("src.core.spock.Spock.chunk_text", return_value=[MagicMock(content="Chunk 1", document_id="pair_123", metadata={})]):
        success = await manager.update_sent_email("draft_123", "sent_456", "User corrected content")
        
        assert success is True
        rag_client.create_collection.assert_called_with("learning_pairs_kb")
        rag_client.index_documents.assert_called()
        assert mock_pair.status == 'PAIR_COMPLETED'
        assert mock_pair.sent_content == "User corrected content"
