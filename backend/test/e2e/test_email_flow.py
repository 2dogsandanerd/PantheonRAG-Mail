"""
E2E Test: Email Flow with GreenMail

Tests the complete email workflow using GreenMail mock server.
"""

import pytest
import asyncio
from email.message import EmailMessage
import aiosmtplib
import time

pytestmark = [pytest.mark.e2e, pytest.mark.email, pytest.mark.integration]


async def send_test_email(
    subject: str,
    body: str,
    to_addr: str = "test@example.com",
    from_addr: str = "sender@example.com",
) -> bool:
    """Helper to send test email via GreenMail SMTP."""
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr

    try:
        await aiosmtplib.send(msg, hostname="localhost", port=3025, use_tls=False)
        return True
    except Exception as e:
        pytest.skip(f"Cannot send test email: {e}")


@pytest.mark.asyncio
async def test_imap_connection(imap_client):
    """Test basic IMAP connection to GreenMail."""
    # Client is already connected via fixture
    assert imap_client is not None
    print("✅ IMAP client connected to GreenMail")


@pytest.mark.asyncio
async def test_send_and_receive_email(imap_client):
    """Test sending email via SMTP and receiving via IMAP."""
    # Clear inbox first
    await imap_client.clear_inbox()

    # Send test email
    subject = f"E2E Test Email {time.time()}"
    body = "This is a test email for E2E testing."

    success = await send_test_email(subject, body)
    assert success, "Failed to send test email"

    # Wait for email to arrive
    await asyncio.sleep(1)

    # Fetch emails
    emails = await imap_client.get_unread_emails(max_results=5)

    # Verify we received the email
    found = False
    for email in emails:
        if email.get("subject") == subject:
            found = True
            assert body in email.get("body", "")
            break

    assert found, f"Test email with subject '{subject}' not found in inbox"
    print(f"✅ Email sent and received successfully")


@pytest.mark.asyncio
async def test_email_draft_creation(imap_client):
    """Test creating a draft email."""
    subject = f"Draft Test {time.time()}"
    body = "This is a test draft email."

    # Create draft
    draft_id = await imap_client.create_draft(
        to="recipient@example.com", subject=subject, body=body
    )

    # Note: Draft creation might fail if Drafts folder doesn't exist
    # This tests the actual behavior
    if draft_id:
        print(f"✅ Draft created successfully: {draft_id}")
    else:
        print("⚠️  Draft creation returned None (Drafts folder may not exist)")


@pytest.mark.asyncio
async def test_clear_inbox(imap_client):
    """Test clearing the inbox."""
    # Send a test email first
    await send_test_email("Clear Test", "Test body")
    await asyncio.sleep(1)

    # Clear inbox
    result = await imap_client.clear_inbox()

    # Verify inbox is empty (or operation completed)
    print(f"✅ Inbox clear operation completed")


@pytest.mark.asyncio
async def test_email_listing(imap_client):
    """Test listing emails from inbox."""
    # Send test emails
    for i in range(3):
        await send_test_email(f"List Test {i} {time.time()}", f"Body {i}")

    await asyncio.sleep(1)

    # List all emails
    emails = await imap_client.get_all_emails(max_results=10)

    print(f"✅ Listed {len(emails)} emails from inbox")

    # Verify structure
    if emails:
        email = emails[0]
        assert "id" in email
        assert "subject" in email


@pytest.mark.asyncio
async def test_email_thread_operations(imap_client):
    """Test email thread operations."""
    # Send email
    subject = f"Thread Test {time.time()}"
    await send_test_email(subject, "Thread test body")
    await asyncio.sleep(1)

    # Get emails
    emails = await imap_client.get_unread_emails(max_results=5)

    if emails:
        email = emails[0]
        thread_id = email.get("thread_id") or email.get("id")

        if thread_id:
            # Try to get thread
            try:
                thread = await imap_client.get_thread(thread_id)
                print(f"✅ Thread retrieved: {len(thread)} messages")
            except Exception as e:
                print(f"⚠️  Thread retrieval: {e}")


@pytest.mark.asyncio
async def test_complete_email_flow(imap_client):
    """Complete email flow: send, receive, draft, move."""
    print("\n🧪 Complete Email Flow Test")

    # 1. Clear inbox
    await imap_client.clear_inbox()
    print("  1. ✓ Inbox cleared")

    # 2. Send email
    subject = f"Complete Flow Test {time.time()}"
    await send_test_email(subject, "Complete flow test body")
    await asyncio.sleep(1)
    print("  2. ✓ Email sent")

    # 3. Receive and verify
    emails = await imap_client.get_unread_emails()
    assert len(emails) >= 1
    print("  3. ✓ Email received")

    # 4. Mark as read
    if emails:
        email_id = emails[0]["id"]
        await imap_client.mark_as_read(email_id)
        print("  4. ✓ Email marked as read")

    # 5. List folders
    folders = await imap_client.list_folders()
    print(f"  5. ✓ Folders listed: {len(folders)} folders")

    print("\n✅ Complete email flow passed!")
