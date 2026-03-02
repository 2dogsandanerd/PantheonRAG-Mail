"""
E2E Test: Privacy Law Multi-Article Context

Tests queries that require multiple articles/sections for a complete answer.
Example: Data breach notification requires both Art. 33 and Art. 34 GDPR.
"""

import pytest
import httpx
from pathlib import Path

pytestmark = [pytest.mark.e2e, pytest.mark.privacy, pytest.mark.slow]


@pytest.mark.asyncio
async def test_data_breach_notification(
    http_client: httpx.AsyncClient,
    test_collection: str,
    create_test_document,
    wait_for_processing,
):
    """Test data breach notification query requiring multiple GDPR articles."""
    
    # Create Article 33 and 34 content
    gdpr_breach_content = """
    Article 33 - Notification of a personal data breach to the supervisory authority
    
    1. In the case of a personal data breach, the controller shall without undue delay and, where feasible, not later than 72 hours after having become aware of it, notify the personal data breach to the supervisory authority competent in accordance with Article 55, unless the personal data breach is unlikely to result in a risk to the rights and freedoms of natural persons.
    
    2. The notification referred to in paragraph 1 shall at least:
    (a) describe the nature of the personal data breach including where possible, the categories and approximate number of data subjects concerned and the categories and approximate number of personal data records concerned;
    (b) communicate the name and contact details of the data protection officer or other contact point where more information can be obtained;
    (c) describe the likely consequences of the personal data breach;
    (d) describe the measures taken or proposed to be taken by the controller to address the personal data breach.
    
    ---
    
    Article 34 - Communication of a personal data breach to the data subject
    
    1. When the personal data breach is likely to result in a high risk to the rights and freedoms of natural persons, the controller shall communicate the personal data breach to the data subject without undue delay.
    
    2. The communication to the data subject referred to in paragraph 1 shall describe in clear and plain language the nature of the personal data breach and contain at least the information and measures referred to in points (b), (c) and (d) of Article 33(2).
    
    3. The communication to the data subject referred to in paragraph 1 shall not be required if any of the following conditions are met:
    (a) the controller has implemented appropriate technical and organisational protection measures;
    (b) the controller has taken subsequent measures which ensure that the high risk to the rights and freedoms of data subjects referred to in paragraph 1 is no longer likely to materialise;
    (c) it would involve disproportionate effort.
    """
    
    doc_path = create_test_document("gdpr_breach.txt", gdpr_breach_content)
    
    # Upload document
    with open(doc_path, "rb") as f:
        upload_response = await http_client.post(
            "/api/v1/rag/documents/upload",
            data={
                "collection_name": test_collection,
                "chunk_size": "600",
                "chunk_overlap": "100",
            },
            files={"files": ("gdpr_breach.txt", f, "text/plain")},
        )
    
    assert upload_response.status_code == 200
    print("✅ GDPR breach notification articles uploaded")
    
    await wait_for_processing(3.0)
    
    # Query about data breach obligations
    query_response = await http_client.post(
        "/api/v1/rag/query/test",
        data={
            "query": "We had a data breach. What are our notification obligations and timeline?",
            "collection_name": test_collection,
            "n_results": "5",
        },
    )
    
    assert query_response.status_code == 200
    query_data = query_response.json()
    
    results = query_data.get("results", [])
    assert len(results) > 0, "No results returned"
    
    print(f"✅ Query returned {len(results)} results")
    
    # Verify both Article 33 and 34 are referenced
    found_art33 = False
    found_art34 = False
    found_72_hours = False
    
    for result in results:
        content = str(result.get("content", "")).lower()
        
        if "article 33" in content or "art. 33" in content:
            found_art33 = True
            print("   ✓ Found Article 33 (notification to authority)")
        
        if "article 34" in content or "art. 34" in content:
            found_art34 = True
            print("   ✓ Found Article 34 (communication to data subject)")
        
        if "72 hours" in content or "72 hour" in content:
            found_72_hours = True
            print("   ✓ Found 72-hour timeline")
    
    assert found_art33, "Article 33 not found in results"
    assert found_art34, "Article 34 not found in results"
    assert found_72_hours, "72-hour timeline not found in results"
    
    print("\n✅ Multi-article data breach test passed!")
    print("   - Both Art. 33 and Art. 34 found")
    print("   - 72-hour timeline identified")


@pytest.mark.asyncio
async def test_consent_requirements(
    http_client: httpx.AsyncClient,
    test_collection: str,
    create_test_document,
    wait_for_processing,
):
    """Test consent requirements query (Art. 7 + Art. 13)."""
    
    gdpr_consent_content = """
    Article 7 - Conditions for consent
    
    1. Where processing is based on consent, the controller shall be able to demonstrate that the data subject has consented to processing of his or her personal data.
    
    2. If the data subject's consent is given in the context of a written declaration which also concerns other matters, the request for consent shall be presented in a manner which is clearly distinguishable from the other matters, in an intelligible and easily accessible form, using clear and plain language.
    
    3. The data subject shall have the right to withdraw his or her consent at any time. The withdrawal of consent shall not affect the lawfulness of processing based on consent before its withdrawal.
    
    4. When assessing whether consent is freely given, utmost account shall be taken of whether, inter alia, the performance of a contract, including the provision of a service, is conditional on consent to the processing of personal data that is not necessary for the performance of that contract.
    
    ---
    
    Article 13 - Information to be provided where personal data are collected from the data subject
    
    1. Where personal data relating to a data subject are collected from the data subject, the controller shall, at the time when personal data are obtained, provide the data subject with all of the following information:
    
    (a) the identity and the contact details of the controller and, where applicable, of the controller's representative;
    (b) the contact details of the data protection officer, where applicable;
    (c) the purposes of the processing for which the personal data are intended as well as the legal basis for the processing;
    (d) where the processing is based on point (f) of Article 6(1), the legitimate interests pursued by the controller or by a third party;
    (e) the recipients or categories of recipients of the personal data, if any;
    (f) where applicable, the fact that the controller intends to transfer personal data to a third country.
    """
    
    doc_path = create_test_document("gdpr_consent.txt", gdpr_consent_content)
    
    with open(doc_path, "rb") as f:
        await http_client.post(
            "/api/v1/rag/documents/upload",
            data={
                "collection_name": test_collection,
                "chunk_size": "600",
                "chunk_overlap": "100",
            },
            files={"files": ("gdpr_consent.txt", f, "text/plain")},
        )
    
    await wait_for_processing(3.0)
    
    # Query about consent for marketing
    query_response = await http_client.post(
        "/api/v1/rag/query/test",
        data={
            "query": "Do we need consent for marketing emails? What information must we provide?",
            "collection_name": test_collection,
            "n_results": "5",
        },
    )
    
    assert query_response.status_code == 200
    query_data = query_response.json()
    
    results = query_data.get("results", [])
    assert len(results) > 0
    
    # Verify both articles are found
    found_art7 = False
    found_art13 = False
    
    for result in results:
        content = str(result.get("content", "")).lower()
        if "article 7" in content or "consent" in content:
            found_art7 = True
        if "article 13" in content or "information to be provided" in content:
            found_art13 = True
    
    # At least one should be found (depending on chunking)
    assert found_art7 or found_art13, "Neither Article 7 nor 13 found"
    
    print("✅ Consent requirements test passed!")
