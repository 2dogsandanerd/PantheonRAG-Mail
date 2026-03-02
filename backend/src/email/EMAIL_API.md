EMAIL API DOCUMENTATION

## Email Service API

### Overview
The Email Service provides RESTful endpoints for email functionality including listing emails, sending emails, and managing email configurations.

### Base URL
- Development: `http://localhost:8001`
- Production: `https://your-domain.com`

### Authentication
Email functionality requires either:
- OAuth2 credentials (for Gmail)
- IMAP/SMTP credentials (for other providers)

Credentials are stored in the user session.

## API Endpoints

### 1. List Emails

#### GET /api/v1/email/list
#### GET /email/list (Legacy)

Retrieve a list of emails from the user's inbox.

**Parameters:**
- `maxEmails` (query, optional): Maximum number of emails to return (default: 20)
- `max_emails` (query, optional): Legacy parameter name

**Response:**
```json
{
  "emails": [
    {
      "id": "email_id_123",
      "threadId": "thread_123",
      "subject": "Email Subject",
      "sender": "sender@example.com",
      "date": "2024-01-01T12:00:00Z",
      "snippet": "Email preview text...",
      "unread": true,
      "has_attachments": false,
      "provider": "gmail"
    }
  ],
  "total": 1,
  "provider": "gmail",
  "status": "success"
}
```

**Error Response:**
```json
{
  "emails": [],
  "total": 0,
  "provider": "none",
  "status": "error",
  "error": "Email service not available",
  "details": "No email client configured"
}
```

### 2. Send Email

#### POST /api/v1/email/send

Send an email via the configured email service.

**Request Body:**
```json
{
  "to": "recipient@example.com",
  "subject": "Email Subject",
  "body": "Email content",
  "reply_to": "optional@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email sent successfully",
  "to": "recipient@example.com",
  "subject": "Email Subject"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "No email client configured",
  "details": "Email credentials not available in session"
}
```

### 3. Email Configuration (Future Endpoint)

#### GET /api/v1/email/config

Get current email configuration status.

**Response:**
```json
{
  "provider": "gmail",
  "email_address": "user@gmail.com",
  "imap_configured": true,
  "smtp_configured": true,
  "connection_status": "connected"
}
```

## Error Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (no credentials)
- `403` - Forbidden (invalid credentials)
- `500` - Internal Server Error (service failure)
- `503` - Service Unavailable (email service down)

## Supported Providers

- **Gmail** - OAuth2 and IMAP/SMTP
- **Outlook** - IMAP/SMTP (outlook.office365.com)
- **Yahoo** - IMAP/SMTP (imap.mail.yahoo.com)
- **iCloud** - IMAP/SMTP (imap.mail.me.com)
- **GMX** - IMAP/SMTP (imap.gmx.net)
- **Web.de** - IMAP/SMTP (imap.web.de)

## Provider Configuration Details

### Gmail
- **IMAP**: imap.gmail.com:993 (SSL)
- **SMTP**: smtp.gmail.com:587 (TLS)
- **OAuth2**: Supported via Google API
- **App Passwords**: Required for IMAP/SMTP

### Outlook
- **IMAP**: outlook.office365.com:993 (SSL)
- **SMTP**: smtp.office365.com:587 (TLS)
- **App Passwords**: Required

### Yahoo
- **IMAP**: imap.mail.yahoo.com:993 (SSL)
- **SMTP**: smtp.mail.yahoo.com:587 (TLS)
- **App Passwords**: Required

### iCloud
- **IMAP**: imap.mail.me.com:993 (SSL)
- **SMTP**: smtp.mail.me.com:587 (TLS)
- **App Passwords**: Required

### GMX
- **IMAP**: imap.gmx.net:993 (SSL)
- **SMTP**: mail.gmx.net:587 (TLS)

### Web.de
- **IMAP**: imap.web.de:993 (SSL)
- **SMTP**: smtp.web.de:587 (TLS)

## Integration Examples

### JavaScript/Frontend
```javascript
// List emails
const response = await fetch('/api/v1/email/list?maxEmails=10');
const data = await response.json();

// Send email
const sendResponse = await fetch('/api/v1/email/send', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    to: 'user@example.com',
    subject: 'Hello',
    body: 'Test message'
  })
});
```

### Python/Backend
```python
from src.email.unified.factory import get_email_client

# Get email client
config = {"EMAIL_PROVIDER": "gmail", "EMAIL_USER": "...", "EMAIL_PASSWORD": "..."}
client = get_email_client(config, session)

# Test connection
connected = await client.test_connection()

# List emails
emails = await client.list_emails(max_results=10)
```
