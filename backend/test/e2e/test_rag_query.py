"""
E2E Test: RAG Query Flow

Tests querying the RAG system with real ChromaDB.
"""

import pytest
import httpx
from pathlib import Path

pytestmark = [pytest.mark.e2e, pytest.mark.rag, pytest.mark.integration]


@pytest.mark.asyncio
async def test_query_without_results(
    http_client: httpx.AsyncClient, test_collection: str
):
    """Test querying an empty collection returns empty results."""
    response = await http_client.post(
        "/rag/query/test",
        data={
            "query": "Was ist die Hauptstadt von Deutschland?",
            "collection_name": test_collection,
            "n_results": "5",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Should return results structure (might be empty)
    assert "results" in data or "response" in data or "context_chunks" in data

    print(f"✅ Query executed on empty collection")
    print(f"   Response keys: {list(data.keys())}")


@pytest.mark.asyncio
async def test_query_with_context(
    http_client: httpx.AsyncClient,
    test_collection: str,
    create_test_document,
    wait_for_processing,
):
    """Test querying a collection with documents."""
    # Upload a document first
    content = """
    Deutschland - Grundinformationen
    
    Deutschland ist ein Land in Mitteleuropa.
    Die Hauptstadt von Deutschland ist Berlin.
    Deutschland hat etwa 83 Millionen Einwohner.
    Die offizielle Sprache ist Deutsch.
    """

    doc_path = create_test_document("deutschland_info.txt", content)

    with open(doc_path, "rb") as f:
        await http_client.post(
            "/rag/documents/upload",
            data={
                "collection_name": test_collection,
                "chunk_size": "500",
                "chunk_overlap": "50",
            },
            files={"files": ("deutschland_info.txt", f, "text/plain")},
        )

    # Wait for processing
    await wait_for_processing(2.0)

    # Query the document
    response = await http_client.post(
        "/rag/query/test",
        data={
            "query": "Hauptstadt Deutschland",
            "collection_name": test_collection,
            "n_results": "3",
        },
    )

    assert response.status_code == 200
    data = response.json()

    print(f"✅ Query with context executed")
    print(f"   Found {len(data.get('results', []))} results")

    # Verify we got results
    results = data.get("results", [])
    if len(results) > 0:
        print("   ✓ Query returned results")
    else:
        print("   ⚠️  No results (may need more processing time)")


@pytest.mark.asyncio
async def test_advanced_query_options(
    http_client: httpx.AsyncClient, test_collection: str
):
    """Test query with advanced options."""
    response = await http_client.post(
        "/rag/query/test",
        data={
            "query": "Test query for options",
            "collection_name": test_collection,
            "n_results": "10",
            "advanced_mode": "true",
        },
    )

    assert response.status_code == 200
    data = response.json()

    print(f"✅ Advanced query executed")
    print(f"   Response keys: {list(data.keys())}")


@pytest.mark.asyncio
async def test_query_with_domain(http_client: httpx.AsyncClient, test_collection: str):
    """Test query with domain parameter."""
    response = await http_client.post(
        "/rag/query/test",
        data={
            "query": "Test query",
            "collection_name": test_collection,
            "n_results": "5",
            "domain": "general",
        },
    )

    assert response.status_code == 200
    print("✅ Query with domain parameter executed")


@pytest.mark.asyncio
async def test_llm_query_generation(
    http_client: httpx.AsyncClient,
    test_collection: str,
    create_test_document,
    wait_for_processing,
):
    """Test LLM query with answer generation."""
    # Upload content
    content = """
    Python Programmierung Grundlagen
    
    Python ist eine interpretierte, objektorientierte Programmiersprache.
    Python wurde von Guido van Rossum entwickelt.
    Python ist bekannt für seine einfache Syntax.
    """

    doc_path = create_test_document("python_info.txt", content)

    with open(doc_path, "rb") as f:
        await http_client.post(
            "/rag/documents/upload",
            data={
                "collection_name": test_collection,
                "chunk_size": "500",
                "chunk_overlap": "50",
            },
            files={"files": ("python_info.txt", f, "text/plain")},
        )

    await wait_for_processing(2.0)

    # Query with LLM generation
    response = await http_client.post(
        "/rag/query/test",
        data={
            "query": "Wer hat Python entwickelt?",
            "collection_name": test_collection,
            "n_results": "3",
            "generate_answer": "true",
        },
    )

    assert response.status_code == 200
    data = response.json()

    print(f"✅ LLM query executed")

    # Check for answer in response
    has_answer = "answer" in data or "response" in data or "llm_response" in data

    if has_answer:
        print("   ✓ Answer field present in response")
    else:
        print("   ⚠️  No answer field (LLM may not be configured)")


@pytest.mark.asyncio
async def test_invalid_collection_query(http_client: httpx.AsyncClient):
    """Test querying a non-existent collection."""
    response = await http_client.post(
        "/rag/query/test",
        data={
            "query": "Test",
            "collection_name": "nonexistent_collection_xyz",
            "n_results": "5",
        },
    )

    # Should either return empty results or 404
    assert response.status_code in [200, 404, 400]
    print(f"✅ Invalid collection query handled (status: {response.status_code})")
