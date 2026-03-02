import React, { useState } from 'react';
import { 
  Stack, TextField, Typography, InputAdornment, IconButton, 
  Alert, Divider, Box 
} from '@mui/material';
import { Visibility, VisibilityOff, Key } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

export default function ApiKeysSettings({ config, onChange }) {
  const { t } = useTranslation();
  const [showKeys, setShowKeys] = useState({
    google: false,
    openai: false,
    anthropic: false,
  });

  const toggleVisibility = (key) => {
    setShowKeys(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    onChange(name, value);
  };

  return (
    <Stack spacing={3}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Key color="primary" />
        <Typography variant="h6" sx={{ color: 'text.primary', fontWeight: 'bold' }}>
          {t('settings.apiKeys.title', 'API Keys')}
        </Typography>
      </Box>

      <Alert severity="info" sx={{ bgcolor: 'background.default' }}>
        {t('settings.apiKeys.info', 'API Keys are stored securely and used for LLM provider authentication.')}
      </Alert>

      <TextField
        fullWidth
        label={t('settings.apiKeys.google', 'Google API Key (Gemini)')}
        name="GOOGLE_API_KEY"
        type={showKeys.google ? 'text' : 'password'}
        value={config.GOOGLE_API_KEY || ''}
        onChange={handleChange}
        placeholder="AIza..."
        helperText={t('settings.apiKeys.googleHelp', 'Required for Gemini LLM provider')}
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <IconButton 
                onClick={() => toggleVisibility('google')}
                edge="end"
                size="small"
              >
                {showKeys.google ? <VisibilityOff /> : <Visibility />}
              </IconButton>
            </InputAdornment>
          ),
        }}
        sx={{
          '& .MuiOutlinedInput-root': {
            '& fieldset': { borderColor: 'divider' },
            '&:hover fieldset': { borderColor: 'text.secondary' },
            '&.Mui-focused fieldset': { borderColor: 'primary.main' }
          }
        }}
      />

      <TextField
        fullWidth
        label={t('settings.apiKeys.openai', 'OpenAI API Key')}
        name="OPENAI_API_KEY"
        type={showKeys.openai ? 'text' : 'password'}
        value={config.OPENAI_API_KEY || ''}
        onChange={handleChange}
        placeholder="sk-..."
        helperText={t('settings.apiKeys.openaiHelp', 'Required for OpenAI LLM provider')}
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <IconButton 
                onClick={() => toggleVisibility('openai')}
                edge="end"
                size="small"
              >
                {showKeys.openai ? <VisibilityOff /> : <Visibility />}
              </IconButton>
            </InputAdornment>
          ),
        }}
        sx={{
          '& .MuiOutlinedInput-root': {
            '& fieldset': { borderColor: 'divider' },
            '&:hover fieldset': { borderColor: 'text.secondary' },
            '&.Mui-focused fieldset': { borderColor: 'primary.main' }
          }
        }}
      />

      <TextField
        fullWidth
        label={t('settings.apiKeys.anthropic', 'Anthropic API Key')}
        name="ANTHROPIC_API_KEY"
        type={showKeys.anthropic ? 'text' : 'password'}
        value={config.ANTHROPIC_API_KEY || ''}
        onChange={handleChange}
        placeholder="sk-ant-..."
        helperText={t('settings.apiKeys.anthropicHelp', 'Required for Anthropic LLM provider')}
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <IconButton 
                onClick={() => toggleVisibility('anthropic')}
                edge="end"
                size="small"
              >
                {showKeys.anthropic ? <VisibilityOff /> : <Visibility />}
              </IconButton>
            </InputAdornment>
          ),
        }}
        sx={{
          '& .MuiOutlinedInput-root': {
            '& fieldset': { borderColor: 'divider' },
            '&:hover fieldset': { borderColor: 'text.secondary' },
            '&.Mui-focused fieldset': { borderColor: 'primary.main' }
          }
        }}
      />

      <Divider sx={{ borderColor: 'divider' }} />

      <Alert severity="warning" sx={{ bgcolor: 'background.default' }}>
        {t('settings.apiKeys.warning', 'Keep your API keys secure. Never share them publicly or commit them to version control.')}
      </Alert>
    </Stack>
  );
}

