import React, { useState, useEffect } from 'react';
import {
  Stack, Typography, Button, Alert, TextField, IconButton,
  List, ListItem, ListItemText, ListItemSecondaryAction, Box,
  Paper, Divider
} from '@mui/material';
import {
  Security, Add, Delete, Save, Warning
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { getBackendURL } from '../../api/client';

/**
 * SecuritySettings Component
 *
 * Manages allowed root directories for path validation.
 * Critical security feature that restricts which directories can be accessed
 * by LLM-powered generators and file operations.
 */
export default function SecuritySettings() {
  const { t } = useTranslation();
  const [allowedRoots, setAllowedRoots] = useState([]);
  const [newPath, setNewPath] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // Load allowed roots on component mount
  useEffect(() => {
    loadAllowedRoots();
  }, []);

  const loadAllowedRoots = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${getBackendURL()}/api/v1/config/settings/security/allowed-roots`);
      if (!response.ok) {
        throw new Error('Failed to load security settings');
      }
      const data = await response.json();
      setAllowedRoots(data.allowed_roots || []);
      setError('');
    } catch (err) {
      setError(`Failed to load settings: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAddPath = () => {
    if (!newPath.trim()) {
      setError('Please enter a valid path');
      return;
    }

    // Check for duplicates
    if (allowedRoots.includes(newPath.trim())) {
      setError('This path is already in the list');
      return;
    }

    setAllowedRoots([...allowedRoots, newPath.trim()]);
    setNewPath('');
    setError('');
    setMessage('Path added. Click Save to apply changes.');
  };

  const handleRemovePath = (pathToRemove) => {
    if (allowedRoots.length <= 1) {
      setError('At least one allowed root directory must be configured');
      return;
    }

    setAllowedRoots(allowedRoots.filter(path => path !== pathToRemove));
    setMessage('Path removed. Click Save to apply changes.');
    setError('');
  };

  const handleSave = async () => {
    if (allowedRoots.length === 0) {
      setError('At least one allowed root directory must be specified');
      return;
    }

    try {
      setSaving(true);
      const response = await fetch(`${getBackendURL()}/api/v1/config/settings/security/allowed-roots`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ allowed_roots: allowedRoots }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save security settings');
      }

      const data = await response.json();
      setMessage('Security settings saved successfully');
      setError('');

      // Reload to ensure sync with backend
      await loadAllowedRoots();
    } catch (err) {
      setError(`Failed to save: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography>Loading security settings...</Typography>
      </Box>
    );
  }

  return (
    <Stack spacing={3}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Security color="error" />
        <Typography variant="h6" sx={{ color: 'text.primary', fontWeight: 'bold' }}>
          {t('settings.security.title', 'Path Access Control')}
        </Typography>
      </Box>

      <Alert severity="error" sx={{ bgcolor: 'background.default' }}>
        <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
          🔒 {t('settings.security.critical', 'CRITICAL SECURITY SETTING')}
        </Typography>
        <Typography variant="body2">
          {t('settings.security.description',
            'These directories control which paths can be accessed by LLM-powered features and file operations. ' +
            'Restricting access prevents unauthorized file system access. This setting is important in both ' +
            'development and production environments.'
          )}
        </Typography>
      </Alert>

      {message && (
        <Alert severity="success" onClose={() => setMessage('')}>
          {message}
        </Alert>
      )}

      {error && (
        <Alert severity="error" onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Paper variant="outlined" sx={{ p: 2 }}>
        <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold', mb: 2 }}>
          {t('settings.security.allowedRoots', 'Allowed Root Directories')}
        </Typography>

        <List>
          {allowedRoots.map((path, index) => (
            <ListItem
              key={index}
              sx={{
                border: 1,
                borderColor: 'divider',
                borderRadius: 1,
                mb: 1,
                bgcolor: 'background.default'
              }}
            >
              <ListItemText
                primary={path}
                primaryTypographyProps={{
                  fontFamily: 'monospace',
                  fontSize: '0.875rem'
                }}
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  aria-label="delete"
                  onClick={() => handleRemovePath(path)}
                  color="error"
                  size="small"
                  disabled={allowedRoots.length <= 1}
                >
                  <Delete />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>

        <Divider sx={{ my: 2 }} />

        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            size="small"
            label={t('settings.security.addPath', 'Add New Path')}
            value={newPath}
            onChange={(e) => setNewPath(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleAddPath();
              }
            }}
            placeholder="/path/to/directory"
            helperText={t('settings.security.pathHelp', 'Enter absolute path to a directory (e.g., /home/user/projects)')}
            InputProps={{
              style: { fontFamily: 'monospace' }
            }}
            sx={{
              '& .MuiOutlinedInput-root': {
                '& fieldset': { borderColor: 'divider' },
                '&:hover fieldset': { borderColor: 'text.secondary' },
                '&.Mui-focused fieldset': { borderColor: 'primary.main' }
              }
            }}
          />
          <Button
            variant="outlined"
            startIcon={<Add />}
            onClick={handleAddPath}
            sx={{ minWidth: '120px' }}
          >
            {t('settings.security.add', 'Add')}
          </Button>
        </Box>
      </Paper>

      <Alert severity="warning" sx={{ bgcolor: 'background.default' }}>
        <Typography variant="body2">
          <Warning sx={{ fontSize: 16, verticalAlign: 'middle', mr: 0.5 }} />
          <strong>{t('settings.security.warning', 'Warning:')}</strong>
          {' '}
          {t('settings.security.warningText',
            'Only add paths that should be accessible. Avoid adding system directories like /etc, /usr, or /var ' +
            'unless absolutely necessary.'
          )}
        </Typography>
      </Alert>

      <Divider sx={{ borderColor: 'divider' }} />

      <Button
        variant="contained"
        color="primary"
        startIcon={<Save />}
        onClick={handleSave}
        disabled={saving}
        fullWidth
        sx={{ py: 1.5 }}
      >
        {saving ? t('common.saving', 'Saving...') : t('settings.save', 'Save Security Settings')}
      </Button>

      <Alert severity="info" sx={{ bgcolor: 'background.default' }}>
        <Typography variant="caption">
          💡 <strong>{t('settings.security.tip', 'Tip:')}</strong>
          {' '}
          {t('settings.security.tipText',
            'These settings will be checked during onboarding and can be modified at any time. ' +
            'Changes take effect immediately after saving.'
          )}
        </Typography>
      </Alert>
    </Stack>
  );
}
