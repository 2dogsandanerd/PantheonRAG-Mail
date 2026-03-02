import React, { useState, useEffect } from 'react';
import {
  Box, Typography, List, ListItem, ListItemAvatar, ListItemText,
  Avatar, Chip, Divider, Paper, Button, Switch, FormControlLabel,
  TextField, Slider, Dialog, DialogTitle, DialogContent,
  DialogContentText, DialogActions, Accordion, AccordionSummary,
  AccordionDetails, Alert, AlertTitle, Collapse
} from '@mui/material';
import {
  Email as EmailIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  FilterAlt as FilterAltIcon
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { getInbox, getInboxFromFolder, clearInbox } from '../api/client';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorDisplay } from './ErrorDisplay';

function Inbox({ onEmailSelect, draftMode = 'folder', draftFolderName = 'AI_DRAFT' }) {
  const { t } = useTranslation();

  // Basic State
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Control Panel State
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [maxEmails, setMaxEmails] = useState(10);
  const [refreshInterval, setRefreshInterval] = useState(30); // seconds

  // Status & Logs State
  const [status, setStatus] = useState({ type: 'info', message: 'Bereit' });
  const [logs, setLogs] = useState([]);

  // Dialog State
  const [clearDialogOpen, setClearDialogOpen] = useState(false);

  // LLM-Filter State
  const [filteredEmails, setFilteredEmails] = useState([]);
  const [showFilteredDetails, setShowFilteredDetails] = useState(false);

  // Helper function to add log entry
  const addLog = (message) => {
    const timestamp = new Date().toISOString();
    setLogs(prev => [...prev, { timestamp, message }].slice(-20)); // Keep last 20 logs
  };

  // Fetch emails with mode switch
  const fetchEmails = async () => {
    try {
      setLoading(true);
      setError(null);
      setFilteredEmails([]); // Reset filtered emails

      let data;
      if (draftMode === 'folder') {
        // 🛡️ Sicherheitsmodus: Nur aus AI_DRAFT Ordner
        addLog(`📁 Lade aus Ordner: ${draftFolderName}`);
        setStatus({ type: 'info', message: `Lade aus "${draftFolderName}"...` });

        data = await getInboxFromFolder(draftFolderName, maxEmails);

        addLog(`✅ ${data.count || 0} E-Mails aus ${draftFolderName} geladen`);
      } else {
        // 🤖 Automatik-Modus: Aus Posteingang (LLM filtert)
        addLog(`🤖 Automatik-Modus: LLM filtert Emails aus Posteingang`);
        setStatus({ type: 'info', message: 'LLM analysiert Emails...' });

        data = await getInboxWithFilter(maxEmails, "auto");

        // Backend gibt zurück: { emails: [...], filtered_emails: [...], count: 5 }
        if (data.filtered_emails && data.filtered_emails.length > 0) {
          setFilteredEmails(data.filtered_emails);
          addLog(`🔍 ${data.filtered_emails.length} E-Mails gefiltert`);
        }

        addLog(`✅ ${data.count || 0} relevante E-Mails geladen`);
      }

      setEmails(data.emails || []);
      setStatus({
        type: 'success',
        message: `${data.count || 0} E-Mails geladen${draftMode === 'auto' && data.filtered_count > 0 ? ` (${data.filtered_count} gefiltert)` : ''}`
      });
    } catch (err) {
      setError(err.message);
      setEmails([]);
      setStatus({ type: 'error', message: 'Fehler beim Laden' });
      addLog(`❌ Fehler: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Handle manual refresh
  const handleRefresh = async () => {
    await fetchEmails();
  };

  // Handle clear inbox
  const handleClearInbox = async () => {
    setClearDialogOpen(false);

    try {
      setLoading(true);
      setStatus({ type: 'info', message: 'Leere Inbox...' });
      addLog('Markiere alle E-Mails als gelesen...');

      const result = await clearInbox();

      setStatus({ type: 'success', message: result.message || 'Inbox geleert' });
      addLog(`✅ ${result.count || 0} E-Mails als gelesen markiert`);

      // Reload inbox after clearing
      await fetchEmails();
    } catch (err) {
      setError(err.message);
      setStatus({ type: 'error', message: 'Fehler beim Leeren' });
      addLog(`❌ Fehler: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchEmails();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [draftMode, draftFolderName, maxEmails]);

  // Auto-Refresh Effect
  useEffect(() => {
    if (!autoRefresh) return;

    addLog(`⏰ Auto-Refresh aktiviert (Intervall: ${refreshInterval}s)`);

    const interval = setInterval(() => {
      handleRefresh();
    }, refreshInterval * 1000);

    return () => {
      clearInterval(interval);
      addLog('⏰ Auto-Refresh deaktiviert');
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoRefresh, refreshInterval]);

  if (loading && emails.length === 0) {
    return <LoadingSpinner message={t('inbox.loading')} />;
  }

  return (
    <Box sx={{ mb: 4 }}>
      {/* Title with Unread Badge */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        {t('inbox.title')}
        {emails.length > 0 && (
          <Chip
            label={`${emails.length} ${t('inbox.unreadEmails')}`}
            color="primary"
            size="small"
            sx={{ ml: 2 }}
          />
        )}
      </Typography>

      {/* Control Panel */}
      <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <Typography variant="h6">
            Einstellungen
          </Typography>
          <Chip
            label={draftMode === 'folder' ? '🛡️ Sicherheitsmodus' : '🤖 Automatik-Modus'}
            size="small"
            color={draftMode === 'folder' ? 'default' : 'primary'}
          />
          {draftMode === 'folder' && (
            <Chip
              label={`Ordner: ${draftFolderName}`}
              size="small"
              variant="outlined"
            />
          )}
        </Box>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* Row 1: Buttons */}
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              startIcon={<RefreshIcon />}
              onClick={handleRefresh}
              disabled={loading}
            >
              E-Mails laden
            </Button>

            <Button
              variant="outlined"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={() => setClearDialogOpen(true)}
            >
              Inbox leeren
            </Button>
          </Box>

          {/* Row 2: Switches & Inputs */}
          <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap', alignItems: 'center' }}>
            <FormControlLabel
              control={
                <Switch
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                />
              }
              label="Auto-Refresh"
            />

            <TextField
              type="number"
              label="Max E-Mails"
              value={maxEmails}
              onChange={(e) => setMaxEmails(Math.max(5, Math.min(100, parseInt(e.target.value) || 10)))}
              inputProps={{ min: 5, max: 100, step: 5 }}
              sx={{ width: 140 }}
              size="small"
            />
          </Box>

          {/* Row 3: Refresh Interval Slider */}
          {autoRefresh && (
            <Box sx={{ px: 2 }}>
              <Typography variant="caption" gutterBottom>
                Refresh-Intervall: {refreshInterval} Sekunden
              </Typography>
              <Slider
                value={refreshInterval}
                onChange={(e, val) => setRefreshInterval(val)}
                min={10}
                max={300}
                step={10}
                marks={[
                  { value: 10, label: '10s' },
                  { value: 60, label: '1m' },
                  { value: 180, label: '3m' },
                  { value: 300, label: '5m' }
                ]}
                valueLabelDisplay="auto"
              />
            </Box>
          )}
        </Box>
      </Paper>

      {/* Clear Inbox Confirmation Dialog */}
      <Dialog open={clearDialogOpen} onClose={() => setClearDialogOpen(false)}>
        <DialogTitle>Inbox leeren?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Möchten Sie wirklich alle ungelesenen E-Mails als gelesen markieren?
            Diese Aktion kann nicht rückgängig gemacht werden.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setClearDialogOpen(false)}>
            Abbrechen
          </Button>
          <Button onClick={handleClearInbox} color="error" variant="contained">
            Inbox leeren
          </Button>
        </DialogActions>
      </Dialog>

      {/* Filtered Emails Alert (nur im Automatik-Modus) */}
      {draftMode === 'auto' && filteredEmails.length > 0 && (
        <Alert
          severity="info"
          sx={{ mb: 2 }}
          icon={<FilterAltIcon />}
        >
          <AlertTitle>
            {filteredEmails.length} Email(s) gefiltert
          </AlertTitle>

          <Typography variant="body2" sx={{ mb: 1 }}>
            Diese E-Mails wurden automatisch gefiltert und benötigen keine Antwort:
          </Typography>

          <Collapse in={showFilteredDetails}>
            <List dense>
              {filteredEmails.map(email => (
                <ListItem key={email.id} sx={{ pl: 0 }}>
                  <Chip
                    label={email.reason_category || 'GEFILTERT'}
                    size="small"
                    color={
                      email.reason_category === 'NEWSLETTER' ? 'default' :
                      email.reason_category === 'NOTIFICATION' ? 'info' :
                      email.reason_category === 'INSUFFICIENT_CONTEXT' ? 'warning' :
                      'secondary'
                    }
                    sx={{ mr: 1, minWidth: 140 }}
                  />
                  <Typography variant="body2" noWrap sx={{ flex: 1 }}>
                    <strong>{email.sender || 'Unbekannt'}:</strong> {email.subject}
                  </Typography>
                </ListItem>
              ))}
            </List>
          </Collapse>

          <Button
            size="small"
            onClick={() => setShowFilteredDetails(!showFilteredDetails)}
            endIcon={<ExpandMoreIcon sx={{ transform: showFilteredDetails ? 'rotate(180deg)' : 'rotate(0deg)', transition: '0.3s' }} />}
          >
            {showFilteredDetails ? 'Ausblenden' : 'Details anzeigen'}
          </Button>
        </Alert>
      )}

      {/* Status & Logs Accordion */}
      <Accordion sx={{ mb: 3 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
            <Typography variant="h6">
              Status & Logs
            </Typography>
            <Chip
              label={status.message}
              color={status.type === 'error' ? 'error' : status.type === 'success' ? 'success' : 'default'}
              size="small"
            />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Paper
            sx={{
              p: 2,
              maxHeight: 200,
              overflowY: 'auto',
              bgcolor: 'background.default'
            }}
          >
            {logs.length === 0 ? (
              <Typography variant="caption" color="text.secondary">
                Keine Logs vorhanden
              </Typography>
            ) : (
              logs.map((log, i) => (
                <Typography
                  key={i}
                  variant="caption"
                  sx={{ display: 'block', fontFamily: 'monospace' }}
                >
                  [{new Date(log.timestamp).toLocaleTimeString()}] {log.message}
                </Typography>
              ))
            )}
          </Paper>
        </AccordionDetails>
      </Accordion>

      {/* Error Display */}
      {error && (
        <ErrorDisplay
          error={error}
          title={t('common.error')}
          onRetry={handleRefresh}
        />
      )}

      {/* Email List */}
      {emails.length === 0 ? (
        <Paper
          sx={{
            p: 4,
            textAlign: 'center',
            bgcolor: 'background.default',
          }}
        >
          <EmailIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            Keine ungelesenen E-Mails
          </Typography>
          <Typography variant="body2" color="text.disabled">
            {draftMode === 'folder'
              ? `Der Ordner "${draftFolderName}" ist leer.`
              : 'Ihr Posteingang ist leer. Alles erledigt!'}
          </Typography>
        </Paper>
      ) : (
        <Paper elevation={2}>
          <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
            {emails.map((email, index) => (
              <React.Fragment key={email.id}>
                <ListItem
                  alignItems="flex-start"
                  onClick={() => onEmailSelect(email)}
                  sx={{
                    cursor: 'pointer',
                    transition: 'background-color 0.2s',
                    '&:hover': {
                      bgcolor: 'action.hover',
                    },
                    py: 2,
                  }}
                >
                  <ListItemAvatar>
                    <Avatar
                      sx={{
                        bgcolor: 'primary.main',
                        width: 48,
                        height: 48,
                      }}
                    >
                      {email.sender ? email.sender[0].toUpperCase() : 'E'}
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography
                          component="span"
                          variant="body1"
                          color="text.primary"
                          sx={{ fontWeight: 'medium' }}
                        >
                          {email.sender}
                        </Typography>
                        {email.date && (
                          <Typography
                            component="span"
                            variant="caption"
                            color="text.secondary"
                          >
                            {new Date(email.date).toLocaleDateString()}
                          </Typography>
                        )}
                      </Box>
                    }
                    secondary={
                      <>
                        <Typography
                          component="div"
                          variant="body2"
                          color="text.primary"
                          sx={{ fontWeight: 'medium', mb: 0.5 }}
                        >
                          {email.subject}
                        </Typography>
                        <Typography
                          component="div"
                          variant="body2"
                          color="text.secondary"
                          sx={{
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                          }}
                        >
                          {email.snippet}
                        </Typography>
                      </>
                    }
                  />
                </ListItem>
                {index < emails.length - 1 && <Divider variant="inset" component="li" />}
              </React.Fragment>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  );
}

export default Inbox;
