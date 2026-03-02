import React, { useState, useEffect, useRef } from 'react';
import {
  Paper, Box, Button, Typography, LinearProgress,
  Alert, Stack, Chip, List, ListItem, ListItemText, ListItemIcon,
  IconButton, FormControl, InputLabel, Select, MenuItem, Divider,
  CircularProgress, Collapse, Card, CardContent
} from '@mui/material';
import {
  CloudUpload, Delete, Description, PictureAsPdf,
  TextSnippet, CheckCircle, Error as ErrorIcon, Pending,
  Article, TableChart, Code, Image, ContentCopy
} from '@mui/icons-material';

const getFileIcon = (filename) => {
  const ext = filename.split('.').pop().toLowerCase();
  const iconMap = {
    'pdf': <PictureAsPdf color="error" />,
    'docx': <Description color="primary" />,
    'pptx': <Article color="warning" />,
    'xlsx': <TableChart color="success" />,
    'html': <Code color="info" />,
    'md': <Description color="primary" />,
    'csv': <TableChart color="info" />,
    'txt': <TextSnippet color="action" />
  };
  return iconMap[ext] || <Description />;
};

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const SUPPORTED_EXTENSIONS = ['.pdf', '.docx', '.pptx', '.xlsx', '.html', '.md', '.csv'];
const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100 MB

