import React, { useState, useEffect } from 'react';
import {
  Paper, Box, Button, TextField, Typography, LinearProgress,
  Alert, Stack, Slider, FormControl, InputLabel, Select, MenuItem,
  List, ListItem, ListItemText, ListItemIcon, IconButton, Chip
} from '@mui/material';
import {
  CloudUpload, Delete, Description, PictureAsPdf,
  TextSnippet, CheckCircle, Error as ErrorIcon
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { uploadRAGDocuments, validateUpload } from '../../api/client';

const getFileIcon = (filename) => {
  if (filename.endsWith('.pdf')) return <PictureAsPdf color="error" />;
  if (filename.endsWith('.md')) return <Description color="primary" />;
  if (filename.endsWith('.txt')) return <TextSnippet color="info" />;
  return <Description />;
};

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export default function DocumentUploader({ collection, onUploadSuccess, onUploadStateChange }) {
  const { t } = useTranslation();
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [chunkSize, setChunkSize] = useState(500);
  const [chunkOverlap, setChunkOverlap] = useState(50);
  const [chunkStrategy, setChunkStrategy] = useState('recursive');
  const [validationResult, setValidationResult] = useState(null);
  const [validating, setValidating] = useState(false);
  const [filePreview, setFilePreview] = useState('');

  // Notify parent component when upload state changes
  useEffect(() => {
    if (onUploadStateChange) {
      onUploadStateChange(uploading);
    }
  }, [uploading, onUploadStateChange]);

  // Validate upload compatibility when collection changes
  useEffect(() => {
    const checkValidation = async () => {
      if (!collection) return;

      setValidating(true);
      try {
        const result = await validateUpload(collection);
        setValidationResult(result);
      } catch (error) {
        // Handle validation errors (e.g., 400 from backend)
        if (error.response && error.response.status === 400) {
          setValidationResult(error.response.data);
        } else {
          console.error('Validation check failed:', error);
          setValidationResult(null);
        }
      } finally {
        setValidating(false);
      }
    };

    checkValidation();
  }, [collection]);

  const readFileAsText = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = (e) => reject(e);

      // Check file type
      if (file.type.includes('text') || file.name.endsWith('.md') || file.name.endsWith('.txt')) {
        reader.readAsText(file);
      } else if (file.name.endsWith('.json')) {
        reader.readAsText(file);
      } else {
        // For binary files, show metadata
        resolve(`Binär-Datei: ${file.name}\nGröße: ${(file.size / 1024).toFixed(2)} KB\nTyp: ${file.type}`);
      }
    });
  };

  const handleFileSelect = async (event) => {
    const selectedFiles = Array.from(event.target.files);
    const validFiles = selectedFiles.filter(file => {
      const extension = file.name.split('.').pop().toLowerCase();
      return ['txt', 'md', 'pdf', 'json', 'xml', 'csv'].includes(extension);
    });

    if (validFiles.length !== selectedFiles.length) {
      setResult({
        success: false,
        message: 'Some files were skipped. Only .txt, .md, .pdf, .json, .xml, and .csv files are supported.'
      });
    }

    setFiles(prev => [...prev, ...validFiles]);
    setResult(null);

    // Generate preview for first file
    if (validFiles.length > 0) {
      const file = validFiles[0];
      try {
        const text = await readFileAsText(file);
        setFilePreview(text.substring(0, 500));
      } catch (error) {
        setFilePreview('Vorschau nicht verfügbar');
      }
    }
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    setUploading(true);
    setProgress(0);
    setResult(null);

    try {
      const data = await uploadRAGDocuments(files, collection, chunkSize, chunkOverlap);
      setResult(data);
      setFiles([]);
      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (error) {
      setResult({ 
        success: false, 
        message: error.response?.data?.detail || error.message 
      });
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  const totalSize = files.reduce((sum, file) => sum + file.size, 0);

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        📤 Upload Documents to "{collection}"
      </Typography>

      <Stack spacing={3}>
        {/* Embedding Validation */}
        {validating ? (
          <Alert severity="info">
            <Typography variant="body2">Checking embedding compatibility...</Typography>
          </Alert>
        ) : validationResult && !validationResult.valid ? (
          <Alert severity="error">
            <Typography variant="body2" gutterBottom>
              <strong>⚠️ Embedding Mismatch Detected!</strong>
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              Collection requires: <strong>{validationResult.collection_model}</strong> ({validationResult.collection_dims} dims)<br/>
              Current settings: <strong>{validationResult.current_model}</strong> ({validationResult.current_dims} dims)
            </Typography>
            <Typography variant="body2">
              {validationResult.suggestion}
            </Typography>
          </Alert>
        ) : validationResult && validationResult.valid ? (
          <Alert severity="success">
            <Typography variant="body2">
              ✅ <strong>Compatible</strong> - Upload will work correctly
              {validationResult.collection_model && (
                <> (Using <strong>{validationResult.collection_model}</strong>)</>
              )}
            </Typography>
          </Alert>
        ) : null}

        {/* Chunk Configuration */}
        <Box>
          <Typography variant="subtitle1" gutterBottom>
            Chunk Configuration
          </Typography>
          <Stack spacing={2}>
            <Box>
              <Typography variant="caption" gutterBottom>
                Chunk Size: {chunkSize} characters
              </Typography>
              <Slider
                value={chunkSize}
                onChange={(e, v) => setChunkSize(v)}
                min={100}
                max={2000}
                step={50}
                marks={[
                  { value: 100, label: '100' },
                  { value: 500, label: '500' },
                  { value: 1000, label: '1000' },
                  { value: 2000, label: '2000' }
                ]}
                disabled={uploading}
              />
            </Box>

            <Box>
              <Typography variant="caption" gutterBottom>
                Chunk Overlap: {chunkOverlap} characters
              </Typography>
              <Slider
                value={chunkOverlap}
                onChange={(e, v) => setChunkOverlap(v)}
                min={0}
                max={500}
                step={10}
                disabled={uploading}
              />
            </Box>

            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Chunking Strategy</InputLabel>
              <Select
                value={chunkStrategy}
                onChange={(e) => setChunkStrategy(e.target.value)}
                label="Chunking Strategy"
                disabled={uploading}
              >
                <MenuItem value="recursive">Recursive Character Splitter</MenuItem>
                <MenuItem value="markdown">Markdown Header Splitter</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </Box>

        {/* File Selection */}
        <Box>
          <Button
            variant="outlined"
            component="label"
            startIcon={<CloudUpload />}
            disabled={uploading}
            sx={{ mb: 2 }}
          >
            Select Files (TXT, MD, PDF, JSON, XML, CSV)
            <input
              type="file"
              hidden
              multiple
              accept=".txt,.md,.pdf,.json,.xml,.csv"
              onChange={handleFileSelect}
            />
          </Button>

          {files.length > 0 && (
            <Paper sx={{ p: 2, mb: 2, bgcolor: 'background.default' }}>
              <Typography variant="subtitle2" gutterBottom>
                📄 Preview: {files[0].name}
              </Typography>
              <Box
                sx={{
                  mt: 1,
                  p: 1,
                  bgcolor: 'background.paper',
                  borderRadius: 1,
                  maxHeight: '200px',
                  overflow: 'auto',
                  fontFamily: 'monospace',
                  fontSize: '0.75rem',
                  whiteSpace: 'pre-wrap'
                }}
              >
                {filePreview || 'Lädt Preview...'}
              </Box>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Erste 500 Zeichen des Dokuments
              </Typography>
            </Paper>
          )}

          {files.length > 0 && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Selected Files ({files.length} files, {formatFileSize(totalSize)})
              </Typography>
              <List dense>
                {files.map((file, index) => (
                  <ListItem
                    key={index}
                    secondaryAction={
                      <IconButton 
                        edge="end" 
                        onClick={() => removeFile(index)}
                        disabled={uploading}
                      >
                        <Delete />
                      </IconButton>
                    }
                    sx={{ 
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 1,
                      mb: 1
                    }}
                  >
                    <ListItemIcon>
                      {getFileIcon(file.name)}
                    </ListItemIcon>
                    <ListItemText
                      primary={file.name}
                      secondary={`${formatFileSize(file.size)} • ${file.type || 'Unknown type'}`}
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </Box>

        {/* Upload Button */}
        <Button
          variant="contained"
          onClick={handleUpload}
          disabled={uploading || files.length === 0 || (validationResult && !validationResult.valid)}
          fullWidth
          size="large"
          startIcon={uploading ? <LinearProgress size={20} /> : <CloudUpload />}
        >
          {uploading
            ? `Uploading to ${collection}...`
            : (validationResult && !validationResult.valid)
              ? `Upload Blocked (Embedding Mismatch)`
              : `Upload ${files.length} file(s) to ${collection}`
          }
        </Button>

        {uploading && (
          <Box>
            <Typography variant="caption" gutterBottom>
              Processing files...
            </Typography>
            <LinearProgress />
          </Box>
        )}

        {/* Results */}
        {result && (
          <Alert 
            severity={result.success ? 'success' : 'error'}
            icon={result.success ? <CheckCircle /> : <ErrorIcon />}
          >
            {result.success ? (
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  ✅ Upload Successful!
                </Typography>
                <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 1 }}>
                  <Chip label={`${result.files_processed} files`} size="small" />
                  <Chip label={`${result.total_chunks} chunks`} size="small" />
                </Stack>
                {result.results && (
                  <Box sx={{ mt: 1 }}>
                    {result.results.map((fileResult, index) => (
                      <Typography key={index} variant="caption" display="block">
                        • {fileResult.filename}: {fileResult.chunks} chunks
                      </Typography>
                    ))}
                  </Box>
                )}
              </Box>
            ) : (
              <Typography>
                ❌ Error: {result.message}
              </Typography>
            )}
          </Alert>
        )}

        {/* Help Text */}
        <Alert severity="info">
          <Typography variant="body2">
            <strong>Supported formats:</strong> TXT, MD, PDF<br/>
            <strong>Chunk Size:</strong> Smaller chunks (100-500) for precise matching, larger chunks (1000-2000) for context<br/>
            <strong>Chunk Overlap:</strong> Higher overlap preserves context across chunk boundaries
          </Typography>
        </Alert>
      </Stack>
    </Paper>
  );
}