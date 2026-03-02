#!/usr/bin/env python3
"""
Send Demo Emails to GreenMail

This script sends test emails to the local GreenMail server for E2E testing
and user demonstrations.

Usage:
    python send_demo_email.py [subject] [body] [to_address]

Examples:
    python send_demo_email.py
    python send_demo_email.py "Test Subject" "Test body content"
    python send_demo_email.py "Projekt Alpha" "Meeting um 14 Uhr" demo@example.com
"""

import asyncio
import sys
from email.message import EmailMessage
from datetime import datetime

try:
    import aiosmtplib
except ImportError:
    print("❌ Error: aiosmtplib not installed")
    print("   Install with: pip install aiosmtplib")
    sys.exit(1)


# GreenMail Configuration
SMTP_HOST = "localhost"
SMTP_PORT = 3025
DEFAULT_FROM = "demo-sender@example.com"
DEFAULT_TO = "demo@example.com"


async def send_email(
    subject: str, body: str, to_addr: str = DEFAULT_TO, from_addr: str = DEFAULT_FROM
) -> bool:
    """Send an email via GreenMail SMTP."""
    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

    try:
        await aiosmtplib.send(msg, hostname=SMTP_HOST, port=SMTP_PORT, use_tls=False)
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def create_sample_emails():
    """Create sample email content for demos."""
    return [
        {
            "subject": "Projekt Alpha - Status Update",
            "body": """Hallo Team,

hier ist ein kurzes Update zum Projekt Alpha:

✅ Backend API fertiggestellt
✅ Datenbank-Schema implementiert
🔄 Frontend in Entwicklung
⏳ Tests in Planung

Nächster Meilenstein: Integrationstests

Viele Grüße,
Das Entwicklerteam
""",
        },
        {
            "subject": "Kundenanfrage #1234",
            "body": """Sehr geehrte Damen und Herren,

wir haben Ihre Anfrage bezüglich unseres Kundenmanagement-Systems erhalten.

Gerne bieten wir Ihnen eine persönliche Demo an. Wäre nächste Woche 
Dienstag um 14:00 Uhr für Sie passend?

Unser System bietet:
- 360-Grad-Kundensicht
- Automatische E-Mail-Integration
- Leistungsstarke Analytics

Mit freundlichen Grüßen
Ihr Vertriebsteam
""",
        },
        {
            "subject": "Re: Meeting für nächste Woche",
            "body": """Hallo,

ja, der Termin für nächste Woche passt gut.

Ich schlage vor:
📅 Datum: Mittwoch, 18.02.2026
🕐 Zeit: 10:00 - 11:30 Uhr
📍 Ort: Konferenzraum B / Zoom

Agenda:
1. Projektstatus (15 Min)
2. RAG System Demo (30 Min)
3. Q&A (15 Min)
4. Nächste Schritte (15 Min)

Bitte bestätigen Sie den Termin.

Beste Grüße
""",
        },
    ]


async def main():
    """Main function."""
    print("=" * 60)
    print("📧 Mail Modul Fiat - Demo Email Sender")
    print("=" * 60)
    print()
    print(f"SMTP Server: {SMTP_HOST}:{SMTP_PORT}")
    print()

    # Check if GreenMail is running
    import socket

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((SMTP_HOST, SMTP_PORT))
        sock.close()

        if result != 0:
            print(f"❌ GreenMail SMTP not accessible on port {SMTP_PORT}")
            print()
            print("Start GreenMail with:")
            print("  docker-compose -f docker-compose-test.yml up -d")
            print()
            sys.exit(1)
    except Exception as e:
        print(f"⚠️  Could not check GreenMail status: {e}")

    # Parse command line arguments
    if len(sys.argv) > 1:
        # Custom email
        subject = sys.argv[1]
        body = sys.argv[2] if len(sys.argv) > 2 else "Test email body"
        to_addr = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_TO

        print(f"Sending custom email:")
        print(f"  To: {to_addr}")
        print(f"  Subject: {subject}")
        print()

        if await send_email(subject, body, to_addr):
            print(f"✅ Email sent successfully!")
        else:
            print(f"❌ Failed to send email")
            sys.exit(1)
    else:
        # Send sample emails
        print("Sending sample demo emails...")
        print()

        samples = create_sample_emails()

        for i, email in enumerate(samples, 1):
            print(f"  {i}. {email['subject']}")

            if await send_email(email["subject"], email["body"]):
                print(f"     ✅ Sent")
            else:
                print(f"     ❌ Failed")

            # Small delay between emails
            await asyncio.sleep(0.5)

        print()
        print("=" * 60)
        print(f"✅ Sent {len(samples)} demo emails to {DEFAULT_TO}")
        print()
        print("You can now:")
        print("  1. Check the Mail Modul UI - emails should appear in inbox")
        print("  2. Run E2E tests: ./scripts/run_e2e_tests.sh")
        print(
            "  3. Test IMAP: python -c \"import imaplib; c=imaplib.IMAP4('localhost', 3143); c.login('demo@example.com', 'any')\""
        )


if __name__ == "__main__":
    asyncio.run(main())
