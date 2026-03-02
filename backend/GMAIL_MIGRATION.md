# Gmail OAuth Migration Notice

Gmail OAuth support has been removed from this project.

## Why?
- Simplified codebase
- IMAP works for all providers (Gmail, Outlook, etc.)
- Easier for customers to configure

## Migration Steps

If you were using Gmail OAuth before:

1. **Enable IMAP in Gmail**:
   - Go to: https://mail.google.com/mail/u/0/#settings/fwdandpop
   - Enable IMAP access

2. **Create App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select 'Mail' and 'Other (Custom name)'
   - Copy the 16-character password

3. **Update .env**:
   ```bash
   EMAIL_PROVIDER=imap
   EMAIL_USER=your@gmail.com
   EMAIL_PASSWORD=your_16_char_app_password
   IMAP_HOST=imap.gmail.com
   IMAP_PORT=993
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   ```

4. **Remove old OAuth files**:
   - Delete: credentials.json, token.json, client_secret_*.json

5. **Restart application**

## Questions?
See: /planung/1_neustart/async/PHASE_0_GMAIL_DEAKTIVIERUNG.md

