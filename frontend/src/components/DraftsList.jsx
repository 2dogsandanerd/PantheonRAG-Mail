import React, { useState, useEffect } from 'react';
import {
  Box, Typography, List, Accordion, AccordionSummary, AccordionDetails, Paper, Chip,
  IconButton, Select, MenuItem, FormControl, InputLabel, Stack, Button, Dialog,
  DialogTitle, DialogContent, DialogContentText, DialogActions, Snackbar, Alert, CircularProgress
} from '@mui/material';
import { ExpandMore, Delete, Sort, Send } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { getDrafts, deleteDraft, getThread, saveDraft } from '../api/client';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorDisplay } from './ErrorDisplay';

function DraftsList() {
  const { t } = useTranslation();
  const [drafts, setDrafts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, DRAFT_CREATED, PAIR_COMPLETED
  const [sortBy, setSortBy] = useState('date-desc'); // date-asc, date-desc
  const [deleteDialog, setDeleteDialog] = useState({ open: false, draftId: null });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [creatingId, setCreatingId] = useState(null); // To show loading on a specific draft

  const fetchDrafts = async () => {
    try {
      setLoading(true);
      const data = await getDrafts();
      setDrafts(data.drafts || []);
      setError(null);
    } catch (err) {
      setError(err.message);
      setDrafts([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDrafts();
  }, []);

  const handleDelete = async () => {
    try {
      await deleteDraft(deleteDialog.draftId);
      setDeleteDialog({ open: false, draftId: null });
      setSnackbar({ open: true, message: t('drafts.deleteSuccess', 'Draft deleted successfully!'), severity: 'success' });
      fetchDrafts(); // Refresh list after deletion
    } catch (err) {
      setSnackbar({ open: true, message: t('drafts.deleteError', `Delete failed: ${err.message}`), severity: 'error' });
      setDeleteDialog({ open: false, draftId: null });
    }
  };

  const handleCreateInClient = async (draft) => {
    setCreatingId(draft.id);
    try {
      // 1. Fetch thread details to get recipient, subject, etc.
      const threadData = await getThread(draft.thread_id);
      const lastMessage = threadData.thread[threadData.thread.length - 1];

      if (!lastMessage) {
        throw new Error('Could not retrieve original message from thread.');
      }

      // 2. Construct the draft data for the API
      const draftToSave = {
        to: lastMessage.sender, // Replying to the sender of the last message
        subject: lastMessage.subject.startsWith('Re:') ? lastMessage.subject : `Re: ${lastMessage.subject}`,
        body: draft.draft_content,
        thread_id: draft.thread_id,
        in_reply_to: lastMessage.id, // ID of the message we are replying to
      };

      // 3. Call the API to save the draft
      await saveDraft(draftToSave);
      setSnackbar({ open: true, message: t('drafts.createSuccess', 'Draft successfully created in your email client!'), severity: 'success' });
      
      // 4. Refresh the list to update status
      fetchDrafts();

    } catch (err) {
      setSnackbar({ open: true, message: t('drafts.createError', `Failed to create draft: ${err.message}`), severity: 'error' });
    } finally {
      setCreatingId(null);
    }
  };

  const getStatusChip = (status) => {
    switch (status) {
      case 'PAIR_COMPLETED':
        return <Chip label={t('learning.status.pairCompleted')} color="success" size="small" />;
      case 'DRAFT_CREATED':
        return <Chip label={t('learning.status.draftCreated')} color="info" size="small" />;
      default:
        return <Chip label={status} size="small" />;
    }
  };

  // Filter and sort drafts
  const filteredDrafts = drafts
    .filter(draft => filter === 'all' || draft.status === filter)
    .sort((a, b) => {
      const dateA = new Date(a.created_at);
      const dateB = new Date(b.created_at);
      return sortBy === 'date-asc' ? dateA - dateB : dateB - dateA;
    });

  if (loading) {
    return <LoadingSpinner message={t('drafts.loading', 'Loading drafts...')} />;
  }

  if (error && !snackbar.open) { // Prevents showing a big error display if a snackbar error is already shown
    return <ErrorDisplay error={error} title={t('drafts.error', 'Error loading drafts')} onRetry={fetchDrafts} />;
  }

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h5" gutterBottom>
        {t('drafts.title', 'Generated Drafts')} ({drafts.length})
      </Typography>

      {/* Filter and Sort Controls */}
      <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Filter by Status</InputLabel>
          <Select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            label="Filter by Status"
          >
            <MenuItem value="all">All Drafts</MenuItem>
            <MenuItem value="DRAFT_CREATED">Draft Created</MenuItem>
            <MenuItem value="PAIR_COMPLETED">Pair Completed</MenuItem>
          </Select>
        </FormControl>

        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Sort by</InputLabel>
          <Select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            label="Sort by"
            startAdornment={<Sort sx={{ mr: 1 }} />}
          >
            <MenuItem value="date-desc">Newest First</MenuItem>
            <MenuItem value="date-asc">Oldest First</MenuItem>
          </Select>
        </FormControl>
      </Stack>

      {drafts.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center', bgcolor: 'background.default' }}>
          <Typography variant="h6" color="text.secondary">
            {t('drafts.noDrafts', 'No drafts have been generated yet.')}
          </Typography>
        </Paper>
      ) : (
        <>
          <Paper elevation={2}>
            <List sx={{ bgcolor: 'background.paper', padding: 0 }}>
              {filteredDrafts.map((draft) => (
                <Accordion key={draft.id}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                      <Typography sx={{ flexShrink: 0, mr: 2 }}>
                        {`Draft for Thread: ${draft.thread_id.substring(0, 15)}...`}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                        {getStatusChip(draft.status)}
                        <IconButton
                          size="small"
                          color="error"
                          onClick={(e) => {
                            e.stopPropagation(); // Prevent accordion toggle
                            setDeleteDialog({ open: true, draftId: draft.id });
                          }}
                        >
                          <Delete />
                        </IconButton>
                      </Box>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails sx={{ bgcolor: 'action.hover' }}>
                    <Typography variant="caption" color="text.secondary" display="block">
                      Created at: {new Date(draft.created_at).toLocaleString()}
                    </Typography>
                    <Paper variant="outlined" sx={{ p: 2, mt: 1, whiteSpace: 'pre-wrap', maxHeight: 300, overflowY: 'auto' }}>
                      {draft.draft_content}
                    </Paper>
                    {draft.status === 'DRAFT_CREATED' && (
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={creatingId === draft.id ? <CircularProgress size={16} color="inherit" /> : <Send />}
                        onClick={() => handleCreateInClient(draft)}
                        disabled={creatingId === draft.id}
                        sx={{ mt: 2 }}
                      >
                        {t('drafts.createInClient', 'Create in Email Client')}
                      </Button>
                    )}
                  </AccordionDetails>
                </Accordion>
              ))}
            </List>
          </Paper>

          {/* Delete Confirmation Dialog */}
          <Dialog
            open={deleteDialog.open}
            onClose={() => setDeleteDialog({ open: false, draftId: null })}
          >
            <DialogTitle>{t('drafts.deleteTitle', 'Delete Draft?')}</DialogTitle>
            <DialogContent>
              <DialogContentText>
                {t('drafts.deleteConfirm', 'Are you sure you want to delete this draft? This action cannot be undone.')}
              </DialogContentText>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDeleteDialog({ open: false, draftId: null })}>
                {t('common.cancel', 'Cancel')}
              </Button>
              <Button onClick={handleDelete} color="error" variant="contained">
                {t('common.delete', 'Delete')}
              </Button>
            </DialogActions>
          </Dialog>
        </>
      )}

      {/* Feedback Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default DraftsList;
