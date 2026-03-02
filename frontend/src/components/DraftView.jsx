import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Card, CardContent, TextField, Button,
  Paper, Stack, Accordion, AccordionSummary, AccordionDetails, CircularProgress,
  Alert, AlertTitle, Chip, Snackbar
} from '@mui/material';
import {
  Send, AutoAwesome, ExpandMore, History, SmartToy,
  InfoOutlined as InfoIcon,
  CheckCircle as CheckCircleIcon,
  HourglassEmpty as HourglassIcon,
  Circle as CircleIcon,
  Newspaper as NewsletterIcon,
  Notifications as NotificationIcon,
  QuestionMark as QuestionIcon,
  Block as BlockIcon
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { getThread, generateDraft, saveDraft } from '../api/client';
import { ErrorDisplay } from './ErrorDisplay';

function DraftView({ selectedEmail, draftMode = 'folder', draftFolderName = 'AI_DRAFT' }) {
  const { t } = useTranslation();
  
  // Status configuration
  const statusConfig = {
    idle: {
      color: 'default',
      icon: <CircleIcon sx={{ fontSize: 16 }} />,
      label: 'Bereit'
    },
    generating: {
      color: 'warning',
      icon: <HourglassIcon sx={{ fontSize: 16 }} />,
      label: 'Generiere Draft...'
    },
    ready: {
      color: 'success',
      icon: <CheckCircleIcon sx={{ fontSize: 16 }} />,
      label: 'Draft Fertig'
    },
    created: {
      color: 'info',
      icon: <Send sx={{ fontSize: 16 }} />,
      label: 'Draft Erstellt'
    }
  };

  const getAlertIcon = () => {
    switch (reasonCategory) {
      case 'NEWSLETTER': return <NewsletterIcon />;
      case 'NOTIFICATION': return <NotificationIcon />;
      case 'INSUFFICIENT_CONTEXT': return <QuestionIcon />;
      case 'OUT_OF_SCOPE': return <BlockIcon />;
      default: return <InfoIcon />;
    }
  };

  const [thread, setThread] = useState([]);
  const [draft, setDraft] = useState('');
  const [ragContext, setRagContext] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // New state for Phase 4
  const [draftStatus, setDraftStatus] = useState('idle');
  const [noAnswerNeeded, setNoAnswerNeeded] = useState(false);
  const [reasonCategory, setReasonCategory] = useState(null);
  const [learningPairId, setLearningPairId] = useState(null);
  const [createLoading, setCreateLoading] = useState(false);

  useEffect(() => {
    if (selectedEmail && selectedEmail.thread_id) {
      const fetchThread = async () => {
        try {
          setLoading(true);
          setDraft('');
          setRagContext('');
          setThread([]);
          const data = await getThread(selectedEmail.thread_id);
          setThread(data.thread || []);
          setError(null);
        } catch (err) {
          setError(err.message);
          setThread([]);
        } finally {
          setLoading(false);
        }
      };
      fetchThread();
    }
  }, [selectedEmail]);

  const handleGenerateDraft = async () => {
    if (!selectedEmail) return;
    try {
        setLoading(true);
        setDraft('');
        setRagContext('');
        setDraftStatus('generating'); // Set status

        const request = {
            sender: selectedEmail.sender,
            subject: selectedEmail.subject,
            body: selectedEmail.body,
            thread_id: selectedEmail.thread_id,
            use_rag: true
        };

        const response = await generateDraft(request);

        // Check for NO_ANSWER_NEEDED (boolean flag)
        if (response.no_answer_needed === true) {
            setNoAnswerNeeded(true);
            setReasonCategory(response.reason_category || null); // Store category
            setDraft('');
            setRagContext(response.rag_context || '');
            setDraftStatus('idle');
            setError(null);
            return;
        }

        // Normal draft generated
        setDraft(response.draft || 'No draft generated.');
        setRagContext(response.rag_context || 'No RAG context was used.');
        setDraftStatus('ready');
        setNoAnswerNeeded(false);
        setError(null);

    } catch (err) {
        setError(err.message);
        setDraft('');
        setDraftStatus('idle');
    } finally {
        setLoading(false);
    }
  };

  const handleCreateDraft = async () => {
    if (!draft || !selectedEmail) return;

    try {
      setCreateLoading(true);

      const result = await saveDraft({
        to: selectedEmail.sender,
        subject: `Re: ${selectedEmail.subject}`,
        body: draft,
        thread_id: selectedEmail.thread_id,
        in_reply_to: selectedEmail.id,
        // Include source_folder only in folder mode
        source_folder: draftMode === 'folder' ? draftFolderName : null
      });

      setDraftStatus('created');
      setLearningPairId(result.learning_pair_id || null);

      // Show success message
      setError(null);

    } catch (err) {
      setError(err.message);
    } finally {
      setCreateLoading(false);
    }
  };

  if (!selectedEmail) {
    return (
      <Paper
        sx={{
          p: 6,
          textAlign: 'center',
          bgcolor: 'background.default',
        }}
      >
        <Send sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
        <Typography variant="h6" color="text.secondary">
          {t('draft.noEmailSelected')}
        </Typography>
        <Typography variant="body2" color="text.disabled">
          {t('draft.selectEmail')}
        </Typography>
      </Paper>
    );
  }

  return (
    <Box sx={{ mb: 4 }}>
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        {t('draft.title')}: {selectedEmail.subject}
      </Typography>

      {error && (
        <ErrorDisplay
          error={error}
          title={t('common.error')}
          onRetry={handleGenerateDraft}
        />
      )}

      {/* NO_ANSWER_NEEDED Alert with Kategorien */}
      {noAnswerNeeded && (
        <Alert
          severity="info"
          icon={getAlertIcon()}
          sx={{ mb: 3 }}
          onClose={() => {
            setNoAnswerNeeded(false);
            setReasonCategory(null);
          }}
        >
          <AlertTitle>Keine Antwort erforderlich</AlertTitle>

          {/* Kategorie-spezifische Nachrichten */}
          {reasonCategory === 'NEWSLETTER' && (
            <>
              <Typography variant="body2">
                Newsletter oder Marketing-Email erkannt.
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Diese Art von E-Mail benötigt in der Regel keine persönliche Antwort.
              </Typography>
            </>
          )}

          {reasonCategory === 'NOTIFICATION' && (
            <>
              <Typography variant="body2">
                Automatische Benachrichtigung erkannt.
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                System-Benachrichtigungen oder Bestätigungen benötigen keine Antwort.
              </Typography>
            </>
          )}

          {reasonCategory === 'INSUFFICIENT_CONTEXT' && (
            <>
              <Typography variant="body2">
                Der RAG-Context enthält nicht genügend Informationen für eine hilfreiche Antwort.
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Um präzise zu antworten, fehlen relevante Informationen in der Wissensdatenbank.
              </Typography>
            </>
          )}

          {reasonCategory === 'OUT_OF_SCOPE' && (
            <>
              <Typography variant="body2">
                Die Anfrage liegt außerhalb des Wissensbereichs.
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Diese E-Mail behandelt Themen, die nicht im konfigurierten Fachgebiet liegen.
              </Typography>
            </>
          )}

          {!reasonCategory && (
            <Typography variant="body2">
              Der LLM-Assistent hat entschieden, dass diese E-Mail keine Antwort benötigt.
            </Typography>
          )}

          {/* RAG Context Indicator */}
          {ragContext && (
            <Chip
              label="RAG-Context geprüft"
              size="small"
              variant="outlined"
              sx={{ mt: 2 }}
            />
          )}
        </Alert>
      )}

      {/* Thread History */}
      <Accordion defaultExpanded sx={{ mb: 3 }}>
        <AccordionSummary
          expandIcon={<ExpandMore />}
          aria-controls="thread-history-content"
          id="thread-history-header"
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <History color="primary" />
            <Typography variant="h6">
              Thread History ({thread.length} messages)
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Stack spacing={2} sx={{ maxHeight: 300, overflowY: 'auto' }}>
            {thread.length === 0 ? (
              <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                {t('common.loading')}
              </Typography>
            ) : (
              thread.map((msg, index) => (
                <Card key={index} variant="outlined">
                  <CardContent>
                    <Typography variant="caption" color="text.secondary">
                      <strong>{t('draft.from')}:</strong> {msg.sender}
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        mt: 1,
                        whiteSpace: 'pre-wrap',
                        bgcolor: 'background.default',
                        p: 1,
                        borderRadius: 1,
                      }}
                    >
                      {msg.body}
                    </Typography>
                  </CardContent>
                </Card>
              ))
            )}
          </Stack>
        </AccordionDetails>
      </Accordion>

      {/* Draft Editor */}
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">
            {t('draft.response')}
          </Typography>

          {/* Status Indicator Chip */}
          <Chip
            icon={statusConfig[draftStatus].icon}
            label={statusConfig[draftStatus].label}
            color={statusConfig[draftStatus].color}
            size="small"
          />
        </Box>
        <TextField
          fullWidth
          multiline
          rows={8}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder={t('draft.selectEmail')}
          variant="outlined"
          sx={{ mb: 2 }}
        />
        <Stack direction="row" spacing={2}>
          <Button
            variant="contained"
            startIcon={loading ? <CircularProgress size={20} /> : <AutoAwesome />}
            onClick={handleGenerateDraft}
            disabled={loading}
          >
            {loading ? t('draft.generating') : t('draft.generateDraft')}
          </Button>
          <Button
            variant="outlined"
            startIcon={createLoading ? <CircularProgress size={20} /> : <Send />}
            onClick={handleCreateDraft}
            disabled={!draft || createLoading || draftStatus === 'created'}
          >
            {createLoading ? 'Erstelle...' : draftStatus === 'created' ? 'Draft Erstellt' : t('draft.createDraft')}
          </Button>
        </Stack>
        
        {/* Learning Pair Feedback */}
        {learningPairId && (
          <Alert severity="success" sx={{ mt: 2 }}>
            <AlertTitle>Draft erfolgreich erstellt!</AlertTitle>
            Learning Pair ID: <strong>{learningPairId}</strong>
            <br />
            <Button
              size="small"
              onClick={() => console.log("Navigate to learning dashboard")}
              sx={{ mt: 1 }}
            >
              Zum Learning Dashboard →
            </Button>
          </Alert>
        )}
      </Paper>

      {/* RAG Context */}
      {ragContext && (
        <Accordion sx={{ bgcolor: 'info.light' }}>
          <AccordionSummary
            expandIcon={<ExpandMore />}
            aria-controls="rag-context-content"
            id="rag-context-header"
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <SmartToy />
              <Typography variant="h6">
                RAG Context Used
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography
              variant="body2"
              component="pre"
              sx={{
                whiteSpace: 'pre-wrap',
                fontSize: '0.85rem',
                maxHeight: 200,
                overflowY: 'auto',
                bgcolor: 'background.paper',
                p: 2,
                borderRadius: 1,
                color: 'text.primary',
              }}
            >
              {ragContext}
            </Typography>
          </AccordionDetails>
        </Accordion>
      )}
    </Box>
  );
}

export default DraftView;
