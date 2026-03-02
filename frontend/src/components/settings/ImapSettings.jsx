import React, { useState } from 'react';
import { 
  Stack, TextField, Button, Alert, Divider, Typography, Box,
  Paper, CircularProgress 
} from '@mui/material';
import { BugReport, Email, Security } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { testEmailConnection } from '../../api/client';

export default function ImapSettings({ config, onChange, onTest }) {
  const { t } = useTranslation();
  const [testResult, setTestResult] = useState(null);
  const [testing, setTesting] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    onChange(name, value);
  };

  const handleTest = async () => {
    if (!config.EMAIL_USER || !config.EMAIL_PASSWORD || !config.IMAP_HOST) {
      setTestResult({
        success: false,
        message: 'Please fill in email address, password, and IMAP host before testing'
      });
      return;
    }

    setTesting(true);
    setTestResult(null);

    try {
      const testConfig = {
        email_user: config.EMAIL_USER,
        email_password: config.EMAIL_PASSWORD,
        imap_host: config.IMAP_HOST,
        imap_port: config.IMAP_PORT || 993,
        smtp_host: config.SMTP_HOST,
        smtp_port: config.SMTP_PORT || 587
      };

      const result = await testEmailConnection(testConfig);
      setTestResult({
        success: result.success,
        message: result.message,
        details: result.details
      });
    } catch (error) {
      setTestResult({
        success: false,
        message: error.response?.data?.detail || error.message || 'Connection test failed'
      });
    } finally {
      setTesting(false);
    }
  };

  return (
    <Stack spacing={3}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Email color="primary" />
        <Typography variant="h6" sx={{ color: 'text.primary', fontWeight: 'bold' }}>
          {t('settings.imap.title', 'IMAP Configuration')}
        </Typography>
      </Box>

      <Alert severity="info" sx={{ bgcolor: 'background.default' }}>
        {t('settings.imap.info', 'Configure your email account settings for IMAP/SMTP access.')}
      </Alert>

      {/* Email Credentials */}
      <Paper 
        variant="outlined" 
        sx={{ 
          p: 3, 
          bgcolor: 'background.default',
          border: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold' }}>
          {t('settings.imap.credentialsTitle', 'Email Credentials')}
        </Typography>

        <TextField
          fullWidth
          label={t('settings.imap.emailAddress', 'Email Address')}
          name="EMAIL_USER"
          value={config.EMAIL_USER || ''}
          onChange={handleChange}
          placeholder="your@email.com"
          helperText={t('settings.imap.emailAddressHelp', 'Your full email address')}
          required
          sx={{
            mb: 2,
            '& .MuiOutlinedInput-root': {
              '& fieldset': { borderColor: 'divider' },
              '&:hover fieldset': { borderColor: 'text.secondary' },
              '&.Mui-focused fieldset': { borderColor: 'primary.main' }
            }
          }}
        />

        <TextField
          fullWidth
          label={t('settings.imap.emailPassword', 'Email Password')}
          name="EMAIL_PASSWORD"
          type="text"
          value={config.EMAIL_PASSWORD || ''}
          onChange={handleChange}
          placeholder="Enter app password without spaces"
          helperText={t('settings.imap.emailPasswordHelp', 'Your email password or app-specific password (visible for debugging)')}
          required
          sx={{
            '& .MuiOutlinedInput-root': {
              '& fieldset': { borderColor: 'divider' },
              '&:hover fieldset': { borderColor: 'text.secondary' },
              '&.Mui-focused fieldset': { borderColor: 'primary.main' }
            }
          }}
        />
      </Paper>

      <Divider sx={{ borderColor: 'divider' }}>
        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
          {t('settings.imap.serverSettings', 'Server Settings')}
        </Typography>
      </Divider>

      {/* IMAP Settings */}
      <Paper 
        variant="outlined" 
        sx={{ 
          p: 3, 
          bgcolor: 'background.default',
          border: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold' }}>
          {t('settings.imap.imapTitle', 'IMAP Settings (Incoming Mail)')}
        </Typography>

        <TextField
          fullWidth
          label={t('settings.imap.imapHost', 'IMAP Host')}
          name="IMAP_HOST"
          value={config.IMAP_HOST || ''}
          onChange={handleChange}
          placeholder="imap.gmail.com"
          helperText={t('settings.imap.imapHostHelp', 'IMAP server hostname')}
          required
          sx={{
            mb: 2,
            '& .MuiOutlinedInput-root': {
              '& fieldset': { borderColor: 'divider' },
              '&:hover fieldset': { borderColor: 'text.secondary' },
              '&.Mui-focused fieldset': { borderColor: 'primary.main' }
            }
          }}
        />

        <TextField
          fullWidth
          type="number"
          label={t('settings.imap.imapPort', 'IMAP Port')}
          name="IMAP_PORT"
          value={config.IMAP_PORT || 993}
          onChange={handleChange}
          inputProps={{ min: 1, max: 65535 }}
          helperText={t('settings.imap.imapPortHelp', 'IMAP server port (usually 993 for SSL)')}
          required
          sx={{
            mb: 2,
            '& .MuiOutlinedInput-root': {
              '& fieldset': { borderColor: 'divider' },
              '&:hover fieldset': { borderColor: 'text.secondary' },
              '&.Mui-focused fieldset': { borderColor: 'primary.main' }
            }
          }}
        />

        <TextField
          fullWidth
          label={t('settings.imap.watchFolder', 'Watch Folder')}
          name="IMAP_WATCH_FOLDER"
          value={config.IMAP_WATCH_FOLDER || 'INBOX'}
          onChange={handleChange}
          placeholder="INBOX"
          helperText={t('settings.imap.watchFolderHelp', 'Folder to monitor for new emails (e.g., "INBOX", "AI-Assistant", "Auto-Draft")')}
          sx={{
            '& .MuiOutlinedInput-root': {
              '& fieldset': { borderColor: 'divider' },
              '&:hover fieldset': { borderColor: 'text.secondary' },
              '&.Mui-focused fieldset': { borderColor: 'primary.main' }
            }
          }}
        />
      </Paper>

      {/* SMTP Settings */}
      <Paper 
        variant="outlined" 
        sx={{ 
          p: 3, 
          bgcolor: 'background.default',
          border: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold' }}>
          {t('settings.imap.smtpTitle', 'SMTP Settings (Outgoing Mail)')}
        </Typography>

        <TextField
          fullWidth
          label={t('settings.imap.smtpHost', 'SMTP Host')}
          name="SMTP_HOST"
          value={config.SMTP_HOST || ''}
          onChange={handleChange}
          placeholder="smtp.gmail.com"
          helperText={t('settings.imap.smtpHostHelp', 'SMTP server hostname')}
          required
          sx={{
            mb: 2,
            '& .MuiOutlinedInput-root': {
              '& fieldset': { borderColor: 'divider' },
              '&:hover fieldset': { borderColor: 'text.secondary' },
              '&.Mui-focused fieldset': { borderColor: 'primary.main' }
            }
          }}
        />

        <TextField
          fullWidth
          type="number"
          label={t('settings.imap.smtpPort', 'SMTP Port')}
          name="SMTP_PORT"
          value={config.SMTP_PORT || 587}
          onChange={handleChange}
          inputProps={{ min: 1, max: 65535 }}
          helperText={t('settings.imap.smtpPortHelp', 'SMTP server port (usually 587 for TLS)')}
          required
          sx={{
            '& .MuiOutlinedInput-root': {
              '& fieldset': { borderColor: 'divider' },
              '&:hover fieldset': { borderColor: 'text.secondary' },
              '&.Mui-focused fieldset': { borderColor: 'primary.main' }
            }
          }}
        />
      </Paper>

      {/* Test Connection */}
      <Paper 
        variant="outlined" 
        sx={{ 
          p: 3, 
          bgcolor: 'background.default',
          border: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 'bold' }}>
          {t('settings.imap.testTitle', 'Test Connection')}
        </Typography>

        <Button
          variant="outlined"
          startIcon={testing ? <CircularProgress size={20} /> : <BugReport />}
          onClick={handleTest}
          disabled={testing}
          sx={{
            borderColor: 'primary.main',
            color: 'primary.main',
            '&:hover': {
              borderColor: 'primary.dark',
              backgroundColor: 'primary.light',
              color: 'primary.dark'
            }
          }}
        >
          {testing ? t('settings.imap.testing', 'Testing...') : t('settings.imap.testButton', 'Test Connection')}
        </Button>

        {testResult && (
          <Alert 
            severity={testResult.success ? 'success' : 'error'} 
            sx={{ mt: 2 }}
          >
            {testResult.message}
            {testResult.details && (
              <Box sx={{ mt: 1, fontSize: '0.875rem' }}>
                <Typography variant="caption" display="block">
                  IMAP: {testResult.details.imap?.message || 'Not tested'}
                </Typography>
                <Typography variant="caption" display="block">
                  SMTP: {testResult.details.smtp?.message || 'Not tested'}
                </Typography>
              </Box>
            )}
          </Alert>
        )}
      </Paper>

      <Alert severity="warning" sx={{ bgcolor: 'background.default' }}>
        {t('settings.imap.warning', 'For Gmail, you may need to use an App Password instead of your regular password. Enable 2-factor authentication and generate an App Password in your Google Account settings.')}
      </Alert>
    </Stack>
  );
}

