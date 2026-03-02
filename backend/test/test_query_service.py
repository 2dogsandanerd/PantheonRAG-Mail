import pytest
from unittest.mock import AsyncMock, MagicMock
from src.core.services.query_service import QueryService
from src.core.circuit_breaker import RAGResponse, RAGOperationStatus

@pytest.fixture
def mock_chroma_manager():
    return MagicMock()

@pytest.fixture
def mock_embedding_manager():
    return MagicMock()

@pytest.fixture
def mock_config():
    return {}

@pytest.fixture
def query_service(mock_chroma_manager, mock_embedding_manager, mock_config):
    return QueryService(mock_chroma_manager, mock_embedding_manager, mock_config)

@pytest.mark.asyncio
async def test_retrieve_and_rerank_multi_collection_sorting(query_service):
    # Mock the self.query method to return predefined results
    query_service.query = AsyncMock(side_effect=[
        RAGResponse.ok(data=[
            {'content': 'doc1_colA', 'relevance_score': 0.8, 'metadata': {}, 'collection_name': 'colA'},
            {'content': 'doc2_colA', 'relevance_score': 0.9, 'metadata': {}, 'collection_name': 'colA'}
        ]),
        RAGResponse.ok(data=[
            {'content': 'doc1_colB', 'relevance_score': 0.7, 'metadata': {}, 'collection_name': 'colB'},
            {'content': 'doc2_colB', 'relevance_score': 0.95, 'metadata': {}, 'collection_name': 'colB'}
        ]),
        RAGResponse.ok(data=[
            {'content': 'doc1_colC', 'relevance_score': 0.85, 'metadata': {}, 'collection_name': 'colC'}
        ])
    ])

    query_text = "test query"
    collection_names = ["colA", "colB", "colC"]
    initial_k_per_collection = 2
    final_k = 3

    results = await query_service.retrieve_and_rerank(
        query_text=query_text,
        collection_names=collection_names,
        initial_k_per_collection=initial_k_per_collection,
        final_k=final_k
    )

    # Assert that self.query was called for each collection
    assert query_service.query.call_count == len(collection_names)
    query_service.query.assert_any_call(query_text=query_text, collection_names=['colA'], n_results=initial_k_per_collection)
    query_service.query.assert_any_call(query_text=query_text, collection_names=['colB'], n_results=initial_k_per_collection)
    query_service.query.assert_any_call(query_text=query_text, collection_names=['colC'], n_results=initial_k_per_collection)

    # Assert correct number of final results
    assert len(results) == final_k

    # Assert global sorting is correct
    assert results[0]['content'] == 'doc2_colB' # 0.95
    assert results[1]['content'] == 'doc2_colA' # 0.9
    assert results[2]['content'] == 'doc1_colC' # 0.85

    # Assert source_collection is added
    assert results[0]['source_collection'] == 'colB'
    assert results[1]['source_collection'] == 'colA'
    assert results[2]['source_collection'] == 'colC'

@pytest.mark.asyncio
async def test_retrieve_and_rerank_empty_collections(query_service):
    query_service.query = AsyncMock(return_value=RAGResponse.ok(data=[]))

    results = await query_service.retrieve_and_rerank(
        query_text="test",
        collection_names=["empty_col"],
        initial_k_per_collection=5,
        final_k=5
    )
    assert len(results) == 0

@pytest.mark.asyncio
async def test_retrieve_and_rerank_error_in_one_collection(query_service):
    query_service.query = AsyncMock(side_effect=[
        RAGResponse.ok(data=[{'content': 'doc1', 'relevance_score': 0.8, 'collection_name': 'colA'}]),
        RAGResponse(status=RAGOperationStatus.FAILURE, error="Chroma error"),
        RAGResponse.ok(data=[{'content': 'doc2', 'relevance_score': 0.9, 'collection_name': 'colC'}])
    ])

    results = await query_service.retrieve_and_rerank(
        query_text="test",
        collection_names=["colA", "colB", "colC"],
        initial_k_per_collection=5,
        final_k=2
    )

    assert len(results) == 2
    assert results[0]['content'] == 'doc2'
    assert results[1]['content'] == 'doc1'
    assert query_service.query.call_count == 3 # Still attempts to query all
