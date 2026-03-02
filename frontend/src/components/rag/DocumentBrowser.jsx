import React, { useState, useEffect } from 'react';
import {
  Paper, List, ListItem, ListItemText, IconButton,
  Typography, Box, TextField, Pagination, Alert,
  CircularProgress, Chip, Dialog, DialogTitle, DialogContent,
  DialogActions, Button, Stack, Divider
} from '@mui/material';
import { 
  Delete, Search, Visibility, Description, PictureAsPdf, 
  TextSnippet, CalendarToday, Storage 
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { getRAGDocuments, deleteRAGDocument } from '../../api/client';

const getFileIcon = (fileType) => {
  switch (fileType?.toLowerCase()) {
    case 'pdf': return <PictureAsPdf color="error" />;
    case 'md': return <Description color="primary" />;
    case 'txt': return <TextSnippet color="info" />;
    default: return <Description />;
  }
};

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown';
  try {
    return new Date(dateString).toLocaleString();
  } catch {
    return dateString;
  }
};

export default function DocumentBrowser({ collection, onDocumentDelete }) {
  const { t } = useTranslation();
  const [documents, setDocuments] = useState([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [deleteDialog, setDeleteDialog] = useState(null);
  const [previewDialog, setPreviewDialog] = useState(null);

  const limit = 20;

  const loadDocuments = async () => {
    if (!collection) return;
    
    try {
      setLoading(true);
      setError(null);
      const offset = (page - 1) * limit;
      const data = await getRAGDocuments(collection, limit, offset);
      setDocuments(data.documents || []);
      setTotal(data.total || 0);
    } catch (err) {
      setError(`Failed to load documents: ${err.message}`);
      console.error('Error loading documents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, [collection, page]);

  const handleDelete = async (docId) => {
    try {
      setLoading(true);
      setError(null);
      await deleteRAGDocument(docId, collection);
      setDeleteDialog(null);
      loadDocuments();
      if (onDocumentDelete) {
        onDocumentDelete();
      }
    } catch (err) {
      setError(`Failed to delete document: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const filteredDocs = documents.filter(doc =>
    doc.content.toLowerCase().includes(search.toLowerCase()) ||
    doc.metadata?.source?.toLowerCase().includes(search.toLowerCase())
  );

  const getSourceInfo = (metadata) => {
    const source = metadata?.source || 'Unknown';
    const fileType = source.split('.').pop()?.toLowerCase();
    const uploadedAt = metadata?.uploaded_at;
    const chunkInfo = metadata?.chunk_index !== undefined ? 
      `Chunk ${metadata.chunk_index + 1}/${metadata.total_chunks}` : null;
    
    return { source, fileType, uploadedAt, chunkInfo };
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        📋 Browse Documents in "{collection}"
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Search and Stats */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3, alignItems: 'center' }}>
        <TextField
          fullWidth
          placeholder="Search documents..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          InputProps={{
            startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
          }}
          disabled={loading}
        />
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, minWidth: 120 }}>
          {loading ? (
            <CircularProgress size={20} />
          ) : (
            <>
              <Storage sx={{ fontSize: 16, color: 'text.secondary' }} />
              <Typography variant="body2" color="text.secondary">
                {total} documents
              </Typography>
            </>
          )}
        </Box>
      </Box>

      {/* Documents List */}
      {loading && documents.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : filteredDocs.length === 0 ? (
        <Alert severity="info">
          {search ? 'No documents match your search.' : 'No documents found in this collection.'}
        </Alert>
      ) : (
        <>
          <List>
            {filteredDocs.map((doc, index) => {
              const { source, fileType, uploadedAt, chunkInfo } = getSourceInfo(doc.metadata);
              
              return (
                <ListItem
                  key={doc.id}
                  secondaryAction={
                    <Stack direction="row" spacing={1}>
                      <IconButton 
                        edge="end" 
                        onClick={() => setPreviewDialog(doc)}
                        title="Preview document"
                      >
                        <Visibility />
                      </IconButton>
                      <IconButton 
                        edge="end" 
                        onClick={() => setDeleteDialog(doc)}
                        title="Delete document"
                        color="error"
                      >
                        <Delete />
                      </IconButton>
                    </Stack>
                  }
                  sx={{ 
                    borderBottom: '1px solid',
                    borderColor: 'divider',
                    alignItems: 'flex-start',
                    py: 2
                  }}
                >
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        {getFileIcon(fileType)}
                        <Typography variant="subtitle1" sx={{ fontWeight: 'medium' }}>
                          {source}
                        </Typography>
                        {chunkInfo && (
                          <Chip label={chunkInfo} size="small" variant="outlined" />
                        )}
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            mb: 1,
                            display: '-webkit-box',
                            WebkitLineClamp: 3,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden'
                          }}
                        >
                          {doc.content}
                        </Typography>
                        <Stack direction="row" spacing={2} alignItems="center">
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <CalendarToday sx={{ fontSize: 14, color: 'text.secondary' }} />
                            <Typography variant="caption" color="text.secondary">
                              {formatDate(uploadedAt)}
                            </Typography>
                          </Box>
                          <Typography variant="caption" color="text.secondary">
                            ID: {doc.id}
                          </Typography>
                        </Stack>
                      </Box>
                    }
                    secondaryTypographyProps={{ component: 'div' }}
                  />
                </ListItem>
              );
            })}
          </List>

          {/* Pagination */}
          {total > limit && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
              <Pagination
                count={Math.ceil(total / limit)}
                page={page}
                onChange={(e, p) => setPage(p)}
                color="primary"
                disabled={loading}
              />
            </Box>
          )}
        </>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteDialog} onClose={() => setDeleteDialog(null)}>
        <DialogTitle>Delete Document</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This will permanently delete the document. This action cannot be undone.
          </Alert>
          <Typography>
            Are you sure you want to delete this document?
          </Typography>
          {deleteDialog && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Document ID: {deleteDialog.id}
              </Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                {deleteDialog.content.substring(0, 200)}...
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(null)} disabled={loading}>
            Cancel
          </Button>
          <Button 
            onClick={() => handleDelete(deleteDialog?.id)} 
            color="error"
            variant="contained"
            disabled={loading}
          >
            {loading ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Preview Dialog */}
      <Dialog 
        open={!!previewDialog} 
        onClose={() => setPreviewDialog(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {previewDialog && getFileIcon(getSourceInfo(previewDialog.metadata).fileType)}
            Document Preview
          </Box>
        </DialogTitle>
        <DialogContent>
          {previewDialog && (
            <Box>
              <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                <Chip 
                  label={getSourceInfo(previewDialog.metadata).source} 
                  size="small" 
                />
                {getSourceInfo(previewDialog.metadata).chunkInfo && (
                  <Chip 
                    label={getSourceInfo(previewDialog.metadata).chunkInfo} 
                    size="small" 
                    variant="outlined" 
                  />
                )}
              </Stack>
              <Divider sx={{ mb: 2 }} />
              <Typography 
                variant="body2" 
                sx={{ 
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'monospace',
                  bgcolor: 'grey.50',
                  p: 2,
                  borderRadius: 1,
                  maxHeight: 400,
                  overflow: 'auto'
                }}
              >
                {previewDialog.content}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewDialog(null)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
}

