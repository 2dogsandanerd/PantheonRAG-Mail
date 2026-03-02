
import pytest
import asyncio
import aiosmtplib
from email.message import EmailMessage
import time
from src.core.email_clients.imap_client import IMAPClient

# GreenMail Configuration (matches docker-compose-test.yml)
IMAP_HOST = "localhost"
IMAP_PORT = 3143
SMTP_HOST = "localhost"
SMTP_PORT = 3025
TEST_USER = "test@example.com"
TEST_PASS = "password"  # GreenMail with auth disabled accepts any password

@pytest.fixture
async def imap_client():
    """Fixture to provide a connected IMAPClient"""
    config = {
        'EMAIL_USER': TEST_USER,
        'EMAIL_PASSWORD': TEST_PASS,
        'IMAP_HOST': IMAP_HOST,
        'IMAP_PORT': IMAP_PORT,
        'SMTP_HOST': SMTP_HOST,
        'SMTP_PORT': SMTP_PORT
    }
    client = IMAPClient(session_state={}, config=config)
    connected = await client.is_authenticated()
    assert connected, "Failed to connect to GreenMail IMAP"
    yield client
    await client.close()

async def send_test_email(subject, body, to_addr=TEST_USER, from_addr="sender@example.com"):
    """Helper to send email via SMTP to GreenMail"""
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr

    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            use_tls=False
        )
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

@pytest.mark.asyncio
async def test_fetch_unread_emails(imap_client):
    """Test fetching unread emails from INBOX"""
    # 1. Clear Inbox first
    await imap_client.clear_inbox()
    
    # 2. Send a test email
    subject = f"Test Email {time.time()}"
    body = "This is a test email body."
    await send_test_email(subject, body)
    
    # Give GreenMail a moment to process
    await asyncio.sleep(1)

    # 3. Fetch unread emails
    emails = await imap_client.get_unread_emails(max_results=5)
    
    # 4. Verify
    assert len(emails) >= 1
    found = False
    for email in emails:
        if email['subject'] == subject:
            assert email['body'].strip() == body
            found = True
            break
    
    assert found, f"Email with subject '{subject}' not found"

@pytest.mark.asyncio
async def test_create_draft(imap_client):
    """Test creating a draft email"""
    subject = f"Draft {time.time()}"
    body = "This is a draft body."
    
    # 1. Create draft
    draft_id = await imap_client.create_draft(
        to="recipient@example.com",
        subject=subject,
        body=body
    )
    
    assert draft_id is not None
    
    # 2. Verify it exists (Implementation specific, checks Drafts folder)
    # Note: Our IMAPClient check_draft_status is simplified and might need adjustment 
    # if it relies on specific internal IDs, but we can list folder content.
    
    folders = await imap_client.list_folders()
    # Ensure Drafts folder exists logic is handled by client, 
    # but let's check if we can find the message in Drafts
    
    # We need to manually verify via IMAP lib or assume create_draft success means it's there.
    # Let's try to fetch from Drafts folder if method supported or raw
    
    # Using public method if available or raw client
    # The client lists folder names decoded, let's look for Drafts
    draft_folder = next((f for f in folders if "Draft" in f), "Drafts")
    
    # Search in draft folder
    await imap_client.imap_client.select(f'"{draft_folder}"')
    status, messages = await imap_client.imap_client.search('ALL')
    assert status == 'OK'
    assert len(messages[0].split()) >= 1

@pytest.mark.asyncio
async def test_move_email_to_trash(imap_client):
    """Test moving an email to another folder (simulating delete/trash)"""
    # 1. Send email
    subject = f"To Move {time.time()}"
    await send_test_email(subject, "Move me")
    await asyncio.sleep(1)
    
    # 2. Get ID
    emails = await imap_client.get_unread_emails()
    target_email = next((e for e in emails if e['subject'] == subject), None)
    assert target_email is not None
    
    # 3. Move to Trash (Mocking label behavior)
    # GreenMail doesn't have default "Trash" maybe, let's use "INBOX" -> "Qual" 
    # But usually creating a folder might be needed. IMAPClient assumes folders exist or fails?
    # IMAPClient doesn't create folders. 
    # We will try to move to 'Trash' assuming GreenMail has it or we create it raw.
    
    # Create Trash folder just in case
    await imap_client.imap_client.create('Trash')
    
    success = await imap_client.move_to_label(target_email['id'], 'Trash')
    assert success is True
    
    # 4. Verify gone from Inbox
    # Select Inbox
    await imap_client.imap_client.select('"INBOX"')
    # Search for this specific email? Hard without ID persistence check, 
    # but let's check count or if get_email_details fails.
    
    # Re-fetch unread should not return it
    emails_after = await imap_client.get_unread_emails()
    assert not any(e['subject'] == subject for e in emails_after)
