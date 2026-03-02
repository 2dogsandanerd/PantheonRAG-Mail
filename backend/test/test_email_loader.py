"""
Tests for EmailLoader and MboxLoader (Phase 10a).

Tests cover:
- .eml file loading
- .mbox archive loading
- Metadata extraction
- Body extraction (text/plain, multipart)
- Error handling
"""

import pytest
import tempfile
from pathlib import Path
from src.services.loaders.email_loader import EmailLoader, MboxLoader


class TestEmailLoader:
    """Test suite for EmailLoader (.eml files)."""

    def test_load_simple_eml_file(self):
        """Test loading a simple plain-text email."""
        # Create test .eml file
        email_content = """From: sender@example.com
To: recipient@example.com
Subject: Test Email
Date: Mon, 04 Nov 2024 15:00:00 +0000
Message-ID: <test123@example.com>

This is the email body.
It has multiple lines.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
            f.write(email_content)
            temp_path = f.name

        try:
            loader = EmailLoader(temp_path)
            docs = loader.load()

            assert len(docs) == 1
            doc = docs[0]

            # Check metadata
            assert doc.metadata['from'] == 'sender@example.com'
            assert doc.metadata['to'] == 'recipient@example.com'
            assert doc.metadata['subject'] == 'Test Email'
            assert doc.metadata['message_id'] == '<test123@example.com>'
            assert doc.metadata['file_type'] == '.eml'

            # Check body
            assert 'This is the email body' in doc.text
            assert 'multiple lines' in doc.text

        finally:
            Path(temp_path).unlink()

    def test_load_multipart_eml_file(self):
        """Test loading a multipart email (text/plain)."""
        email_content = """From: sender@example.com
To: recipient@example.com
Subject: Multipart Test
Content-Type: multipart/alternative; boundary="boundary123"

--boundary123
Content-Type: text/plain; charset="utf-8"

Plain text version of the email.

--boundary123
Content-Type: text/html; charset="utf-8"

<html><body>HTML version</body></html>

--boundary123--
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
            f.write(email_content)
            temp_path = f.name

        try:
            loader = EmailLoader(temp_path)
            docs = loader.load()

            assert len(docs) == 1
            # Should extract plain text, not HTML
            assert 'Plain text version' in docs[0].text
            assert '<html>' not in docs[0].text

        finally:
            Path(temp_path).unlink()

    def test_load_email_with_thread_headers(self):
        """Test that thread detection headers are captured."""
        email_content = """From: sender@example.com
To: recipient@example.com
Subject: Re: Previous conversation
In-Reply-To: <original123@example.com>
References: <original123@example.com> <reply456@example.com>
Message-ID: <reply789@example.com>

This is a reply.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
            f.write(email_content)
            temp_path = f.name

        try:
            loader = EmailLoader(temp_path)
            docs = loader.load()

            assert docs[0].metadata['in_reply_to'] == '<original123@example.com>'
            assert '<original123@example.com>' in docs[0].metadata['references']

        finally:
            Path(temp_path).unlink()

    def test_load_nonexistent_file_raises_error(self):
        """Test that loading non-existent file raises FileNotFoundError."""
        loader = EmailLoader('/tmp/nonexistent_email_12345.eml')

        with pytest.raises(FileNotFoundError):
            loader.load()

    def test_load_empty_email_body(self):
        """Test loading email with no body (metadata only)."""
        email_content = """From: sender@example.com
To: recipient@example.com
Subject: Empty Email

"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
            f.write(email_content)
            temp_path = f.name

        try:
            loader = EmailLoader(temp_path)
            docs = loader.load()

            # Should still load, but with empty/whitespace body
            assert len(docs) == 1
            assert docs[0].metadata['subject'] == 'Empty Email'

        finally:
            Path(temp_path).unlink()


class TestMboxLoader:
    """Test suite for MboxLoader (.mbox archives)."""

    def test_load_mbox_with_multiple_emails(self):
        """Test loading mbox archive with multiple emails."""
        mbox_content = """From sender1@example.com Mon Nov 04 15:00:00 2024
From: sender1@example.com
To: recipient@example.com
Subject: First Email
Date: Mon, 04 Nov 2024 15:00:00 +0000

Body of first email.

From sender2@example.com Mon Nov 04 16:00:00 2024
From: sender2@example.com
To: recipient@example.com
Subject: Second Email
Date: Mon, 04 Nov 2024 16:00:00 +0000

Body of second email.

"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mbox', delete=False) as f:
            f.write(mbox_content)
            temp_path = f.name

        try:
            loader = MboxLoader(temp_path)
            docs = loader.load()

            assert len(docs) == 2

            # Check first email
            assert docs[0].metadata['subject'] == 'First Email'
            assert docs[0].metadata['email_index'] == 0
            assert 'Body of first email' in docs[0].text

            # Check second email
            assert docs[1].metadata['subject'] == 'Second Email'
            assert docs[1].metadata['email_index'] == 1
            assert 'Body of second email' in docs[1].text

        finally:
            Path(temp_path).unlink()

    def test_mbox_max_emails_limit(self):
        """Test that max_emails limit is respected."""
        # Create mbox with 3 emails
        mbox_content = """From sender1@example.com Mon Nov 04 15:00:00 2024
