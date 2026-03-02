"""
E2E Smoke Test: Complete Email-to-Draft Workflow with RAG

This is the CRITICAL test for Show HN readiness.
It validates the complete user journey:
1. Upload a document to RAG
2. Send an email asking a question
3. Generate a draft that includes context from the uploaded document
4. Verify the draft contains the expected information

If this test passes, the app works as advertised.
"""

import pytest
import asyncio
import httpx
import time
from pathlib import Path
import tempfile
from email.message import EmailMessage
import aiosmtplib

pytestmark = [pytest.mark.e2e, pytest.mark.smoke, pytest.mark.critical]


@pytest.fixture
def gdpr_test_document(temp_dir: Path) -> Path:
    """Create a minimal GDPR test document."""
    content = """
# GDPR Article 6 - Lawfulness of Processing

Processing shall be lawful only if and to the extent that at least one of the following applies:

(a) the data subject has given consent to the processing of his or her personal data for one or more specific purposes;

(b) processing is necessary for the performance of a contract to which the data subject is party or in order to take steps at the request of the data subject prior to entering into a contract;

(c) processing is necessary for compliance with a legal obligation to which the controller is subject;

(d) processing is necessary in order to protect the vital interests of the data subject or of another natural person;

(e) processing is necessary for the performance of a task carried out in the public interest or in the exercise of official authority vested in the controller;

(f) processing is necessary for the purposes of the legitimate interests pursued by the controller or by a third party.

## Key Takeaway
The legal basis for processing personal data must be established before any processing begins.
Marketing emails require explicit consent under Article 6(1)(a).
"""
    doc_path = temp_dir / "gdpr_article_6.txt"
    doc_path.write_text(content, encoding="utf-8")
    return doc_path


async def send_test_email_smtp(subject: str, body: str, to_addr: str = "test@example.com") -> bool:
    """Send test email via GreenMail SMTP."""
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = "customer@example.com"
    msg["To"] = to_addr

    try:
        await aiosmtplib.send(msg, hostname="localhost", port=3025, use_tls=False)
        return True
    except Exception as e:
        pytest.fail(f"Failed to send test email: {e}")
        return False


