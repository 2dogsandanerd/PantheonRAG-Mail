import React, { useState, useEffect } from 'react';
import {
  Paper, Box, FormControl, InputLabel, Select, MenuItem,
  Button, TextField, Dialog, DialogTitle, DialogContent, DialogActions,
  Stack, Typography, Chip, Alert, IconButton, Tooltip
} from '@mui/material';
import { Add, Delete, Refresh, Storage, Warning } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import {
  getRAGCollections,
  createRAGCollection,
  deleteRAGCollection,
  getRAGCollectionStats,
  resetRAGCollection,
  getCollectionEmbeddingInfo
} from '../../api/client';

export default function CollectionManager({ 
  currentCollection, 
  onCollectionChange, 
  onCollectionUpdate,
  collections = []
}) {
  const { t } = useTranslation();
  const [stats, setStats] = useState(null);
  const [embeddingInfo, setEmbeddingInfo] = useState(null);
  const [createDialog, setCreateDialog] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [resetDialog, setResetDialog] = useState(false);
  const [newCollectionName, setNewCollectionName] = useState('');
  const [newCollectionDescription, setNewCollectionDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const loadStats = async () => {
    if (!currentCollection) return;

    try {
      setLoading(true);
      setError(null);

      // Load stats and embedding info in parallel
      const [statsData, embeddingData] = await Promise.all([
        getRAGCollectionStats(currentCollection),
        getCollectionEmbeddingInfo(currentCollection).catch(err => {
          console.warn('No embedding info available:', err);
          return null;
        })
      ]);

      setStats(statsData);
      setEmbeddingInfo(embeddingData);
    } catch (err) {
      setError(`Failed to load stats: ${err.message}`);
      console.error('Error loading collection stats:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, [currentCollection]);

  const handleCreate = async () => {
    if (!newCollectionName.trim()) return;
    
    try {
      setLoading(true);
      setError(null);
      await createRAGCollection(newCollectionName.trim(), newCollectionDescription.trim());
      setSuccess(`Collection '${newCollectionName}' created successfully`);
      setCreateDialog(false);
      setNewCollectionName('');
      setNewCollectionDescription('');
      onCollectionUpdate();
    } catch (err) {
      setError(`Failed to create collection: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!currentCollection) return;
    
    try {
      setLoading(true);
      setError(null);
      await deleteRAGCollection(currentCollection);
      setSuccess(`Collection '${currentCollection}' deleted successfully`);
      setDeleteDialog(false);
      onCollectionUpdate();
      // Switch to first available collection
      if (collections.length > 1) {
        const remainingCollections = collections.filter(c => c.name !== currentCollection);
        if (remainingCollections.length > 0) {
          onCollectionChange(remainingCollections[0].name);
        }
      }
    } catch (err) {
      setError(`Failed to delete collection: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    if (!currentCollection) return;
    
    try {
      setLoading(true);
      setError(null);
      const result = await resetRAGCollection(currentCollection);
      setSuccess(`Collection '${currentCollection}' reset successfully (${result.deleted_count} documents removed)`);
      setResetDialog(false);
      loadStats();
    } catch (err) {
      setError(`Failed to reset collection: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadStats();
    onCollectionUpdate();
  };

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Stack spacing={3}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Storage sx={{ fontSize: 24, color: 'primary.main' }} />
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            Collection Management
          </Typography>
        </Box>

        {/* Error/Success Messages */}
        {error && (
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        {success && (
          <Alert severity="success" onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        )}

        {/* Collection Selection and Actions */}
        <Stack direction="row" spacing={2} alignItems="center" sx={{ flexWrap: 'wrap', gap: 2 }}>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Collection</InputLabel>
            <Select
              value={collections.some(col => col.name === currentCollection) ? currentCollection : ''}
              onChange={(e) => onCollectionChange(e.target.value)}
              label="Collection"
              disabled={loading}
            >
              {collections.map(col => (
                <MenuItem key={col.name} value={col.name}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Storage sx={{ fontSize: 16 }} />
                    {col.name}
                    <Chip 
                      label={col.count || 0} 
                      size="small" 
                      color="primary" 
                      variant="outlined"
                    />
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Button 
            startIcon={<Add />} 
            onClick={() => setCreateDialog(true)}
            disabled={loading}
            variant="outlined"
          >
            New Collection
          </Button>

          <Button 
            startIcon={<Delete />} 
            color="error" 
            onClick={() => setDeleteDialog(true)}
            disabled={loading || !currentCollection}
            variant="outlined"
          >
            Delete
          </Button>

          <Button 
            startIcon={<Refresh />} 
            onClick={handleRefresh}
            disabled={loading}
            variant="outlined"
          >
            Refresh
          </Button>

          <Box sx={{ flexGrow: 1 }} />

          {/* Collection Stats */}
          {stats && (
            <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 1 }}>
              <Chip 
                label={`${stats.total_documents} docs`} 
                color="primary" 
                icon={<Storage />}
              />
              <Chip 
                label={`${stats.size_mb} MB`} 
                color="info" 
                variant="outlined"
              />
              <Chip 
                label={stats.embedding_model} 
                variant="outlined"
                size="small"
              />
            </Stack>
          )}
        </Stack>

        {/* Embedding Details & Compatibility */}
        {embeddingInfo && (
          <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1, border: '1px solid', borderColor: 'divider' }}>
            <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold', mb: 1.5 }}>
              🧬 Embedding Configuration
            </Typography>

            <Stack spacing={1.5}>
              {/* Collection Embedding */}
              <Box>
                <Typography variant="caption" color="text.secondary" display="block">
                  Collection Embedding:
                </Typography>
                <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
                  <Chip
                    label={embeddingInfo.collection_embedding.model}
                    size="small"
                    color="primary"
                  />
                  <Chip
                    label={`${embeddingInfo.collection_embedding.dimensions} dims`}
                    size="small"
                    variant="outlined"
                  />
                </Stack>
              </Box>

              {/* Current Settings */}
              <Box>
                <Typography variant="caption" color="text.secondary" display="block">
                  Current Settings:
                </Typography>
                <Stack direction="row" spacing={1} sx={{ alignItems: 'center', flexWrap: 'wrap', gap: 1 }}>
                  <Chip
                    label={embeddingInfo.current_settings.model}
                    size="small"
                    color="info"
                  />
                  <Chip
                    label={`${embeddingInfo.current_settings.dimensions} dims`}
                    size="small"
                    variant="outlined"
                  />
                </Stack>
              </Box>

              {/* Compatibility Status */}
              <Alert
                severity={embeddingInfo.compatible ? "success" : "warning"}
                sx={{ mt: 1 }}
              >
                {embeddingInfo.compatible ? (
                  <Typography variant="body2">
                    ✅ <strong>Compatible</strong> - Uploads will work correctly
                  </Typography>
                ) : (
                  <Typography variant="body2">
                    ⚠️ <strong>Not Compatible</strong> - Embedding models don't match!<br/>
                    Please change EMBEDDING_MODEL in Settings to <strong>{embeddingInfo.collection_embedding.model}</strong> before uploading.
                  </Typography>
                )}
              </Alert>
            </Stack>
          </Box>
        )}

        {/* Reset Collection Button */}
        {stats && stats.total_documents > 0 && (
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              startIcon={<Warning />}
              color="warning"
              onClick={() => setResetDialog(true)}
              disabled={loading}
              variant="outlined"
            >
              Reset Collection (Remove All Documents)
            </Button>
          </Box>
        )}
      </Stack>

      {/* Create Collection Dialog */}
      <Dialog open={createDialog} onClose={() => setCreateDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Collection</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              autoFocus
              label="Collection Name"
              fullWidth
              value={newCollectionName}
              onChange={(e) => setNewCollectionName(e.target.value)}
              placeholder="e.g., my_knowledge_base"
              helperText="Use lowercase letters, numbers, and underscores only"
            />
            <TextField
              label="Description (Optional)"
              fullWidth
              multiline
              rows={2}
              value={newCollectionDescription}
              onChange={(e) => setNewCollectionDescription(e.target.value)}
              placeholder="Brief description of this collection's purpose"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialog(false)} disabled={loading}>
            Cancel
          </Button>
          <Button 
            onClick={handleCreate} 
            variant="contained"
            disabled={loading || !newCollectionName.trim()}
          >
            {loading ? 'Creating...' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Collection Dialog */}
      <Dialog open={deleteDialog} onClose={() => setDeleteDialog(false)}>
        <DialogTitle>Delete Collection</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This will permanently delete the collection "{currentCollection}" and all its documents.
            This action cannot be undone.
          </Alert>
          <Typography>
            Are you sure you want to delete this collection?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(false)} disabled={loading}>
            Cancel
          </Button>
          <Button 
            onClick={handleDelete} 
            color="error"
            variant="contained"
            disabled={loading}
          >
            {loading ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Reset Collection Dialog */}
      <Dialog open={resetDialog} onClose={() => setResetDialog(false)}>
        <DialogTitle>Reset Collection</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This will remove all documents from "{currentCollection}" but keep the collection structure.
            This action cannot be undone.
          </Alert>
          <Typography>
            Are you sure you want to reset this collection?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResetDialog(false)} disabled={loading}>
            Cancel
          </Button>
          <Button 
            onClick={handleReset} 
            color="warning"
            variant="contained"
            disabled={loading}
          >
            {loading ? 'Resetting...' : 'Reset'}
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
}