export default function DoclingIngestion({ collections, onIngestionSuccess }) {
  // File Selection
  const [files, setFiles] = useState([]);
  const [collection, setCollection] = useState('');

  // Task State
  const [taskId, setTaskId] = useState(null);
  const [taskStatus, setTaskStatus] = useState(null);
  const [polling, setPolling] = useState(false);

  // UI State
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);

  const pollingInterval = useRef(null);

  // Set default collection when collections are loaded
  useEffect(() => {
    if (collections && collections.length > 0 && !collection) {
      setCollection(collections[0].name);
    }
  }, [collections, collection]);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingInterval.current) {
        clearInterval(pollingInterval.current);
      }
    };
  }, []);

  const handleFileSelect = (event) => {
    const selectedFiles = Array.from(event.target.files);

    // Validate files
    const validatedFiles = selectedFiles.map(file => {
      const ext = '.' + file.name.split('.').pop().toLowerCase();
      const isSupported = SUPPORTED_EXTENSIONS.includes(ext);
      const isSizeOk = file.size <= MAX_FILE_SIZE;

      return {
        file,
        name: file.name,
        size: file.size,
        valid: isSupported && isSizeOk,
        error: !isSupported ? `Unsupported type: ${ext}` :
               !isSizeOk ? `Too large (max ${formatFileSize(MAX_FILE_SIZE)})` : null
      };
    });

    setFiles(validatedFiles);
    setError(null);
    setTaskStatus(null);
  };

  const handleRemoveFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleStartIngestion = async () => {
    const validFiles = files.filter(f => f.valid);

    if (validFiles.length === 0) {
      setError('No valid files selected');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      validFiles.forEach(f => formData.append('files', f.file));
      formData.append('collection_name', collection);
      formData.append('chunk_size', 500);
      formData.append('chunk_overlap', 50);

      const response = await fetch('http://localhost:33800/api/v1/rag/ingest-documents', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const data = await response.json();
      setTaskId(data.task_id);
      startPolling(data.task_id);

    } catch (err) {
      setError(err.message);
      setUploading(false);
    }
  };

  const startPolling = (id) => {
    setPolling(true);

    // Poll every 1 second
    pollingInterval.current = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:33800/api/v1/rag/ingest-status/${id}`);

        if (!response.ok) {
          throw new Error('Failed to fetch status');
        }

        const status = await response.json();
        setTaskStatus(status);

        // Stop polling when task is complete
        if (['success', 'failed', 'partial'].includes(status.status)) {
          clearInterval(pollingInterval.current);
          setPolling(false);
          setUploading(false);

          if (status.status === 'success' && onIngestionSuccess) {
            onIngestionSuccess();
          }
        }

      } catch (err) {
        console.error('Polling error:', err);
        setError(err.message);
        clearInterval(pollingInterval.current);
        setPolling(false);
        setUploading(false);
      }
    }, 1000);
  };

  const handleReset = () => {
    setFiles([]);
    setTaskId(null);
    setTaskStatus(null);
    setError(null);
    if (pollingInterval.current) {
      clearInterval(pollingInterval.current);
    }
  };

  const validFileCount = files.filter(f => f.valid).length;
  const progress = taskStatus ?
    (taskStatus.progress.processed_files / taskStatus.progress.total_files) * 100 : 0;

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        📄 Document Ingestion (Docling)
      </Typography>

      {/* Collection Selection */}
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Target Collection</InputLabel>
        <Select
          value={collection}
          onChange={(e) => setCollection(e.target.value)}
          disabled={uploading}
        >
          {collections && collections.map(c => (
            <MenuItem key={c.name} value={c.name}>
              {c.name} ({c.count || 0} docs)
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {/* File Selection */}
      {!taskId && (
        <Box sx={{ mb: 2 }}>
          <input
            accept={SUPPORTED_EXTENSIONS.join(',')}
            style={{ display: 'none' }}
            id="docling-file-upload"
            type="file"
            multiple
            onChange={handleFileSelect}
            disabled={uploading}
          />
          <label htmlFor="docling-file-upload">
            <Button
              variant="outlined"
              component="span"
              startIcon={<CloudUpload />}
              disabled={uploading}
              fullWidth
            >
              Select Documents
            </Button>
          </label>
          <Typography variant="caption" display="block" sx={{ mt: 1, color: 'text.secondary' }}>
            Supported: PDF, DOCX, PPTX, XLSX, HTML, MD, CSV (max {formatFileSize(MAX_FILE_SIZE)} each)
          </Typography>
        </Box>
      )}

      {/* File List */}
      {files.length > 0 && !taskId && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Selected Files ({validFileCount}/{files.length} valid)
          </Typography>
          <List dense>
            {files.map((f, index) => (
              <ListItem
                key={index}
                secondaryAction={
                  <IconButton edge="end" onClick={() => handleRemoveFile(index)}>
                    <Delete />
                  </IconButton>
                }
                sx={{
                  bgcolor: f.valid ? 'action.hover' : 'error.dark',
                  mb: 0.5,
                  borderRadius: 1
                }}
              >
                <ListItemIcon>
                  {f.valid ? getFileIcon(f.name) : <ErrorIcon color="error" />}
                </ListItemIcon>
                <ListItemText
                  primary={f.name}
                  secondary={
                    f.error || formatFileSize(f.size)
                  }
                  secondaryTypographyProps={{
                    color: f.error ? 'error' : 'text.secondary'
                  }}
                />
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      {/* Start Button */}
      {files.length > 0 && !taskId && (
        <Button
          variant="contained"
          onClick={handleStartIngestion}
          disabled={uploading || validFileCount === 0}
          fullWidth
          startIcon={uploading ? <CircularProgress size={20} /> : <CloudUpload />}
        >
          {uploading ? 'Starting...' : `Upload ${validFileCount} File${validFileCount !== 1 ? 's' : ''}`}
        </Button>
      )}

      {/* Progress Display */}
      {taskStatus && (
        <Box sx={{ mt: 2 }}>
          <Divider sx={{ my: 2 }} />

          <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
            <Chip
              icon={
                taskStatus.status === 'success' ? <CheckCircle /> :
                taskStatus.status === 'failed' ? <ErrorIcon /> :
                taskStatus.status === 'partial' ? <ErrorIcon /> :
                <Pending />
              }
              label={taskStatus.status.toUpperCase()}
              color={
                taskStatus.status === 'success' ? 'success' :
                taskStatus.status === 'failed' ? 'error' :
                taskStatus.status === 'partial' ? 'warning' :
                'info'
              }
            />
            <Chip label={`${taskStatus.progress.processed_files}/${taskStatus.progress.total_files} files`} />
            <Chip label={`${taskStatus.progress.total_chunks} chunks`} color="primary" />
          </Stack>

          {polling && (
            <Box sx={{ mb: 2 }}>
              <LinearProgress variant="determinate" value={progress} />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                Processing... {Math.round(progress)}%
              </Typography>
            </Box>
          )}

          {/* File Results */}
          {taskStatus.file_results && taskStatus.file_results.length > 0 && (
            <Card variant="outlined" sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="subtitle2" gutterBottom>
                  Results:
                </Typography>
                <List dense>
                  {taskStatus.file_results.map((result, idx) => (
                    <ListItem key={idx}>
                      <ListItemIcon>
                        {result.skipped ? <ContentCopy color="warning" /> :
                         result.success ? <CheckCircle color="success" /> :
                         <ErrorIcon color="error" />}
                      </ListItemIcon>
                      <ListItemText
                        primary={result.filename}
                        secondary={
                          result.skipped ? `Skipped: ${result.error}` :
                          result.success ? `${result.chunks} chunks (${result.processing_time}s)` :
                          `Error: ${result.error}`
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          )}

          {/* Summary */}
          {!polling && (
            <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
              <Chip
                icon={<CheckCircle />}
                label={`${taskStatus.progress.successful_files} success`}
                color="success"
                size="small"
              />
              {taskStatus.progress.failed_files > 0 && (
                <Chip
                  icon={<ErrorIcon />}
                  label={`${taskStatus.progress.failed_files} failed`}
                  color="error"
                  size="small"
                />
              )}
              {taskStatus.progress.skipped_files > 0 && (
                <Chip
                  icon={<ContentCopy />}
                  label={`${taskStatus.progress.skipped_files} duplicates`}
                  color="warning"
                  size="small"
                />
              )}
            </Stack>
          )}

          {!polling && (
            <Button
              variant="outlined"
              onClick={handleReset}
              fullWidth
              sx={{ mt: 2 }}
            >
              Upload More Documents
            </Button>
          )}
        </Box>
      )}

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {taskStatus && taskStatus.error_message && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {taskStatus.error_message}
        </Alert>
      )}
    </Paper>
  );
}
