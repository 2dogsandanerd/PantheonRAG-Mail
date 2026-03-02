EMAIL SERVICE SETUP GUIDE

## Prerequisites

### System Requirements
- Python 3.8+
- FastAPI application
- Virtual environment (recommended)

### Dependencies
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip install loguru
pip install fastapi uvicorn
pip install httpx  # For API testing
```

## Installation

### 1. Install Dependencies
```bash
cd /path/to/your/project
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Verify Installation
```bash
python3 -c "import google.auth; print('Google API OK')"
python3 -c "from src.email.clients.gmail_oauth import GmailClient; print('Email modules OK')"
python3 -c "import httpx; print('httpx OK')"
```

### 3. Validate Email Module Structure
```bash
python3 src/email/validate_imports.py
python3 src/email/config_validator.py
```

## Configuration

### Gmail OAuth Setup

1. **Google Cloud Console**
   - Create project at https://console.cloud.google.com
   - Enable Gmail API
   - Create OAuth2 credentials (Desktop application)
   - Download credentials.json

2. **Environment Variables**
   ```bash
   export GOOGLE_CLIENT_ID="your_client_id"
   export GOOGLE_CLIENT_SECRET="your_client_secret"
   ```

3. **OAuth Flow**
   ```python
   # First time setup - run authorization flow
   from src.email.clients.gmail_oauth import GmailClient

   credentials = {
       "client_id": "your_client_id",
       "client_secret": "your_client_secret"
   }

   client = GmailClient(credentials)
   # Follow OAuth flow in browser
   ```

### IMAP/SMTP Setup

1. **Environment Variables**
   ```bash
   export EMAIL_PROVIDER="gmail"  # or outlook, yahoo, icloud, gmx, web_de
   export EMAIL_USER="your@email.com"
   export EMAIL_PASSWORD="your_app_password"
   ```

2. **App Passwords (Required for most providers)**
   - **Gmail**: Enable 2FA, create app password at myaccount.google.com
   - **Outlook**: Enable 2FA, create app password at account.microsoft.com
   - **Yahoo**: Generate app password at account.yahoo.com
   - **iCloud**: Generate app-specific password at appleid.apple.com

3. **Provider-Specific Settings**
   ```python
   # All provider configurations are pre-configured in:
   # src/email/providers/provider_configs.py

   from src.email.providers.provider_configs import EMAIL_PROVIDERS
   print(EMAIL_PROVIDERS.keys())  # ['gmail', 'outlook', 'yahoo', 'icloud', 'gmx', 'web_de']
   ```

## Usage

### 1. Start the Server
```bash
python3 -m uvicorn src.main:app --reload --port 8001
```

### 2. Test Email Functionality
```bash
# Test email list (will return error without credentials)
curl "http://localhost:8001/api/v1/email/list?maxEmails=5"

# Test email send (will return error without credentials)
curl -X POST "http://localhost:8001/api/v1/email/send" \
     -H "Content-Type: application/json" \
     -d '{"to":"test@example.com","subject":"Test","body":"Hello"}'

# Test legacy endpoint
curl "http://localhost:8001/email/list?max_emails=3"
```

### 3. Integration Example
```python
from src.email.unified.factory import get_email_client
from src.email.providers.provider_configs import create_email_config_from_provider

# Method 1: Using unified factory
config = {
    "EMAIL_PROVIDER": "gmail",
    "EMAIL_USER": "user@gmail.com",
    "EMAIL_PASSWORD": "app_password"
}
client = get_email_client(config, session)

# Method 2: Using provider config
email_config = create_email_config_from_provider(
    provider="gmail",
    email_address="user@gmail.com",
    password="app_password"
)
from src.email.unified.client import UnifiedEmailClient
client = UnifiedEmailClient(email_config)

# Test connection
connected = await client.test_connection()

# List emails
emails = await client.list_emails(max_results=10)
```

### 4. Session Integration
```python
# In FastAPI application
from src.session.service_manager import FastAPIServiceManager

# Session setup (simplified)
session_proxy.set('email_provider', 'gmail')
session_proxy.set('email_user', 'user@gmail.com')
session_proxy.set('email_password', 'app_password')

# Service initialization
service_manager = FastAPIServiceManager(session_manager)
success = await service_manager.initialize_services(session_proxy)

# Email client should now be available in session
email_client = session_proxy.get('email_client')
```

## Testing

### Run All Email Tests
```bash
# Test provider configurations
python3 src/email/test_imap_providers.py

# Test end-to-end functionality
python3 src/email/test_email_e2e.py

# Test API endpoints (starts server automatically)
python3 src/email/test_api_integration.py

# Test module integration
python3 src/email/test_module_integration.py

# Test exception handling
python3 src/email/test_exception_handling.py
```

### Validation Scripts
```bash
# Validate imports and dependencies
python3 src/email/validate_imports.py

# Check provider configurations
python3 src/email/config_validator.py

# Test dependencies
python3 src/email/test_dependencies.py
```

## Troubleshooting

### Common Issues

1. **"No module named 'google'"**
   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

2. **"Authentication failed"**
   - Check credentials are correct
   - Use app passwords for Gmail/Outlook
   - Enable 2FA if required by provider
   - Verify IMAP/SMTP is enabled in email account settings

3. **"Connection refused"**
   - Check IMAP/SMTP server settings
   - Verify firewall allows connections on ports 993 (IMAP) and 587 (SMTP)
   - Some networks block email ports

4. **"Service not available"**
   - Verify FastAPI server is running
   - Check logs for detailed errors
   - Ensure session management is working

5. **"Import errors"**
   ```bash
   # Run import validation
   python3 src/email/validate_imports.py

   # Check Python path
   echo $PYTHONPATH
   export PYTHONPATH=$PYTHONPATH:/path/to/your/project
   ```

6. **"httpx not found" (during API testing)**
   ```bash
   pip install httpx
   ```

### Debug Mode
```bash
# Enable detailed logging
export LOG_LEVEL="DEBUG"
python3 -m uvicorn src.main:app --reload --log-level debug --port 8001

# Run with verbose output
python3 -v src/email/test_email_e2e.py
```

### Provider-Specific Troubleshooting

#### Gmail
- Enable "Less secure app access" (if not using OAuth2)
- Use app-specific passwords
- Check Google account security settings

#### Outlook
- Enable IMAP in Outlook settings
- Use modern authentication
- Check Microsoft account security

#### Yahoo
- Enable "Allow apps that use less secure sign in"
- Generate app password in account settings

## Security Considerations

### Credential Storage
- Never commit credentials to version control
- Use environment variables or secure credential stores
- Implement proper session timeout
- Consider OAuth2 for production Gmail integration

### Network Security
- Always use SSL/TLS connections
- Verify certificate chains
- Monitor for suspicious connection patterns

### Error Handling
- Don't expose credentials in error messages
- Log security events appropriately
- Implement rate limiting for API endpoints
