"""
E2E Test: Privacy Law Simple Query

Tests the complete email-to-draft workflow using privacy law documents (GDPR).
This validates that the generic email assistant can handle legal/compliance queries.
"""

import pytest
import httpx
from pathlib import Path

pytestmark = [pytest.mark.e2e, pytest.mark.privacy, pytest.mark.slow]


@pytest.mark.asyncio
async def test_simple_gdpr_query(
    http_client: httpx.AsyncClient,
    test_collection: str,
    create_test_document,
    wait_for_processing,
):
    """Test simple GDPR query: legal basis for processing employee data."""
    
    # 1. Create sample GDPR content (simplified for testing)
    gdpr_content = """
    Article 6 - Lawfulness of processing
    
    1. Processing shall be lawful only if and to the extent that at least one of the following applies:
    
    (a) the data subject has given consent to the processing of his or her personal data for one or more specific purposes;
    
    (b) processing is necessary for the performance of a contract to which the data subject is party or in order to take steps at the request of the data subject prior to entering into a contract;
    
    (c) processing is necessary for compliance with a legal obligation to which the controller is subject;
    
    (d) processing is necessary in order to protect the vital interests of the data subject or of another natural person;
    
    (e) processing is necessary for the performance of a task carried out in the public interest or in the exercise of official authority vested in the controller;
    
    (f) processing is necessary for the purposes of the legitimate interests pursued by the controller or by a third party, except where such interests are overridden by the interests or fundamental rights and freedoms of the data subject which require protection of personal data, in particular where the data subject is a child.
    """
    
    doc_path = create_test_document("gdpr_art6.txt", gdpr_content)
    
    # 2. Upload document to RAG
    with open(doc_path, "rb") as f:
        upload_response = await http_client.post(
            "/api/v1/rag/documents/upload",
            data={
                "collection_name": test_collection,
                "chunk_size": "500",
                "chunk_overlap": "50",
            },
            files={"files": ("gdpr_art6.txt", f, "text/plain")},
        )
    
    assert upload_response.status_code == 200, f"Upload failed: {upload_response.text}"
    print("✅ GDPR document uploaded successfully")
    
    # 3. Wait for processing
    await wait_for_processing(3.0)
    print("✅ Document processing complete")
    
    # 4. Query via RAG
    query_response = await http_client.post(
        "/api/v1/rag/query/test",
        data={
            "query": "What is the legal basis for processing employee data?",
            "collection_name": test_collection,
            "n_results": "5",
        },
    )
    
    assert query_response.status_code == 200, f"Query failed: {query_response.text}"
    query_data = query_response.json()
    
    print(f"✅ Query executed successfully")
    print(f"   Found {len(query_data.get('results', []))} results")
    
    # 5. Verify results contain relevant GDPR articles
    results = query_data.get("results", [])
    assert len(results) > 0, "No results returned from query"
    
    # Check if results mention Article 6
    found_article_6 = False
    for result in results:
        content = str(result.get("content", "")).lower()
        if "article 6" in content or "art. 6" in content or "art 6" in content:
            found_article_6 = True
            print(f"   ✓ Found Article 6 reference")
            break
    
    assert found_article_6, "Expected Article 6 reference not found in results"
    
    # Check if results mention legal basis options (b) or (f) for employment
    found_legal_basis = False
    for result in results:
        content = str(result.get("content", "")).lower()
        if ("performance of a contract" in content or 
            "legitimate interests" in content):
            found_legal_basis = True
            print(f"   ✓ Found relevant legal basis")
            break
    
    assert found_legal_basis, "Expected legal basis not found in results"
    
    print("\n✅ Simple GDPR query test passed!")
    print(f"   - Document uploaded and processed")
    print(f"   - Query returned {len(results)} relevant results")
    print(f"   - Article 6 reference found")
    print(f"   - Relevant legal basis identified")


@pytest.mark.asyncio
async def test_gdpr_right_to_be_forgotten(
    http_client: httpx.AsyncClient,
    test_collection: str,
    create_test_document,
    wait_for_processing,
):
    """Test GDPR right to erasure (right to be forgotten)."""
    
    # Create Article 17 content
    gdpr_art17_content = """
    Article 17 - Right to erasure ('right to be forgotten')
    
    1. The data subject shall have the right to obtain from the controller the erasure of personal data concerning him or her without undue delay and the controller shall have the obligation to erase personal data without undue delay where one of the following grounds applies:
    
    (a) the personal data are no longer necessary in relation to the purposes for which they were collected or otherwise processed;
    
    (b) the data subject withdraws consent on which the processing is based according to point (a) of Article 6(1), or point (a) of Article 9(2), and where there is no other legal ground for the processing;
    
    (c) the data subject objects to the processing pursuant to Article 21(1) and there are no overriding legitimate grounds for the processing, or the data subject objects to the processing pursuant to Article 21(2);
    
    (d) the personal data have been unlawfully processed;
    
    (e) the personal data have to be erased for compliance with a legal obligation in Union or Member State law to which the controller is subject;
    
    (f) the personal data have been collected in relation to the offer of information society services referred to in Article 8(1).
    """
    
    doc_path = create_test_document("gdpr_art17.txt", gdpr_art17_content)
    
    # Upload document
    with open(doc_path, "rb") as f:
        await http_client.post(
            "/api/v1/rag/documents/upload",
            data={
                "collection_name": test_collection,
                "chunk_size": "500",
                "chunk_overlap": "50",
            },
            files={"files": ("gdpr_art17.txt", f, "text/plain")},
        )
    
    await wait_for_processing(3.0)
    
    # Query
    query_response = await http_client.post(
        "/api/v1/rag/query/test",
        data={
            "query": "What are the requirements for the right to be forgotten?",
            "collection_name": test_collection,
            "n_results": "5",
        },
    )
    
    assert query_response.status_code == 200
    query_data = query_response.json()
    
    results = query_data.get("results", [])
    assert len(results) > 0, "No results returned"
    
    # Verify Article 17 is found
    found_art17 = False
    for result in results:
        content = str(result.get("content", "")).lower()
        if "article 17" in content or "right to erasure" in content or "right to be forgotten" in content:
            found_art17 = True
            break
    
    assert found_art17, "Article 17 reference not found"
    print("✅ Right to be forgotten test passed!")