From: sender1@example.com
Subject: Email 1

Body 1

From sender2@example.com Mon Nov 04 16:00:00 2024
From: sender2@example.com
Subject: Email 2

Body 2

From sender3@example.com Mon Nov 04 17:00:00 2024
From: sender3@example.com
Subject: Email 3

Body 3

"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mbox', delete=False) as f:
            f.write(mbox_content)
            temp_path = f.name

        try:
            # Load with max_emails=2
            loader = MboxLoader(temp_path, max_emails=2)
            docs = loader.load()

            # Should only load first 2 emails
            assert len(docs) == 2
            assert docs[0].metadata['subject'] == 'Email 1'
            assert docs[1].metadata['subject'] == 'Email 2'

        finally:
            Path(temp_path).unlink()

    def test_mbox_skips_empty_emails(self):
        """Test that emails with no body are skipped."""
        mbox_content = """From sender1@example.com Mon Nov 04 15:00:00 2024
From: sender1@example.com
Subject: Email with body

This has a body.

From sender2@example.com Mon Nov 04 16:00:00 2024
From: sender2@example.com
Subject: Email without body

"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mbox', delete=False) as f:
            f.write(mbox_content)
            temp_path = f.name

        try:
            loader = MboxLoader(temp_path)
            docs = loader.load()

            # Should only load the email with body
            assert len(docs) == 1
            assert docs[0].metadata['subject'] == 'Email with body'

        finally:
            Path(temp_path).unlink()

    def test_mbox_nonexistent_file_raises_error(self):
        """Test that loading non-existent mbox raises FileNotFoundError."""
        loader = MboxLoader('/tmp/nonexistent_mbox_12345.mbox')

        with pytest.raises(FileNotFoundError):
            loader.load()

    def test_mbox_metadata_completeness(self):
        """Test that all metadata fields are extracted."""
        mbox_content = """From sender@example.com Mon Nov 04 15:00:00 2024
From: sender@example.com
To: recipient@example.com
Cc: cc@example.com
Subject: Complete Metadata Test
Date: Mon, 04 Nov 2024 15:00:00 +0000
Message-ID: <msg123@example.com>
In-Reply-To: <original@example.com>
References: <ref1@example.com> <ref2@example.com>

Email body here.

"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mbox', delete=False) as f:
            f.write(mbox_content)
            temp_path = f.name

        try:
            loader = MboxLoader(temp_path)
            docs = loader.load()

            assert len(docs) == 1
            metadata = docs[0].metadata

            assert metadata['from'] == 'sender@example.com'
            assert metadata['to'] == 'recipient@example.com'
            assert metadata['cc'] == 'cc@example.com'
            assert metadata['subject'] == 'Complete Metadata Test'
            assert metadata['message_id'] == '<msg123@example.com>'
            assert metadata['in_reply_to'] == '<original@example.com>'
            assert '<ref1@example.com>' in metadata['references']

        finally:
            Path(temp_path).unlink()


class TestEmailLoaderEdgeCases:
    """Test edge cases and error handling."""

    def test_email_with_special_characters(self):
        """Test email with UTF-8 special characters."""
        email_content = """From: sender@example.com
To: recipient@example.com
Subject: Test with Umlauts äöü and Emoji 🎉

Body with special characters: Größe, Straße, 日本語
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False, encoding='utf-8') as f:
            f.write(email_content)
            temp_path = f.name

        try:
            loader = EmailLoader(temp_path)
            docs = loader.load()

            assert len(docs) == 1
            assert 'Umlauts' in docs[0].metadata['subject']
            assert 'special characters' in docs[0].text

        finally:
            Path(temp_path).unlink()

    def test_mbox_unlimited_emails(self):
        """Test mbox with max_emails=None (unlimited)."""
        mbox_content = """From sender@example.com Mon Nov 04 15:00:00 2024
From: sender@example.com
Subject: Email 1

Body 1

From sender@example.com Mon Nov 04 16:00:00 2024
From: sender@example.com
Subject: Email 2

Body 2

"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mbox', delete=False) as f:
            f.write(mbox_content)
            temp_path = f.name

        try:
            loader = MboxLoader(temp_path, max_emails=None)
            docs = loader.load()

            # Should load all emails
            assert len(docs) == 2

        finally:
            Path(temp_path).unlink()