@pytest.mark.asyncio
async def test_complete_email_to_draft_with_rag_smoke(
    http_client: httpx.AsyncClient,
    gdpr_test_document: Path,
    generate_unique_id,
    ensure_services
):
    """
    🔥 SMOKE TEST: Complete Email → RAG → Draft Flow
    
    This test validates the ENTIRE user journey:
    1. Create RAG collection
    2. Upload GDPR document
    3. Verify document is indexed
    4. Send test email asking about legal basis for marketing
    5. Generate draft using RAG
    6. Verify draft mentions Article 6 and consent
    
    If this passes, the app is Show HN ready.
    """
    print("\n" + "="*60)
    print("🔥 SMOKE TEST: Complete Email-to-Draft with RAG")
    print("="*60)
    
    collection_name = generate_unique_id("smoke_test_gdpr")
    
    # ============================================================
    # STEP 1: Create RAG Collection
    # ============================================================
    print("\n📦 Step 1: Creating RAG collection...")
    response = await http_client.post(
        "/rag/collections",
        data={"collection_name": collection_name}
    )
    
    assert response.status_code in [200, 201], f"Failed to create collection: {response.text}"
    print(f"   ✅ Collection '{collection_name}' created")
    
    # ============================================================
    # STEP 2: Upload GDPR Document to RAG
    # ============================================================
    print("\n📄 Step 2: Uploading GDPR test document...")
    
    with open(gdpr_test_document, "rb") as f:
        files = {"file": ("gdpr_article_6.txt", f, "text/plain")}
        data = {"collection_name": collection_name}
        
        response = await http_client.post(
            "/rag/ingest",
            files=files,
            data=data
        )
    
    assert response.status_code == 200, f"Failed to upload document: {response.text}"
    result = response.json()
    print(f"   ✅ Document uploaded: {result.get('message', 'Success')}")
    
    # Wait for indexing to complete
    await asyncio.sleep(2)
    
    # ============================================================
    # STEP 3: Verify Document is Indexed
    # ============================================================
    print("\n🔍 Step 3: Verifying document is indexed...")
    
    response = await http_client.post(
        f"/rag/query/{collection_name}",
        json={
            "query": "legal basis for processing personal data",
            "n_results": 3
        }
    )
    
    assert response.status_code == 200, f"RAG query failed: {response.text}"
    query_result = response.json()
    
    assert "results" in query_result, "No results in RAG query response"
    assert len(query_result["results"]) > 0, "RAG query returned no results"
    
    # Verify GDPR content is in results
    results_text = " ".join([r.get("content", "") for r in query_result["results"]])
    assert "Article 6" in results_text or "consent" in results_text.lower(), \
        "RAG results don't contain expected GDPR content"
    
    print(f"   ✅ Document indexed: {len(query_result['results'])} chunks retrieved")
    print(f"   📝 Sample content: {query_result['results'][0].get('content', '')[:100]}...")
    
    # ============================================================
    # STEP 4: Simulate Email Asking About Marketing Consent
    # ============================================================
    print("\n📧 Step 4: Simulating customer email...")
    
    email_subject = "Question about marketing emails"
    email_body = """
Hi,

We want to send marketing emails to our customers. 
What is the legal basis we need for this under GDPR?

Thanks,
Customer
"""
    
    # Note: We're simulating the email data directly rather than sending via SMTP
    # because the auto-draft service would need to be running to pick it up
    email_data = {
        "sender": "customer@example.com",
        "subject": email_subject,
        "body": email_body,
        "thread_id": f"thread_{int(time.time())}",
        "use_rag": True
    }
    
    print(f"   📨 Email: '{email_subject}'")
    print(f"   ❓ Question: 'What is the legal basis for marketing emails?'")
    
    # ============================================================
    # STEP 5: Generate Draft with RAG
    # ============================================================
    print("\n🤖 Step 5: Generating draft with RAG context...")
    
    response = await http_client.post(
        "/email/draft",
        json=email_data
    )
    
    assert response.status_code == 200, f"Draft generation failed: {response.text}"
    draft_result = response.json()
    
    print(f"   ✅ Draft generated")
    print(f"   📊 RAG Status: {draft_result.get('rag_status', 'unknown')}")
    print(f"   📚 Collections queried: {draft_result.get('rag_collection_count', 0)}")
    print(f"   📄 Results found: {draft_result.get('rag_result_count', 0)}")
    
    # ============================================================
    # STEP 6: Verify Draft Contains RAG Context
    # ============================================================
    print("\n✅ Step 6: Verifying draft quality...")
    
    draft_text = draft_result.get("draft", "")
    rag_context = draft_result.get("rag_context", "")
    
    assert draft_text, "Draft is empty!"
    assert draft_result.get("rag_status") == "success", \
        f"RAG failed: {draft_result.get('rag_error', 'Unknown error')}"
    
    # Critical assertions: Draft must contain GDPR-specific information
    draft_lower = draft_text.lower()
    
    # Check for Article 6 reference
    has_article_ref = "article 6" in draft_lower or "art. 6" in draft_lower or "art 6" in draft_lower
    
    # Check for consent mention
    has_consent = "consent" in draft_lower
    
    # Check for GDPR mention
    has_gdpr = "gdpr" in draft_lower or "data protection" in draft_lower
    
    print(f"\n   📋 Draft Quality Checks:")
    print(f"      {'✅' if has_article_ref else '❌'} Mentions Article 6")
    print(f"      {'✅' if has_consent else '❌'} Mentions consent")
    print(f"      {'✅' if has_gdpr else '❌'} Mentions GDPR/data protection")
    
    # At least 2 out of 3 must pass
    quality_score = sum([has_article_ref, has_consent, has_gdpr])
    assert quality_score >= 2, \
        f"Draft quality too low ({quality_score}/3). Draft doesn't contain expected GDPR context.\n\nDraft:\n{draft_text}"
    
    print(f"\n   🎯 Quality Score: {quality_score}/3 - PASS")
    
    # ============================================================
    # STEP 7: Display Draft Preview
    # ============================================================
    print("\n📝 Generated Draft Preview:")
    print("-" * 60)
    print(draft_text[:500])
    if len(draft_text) > 500:
        print("...")
    print("-" * 60)
    
    # ============================================================
    # CLEANUP
    # ============================================================
    print("\n🧹 Cleanup: Deleting test collection...")
    await http_client.delete(f"/rag/collections/{collection_name}")
    
    # ============================================================
    # SUCCESS
    # ============================================================
    print("\n" + "="*60)
    print("🎉 SMOKE TEST PASSED!")
    print("="*60)
    print("✅ The app works as advertised:")
    print("   1. Documents can be uploaded to RAG")
    print("   2. RAG retrieval works correctly")
    print("   3. Drafts are generated with RAG context")
    print("   4. Draft quality meets expectations")
    print("\n🚀 App is ready for Show HN!")
    print("="*60 + "\n")


@pytest.mark.asyncio
async def test_draft_generation_without_rag(http_client: httpx.AsyncClient):
    """
    Test that draft generation works even without RAG (fallback mode).
    This ensures the app doesn't crash if RAG is unavailable.
    """
    print("\n🧪 Testing draft generation WITHOUT RAG...")
    
    email_data = {
        "sender": "test@example.com",
        "subject": "Simple question",
        "body": "What is your return policy?",
        "thread_id": f"thread_no_rag_{int(time.time())}",
        "use_rag": False  # Explicitly disable RAG
    }
    
    response = await http_client.post("/email/draft", json=email_data)
    
    assert response.status_code == 200, f"Draft generation failed: {response.text}"
    result = response.json()
    
    # Should still generate a draft, just without RAG context
    assert result.get("draft") or result.get("no_answer_needed"), \
        "No draft generated and no 'no_answer_needed' flag set"
    
    print(f"   ✅ Draft generated without RAG")
    print(f"   📊 No answer needed: {result.get('no_answer_needed', False)}")
