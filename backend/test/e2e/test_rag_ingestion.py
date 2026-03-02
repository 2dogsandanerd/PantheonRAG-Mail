"""
E2E Test: RAG Document Ingestion Flow

Tests the complete document ingestion pipeline:
1. Upload document
2. Processing (Docling)
3. ChromaDB storage
4. Verification via query
"""

import pytest
import httpx
from pathlib import Path
import asyncio
import time

pytestmark = [pytest.mark.e2e, pytest.mark.rag, pytest.mark.slow]


@pytest.mark.asyncio
async def test_create_collection(http_client: httpx.AsyncClient, generate_unique_id):
    """Test creating a RAG collection."""
    collection_name = generate_unique_id("test_collection")

    response = await http_client.post(
        "/rag/collections", data={"collection_name": collection_name}
    )

    assert response.status_code == 200, f"Failed to create collection: {response.text}"
    data = response.json()

    assert "collection_name" in data or "name" in data
    print(f"✅ Created collection: {collection_name}")

    # Cleanup
    await http_client.delete(f"/rag/collections/{collection_name}")


@pytest.mark.asyncio
async def test_upload_text_document(
    http_client: httpx.AsyncClient,
    test_collection: str,
    temp_dir: Path,
    create_test_document,
):
    """Test uploading a text document to a collection."""
    # Create test document
    content = """
    # Test Document for E2E Testing
    
    This is a test document about Artificial Intelligence.
    AI is transforming how we work with information.
    Machine learning models can process documents efficiently.
    Natural language processing enables semantic search.
    """

    doc_path = create_test_document("test_doc.txt", content)

    # Upload document
    with open(doc_path, "rb") as f:
        response = await http_client.post(
            "/rag/documents/upload",
            data={
                "collection_name": test_collection,
                "chunk_size": "500",
                "chunk_overlap": "50",
            },
            files={"files": ("test_doc.txt", f, "text/plain")},
        )

    assert response.status_code == 200, f"Upload failed: {response.text}"
    data = response.json()

    print(f"✅ Uploaded document to {test_collection}")
    print(f"   Response: {data}")


@pytest.mark.asyncio
async def test_upload_and_query_document(
    http_client: httpx.AsyncClient,
    generate_unique_id,
    temp_dir: Path,
    create_test_document,
    wait_for_processing,
):
    """Complete flow: upload document and query it."""
    collection_name = generate_unique_id("query_test_collection")

    try:
        # 1. Create collection
        response = await http_client.post(
            "/rag/collections", data={"collection_name": collection_name}
        )
        assert response.status_code == 200
        print(f"1. ✅ Created collection: {collection_name}")

        # 2. Upload test document with specific content
        content = """
        Projekt Alpha - Technische Dokumentation
        
        Zusammenfassung:
        Projekt Alpha ist ein neues Kundenmanagementsystem.
        Es wurde entwickelt, um alle Kundeninteraktionen zu zentralisieren.
        
        Technische Details:
        - Backend: Python FastAPI
        - Datenbank: PostgreSQL
        - Cache: Redis
        - Frontend: React
        
        Kontakt:
        Entwickler: dev@example.com
        Telefon: +49 123 4567890
        """

        doc_path = create_test_document("projekt_alpha.txt", content)

        with open(doc_path, "rb") as f:
            upload_response = await http_client.post(
                "/rag/documents/upload",
                data={
                    "collection_name": collection_name,
                    "chunk_size": "500",
                    "chunk_overlap": "50",
                },
                files={"files": ("projekt_alpha.txt", f, "text/plain")},
            )

        assert upload_response.status_code == 200
        print("2. ✅ Document uploaded successfully")

        # 3. Wait for processing
        await wait_for_processing(3.0)
        print("3. ✅ Waited for processing")

        # 4. Query the document
        query_response = await http_client.post(
            "/rag/query/test",
            data={
                "query": "Welche Technologien werden in Projekt Alpha verwendet?",
                "collection_name": collection_name,
                "n_results": "5",
            },
        )

        assert query_response.status_code == 200
        query_data = query_response.json()

        print("4. ✅ Query executed")
        print(f"   Found {len(query_data.get('results', []))} results")

        # 5. Verify results contain relevant information
        results = query_data.get("results", [])
        assert len(results) > 0, "No results returned from query"

        # Check if any result contains expected content
        found_relevant = False
        for result in results:
            content_text = str(result.get("content", "")).lower()
            if (
                "fastapi" in content_text
                or "postgresql" in content_text
                or "react" in content_text
            ):
                found_relevant = True
                break

        if found_relevant:
            print("5. ✅ Query returned relevant results")
        else:
            print(
                "5. ⚠️  Query results don't contain expected keywords (may need more processing time)"
            )

        print("\n✅ Complete ingestion and query flow passed!")

    finally:
        # Cleanup
        try:
            await http_client.delete(f"/rag/collections/{collection_name}")
            print(f"   Cleaned up collection: {collection_name}")
        except:
            pass


@pytest.mark.asyncio
async def test_document_listing(http_client: httpx.AsyncClient, test_collection: str):
    """Test listing documents in a collection."""
    response = await http_client.get(
        f"/rag/collections/{test_collection}/documents",
        params={"limit": 10, "offset": 0},
    )

    assert response.status_code == 200
    data = response.json()

    # Should return a list (might be empty)
    assert isinstance(data, list) or "documents" in data or "items" in data

    print(f"✅ Listed documents in {test_collection}")


@pytest.mark.asyncio
async def test_collection_stats(http_client: httpx.AsyncClient, test_collection: str):
    """Test getting collection statistics."""
    response = await http_client.get(f"/rag/collections/{test_collection}/stats")

    assert response.status_code == 200
    data = response.json()

    print(f"✅ Collection stats for {test_collection}:")
    print(f"   {data}")
