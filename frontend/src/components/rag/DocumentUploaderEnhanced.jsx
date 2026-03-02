import React, { useState } from 'react';
import {
  Paper, Box, Button, TextField, Typography, LinearProgress,
  Alert, Stack, Slider, FormControl, InputLabel, Select, MenuItem,
  List, ListItem, ListItemText, ListItemIcon, IconButton, Chip,
  Stepper, Step, StepLabel, CircularProgress, Dialog, DialogTitle,
  DialogContent, DialogActions
} from '@mui/material';
import {
  CloudUpload, Delete, Description, PictureAsPdf,
  TextSnippet, CheckCircle, Error as ErrorIcon, Psychology, Folder
} from '@mui/icons-material';
import { uploadRAGDocuments, analyzeDocument } from '../../api/client';

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

const UPLOAD_STEPS = ['Select Files', 'Configure', 'Upload'];

export default function DocumentUploaderEnhanced({ collection, collections, onUploadSuccess, onUploadStateChange }) {
  // State Machine
  const [uploadStep, setUploadStep] = useState(0); // 0=select, 1=analyzing, 2=confirm, 3=uploading
  const [files, setFiles] = useState([]);
  const [aiRecommendation, setAiRecommendation] = useState(null);

  // Configuration
  const [targetCollection, setTargetCollection] = useState(collection);
  const [chunkSize, setChunkSize] = useState(500);
  const [chunkOverlap, setChunkOverlap] = useState(50);
  const [chunkStrategy, setChunkStrategy] = useState('recursive');

  // UI State
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  // Notify parent when upload state changes
  React.useEffect(() => {
    if (onUploadStateChange) {
      onUploadStateChange(uploading);
    }
  }, [uploading, onUploadStateChange]);

  // === STATE 0: Select Files ===
  const handleFileSelect = async (event) => {
    const selectedFiles = Array.from(event.target.files);
    const validFiles = selectedFiles.filter(file => {
      const extension = file.name.split('.').pop().toLowerCase();
      return ['txt', 'md', 'pdf'].includes(extension);
    });

    if (validFiles.length === 0) {
      setResult({ success: false, message: 'No valid files selected' });
      return;
    }

    setFiles(validFiles);
    setResult(null);

    // Move to configure step (manual AI analysis)
    setUploadStep(1);
  };

  // New functionality to handle folder selection
  const handleSelectFolder = async () => {
    try {
      const selectedPath = await window.electronAPI.selectFolder();
      if (selectedPath) {
        // For folder upload, we would need to implement a backend endpoint
        // that can handle folder scanning and upload
        alert(`Folder selected: ${selectedPath}\n\nNote: This feature requires backend implementation to scan and upload files from the folder.`);
      }
    } catch (error) {
      console.error('Error selecting folder:', error);
    }
  };

  // === STATE 1: Manual AI Analysis ===
  const handleAIAnalysis = async () => {
    if (files.length === 0) return;

    setAnalyzing(true);
    try {
      // Read first 2000 chars from first file
      const text = await files[0].text();
      const sample = text.substring(0, 2000);

      const recommendation = await analyzeDocument(sample);

      setAiRecommendation(recommendation);

      // Auto-set recommendations
      if (recommendation.recommended_collection && collections.some(c => c.name === recommendation.recommended_collection)) {
        setTargetCollection(recommendation.recommended_collection);
      }
      if (recommendation.chunk_strategy) {
        setChunkStrategy(recommendation.chunk_strategy === 'markdown_header' ? 'markdown' : 'recursive');
      }
    } catch (error) {
      console.error('AI analysis failed:', error);
      setAiRecommendation({
        recommended_collection: collection,
        chunk_strategy: 'generic_recursive',
        warning: 'AI analysis unavailable, using defaults'
      });
    } finally {
      setAnalyzing(false);
    }
  };

  // === STATE 2: Upload ===
  const handleUpload = async () => {
    if (files.length === 0) return;

    setUploadStep(2);
    setUploading(true);
    setResult(null);

    try {
      const data = await uploadRAGDocuments(files, targetCollection, chunkSize, chunkOverlap);
      setResult(data);

      if (onUploadSuccess) {
        onUploadSuccess();
      }

      // Reset to initial state after 3 seconds
      setTimeout(() => {
        setFiles([]);
        setAiRecommendation(null);
        setUploadStep(0);
        setResult(null);
      }, 3000);
    } catch (error) {
      setResult({
        success: false,
        message: error.response?.data?.detail || error.message
      });
      setUploadStep(1); // Back to configure on error
    } finally {
      setUploading(false);
    }
  };

  const handleCancel = () => {
    setFiles([]);
    setAiRecommendation(null);
    setUploadStep(0);
    setResult(null);
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const totalSize = files.reduce((sum, file) => sum + file.size, 0);

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        📤 AI-Assisted Document Upload
      </Typography>

      {/* Stepper */}
      <Stepper activeStep={uploadStep} sx={{ mb: 3 }}>
        {UPLOAD_STEPS.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Stack spacing={3}>
        {/* STATE 0: Select Files */}
        {uploadStep === 0 && (
          <Box>
            <Stack direction="column" spacing={2}>
              <Button
                variant="outlined"
                component="label"
                startIcon={<CloudUpload />}
                fullWidth
                size="large"
              >
                Select Files (TXT, MD, PDF)
                <input
                  type="file"
                  hidden
                  multiple
                  accept=".txt,.md,.pdf"
                  onChange={handleFileSelect}
                />
              </Button>
              <Button
                variant="outlined"
                startIcon={<Folder />}
                onClick={handleSelectFolder}
                fullWidth
                size="large"
              >
                Select Folder
              </Button>
            </Stack>

            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2">
                <strong>🤖 AI-Powered Workflow:</strong><br/>
                1. Select your documents<br/>
                2. AI analyzes content and recommends settings<br/>
                3. Review and adjust recommendations<br/>
                4. Upload to RAG knowledge base
              </Typography>
            </Alert>
          </Box>
        )}

        {/* STATE 1: Configure */}
        {uploadStep === 1 && (
          <Box>
            {/* AI Recommendation Display */}
            {aiRecommendation && (
              <Alert severity="info" icon={<Psychology />} sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  🤖 AI Recommendation
                </Typography>
                <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 1 }}>
                  <Chip
                    label={`Collection: ${aiRecommendation.recommended_collection || 'N/A'}`}
                    size="small"
                    color="primary"
                  />
                  <Chip
                    label={`Strategy: ${aiRecommendation.chunk_strategy || 'N/A'}`}
                    size="small"
                    color="secondary"
                  />
                </Stack>
                {aiRecommendation.warning && (
                  <Typography variant="caption" color="warning.main" sx={{ mt: 1, display: 'block' }}>
                    ⚠️ {aiRecommendation.warning}
                  </Typography>
                )}
              </Alert>
            )}

            {/* AI Analysis Button */}
            {!analyzing && (
              <Button
                variant="outlined"
                onClick={handleAIAnalysis}
                disabled={files.length === 0}
                fullWidth
                size="large"
                startIcon={<Psychology />}
                sx={{ mb: 3 }}
              >
                🤖 Analyze with AI (Optional)
              </Button>
            )}

            {/* AI Analyzing State */}
            {analyzing && (
              <Box sx={{ textAlign: 'center', py: 2, mb: 3 }}>
                <CircularProgress size={40} />
                <Typography variant="body2" sx={{ mt: 1 }}>
                  🤖 AI is analyzing your documents...
                </Typography>
              </Box>
            )}

            <Typography variant="subtitle1" gutterBottom>
              {files.length} file(s) selected ({formatFileSize(totalSize)}):
            </Typography>
            <List dense>
              {files.map((file, index) => (
                <ListItem
                  key={index}
                  sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1, mb: 1 }}
                  secondaryAction={
                    <IconButton edge="end" onClick={() => removeFile(index)}>
                      <Delete />
                    </IconButton>
                  }
                >
                  <ListItemIcon>{getFileIcon(file.name)}</ListItemIcon>
                  <ListItemText
                    primary={file.name}
                    secondary={formatFileSize(file.size)}
                  />
                </ListItem>
              ))}
            </List>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Target Collection</InputLabel>
              <Select
                value={targetCollection}
                onChange={(e) => setTargetCollection(e.target.value)}
                label="Target Collection"
              >
                {collections.map(col => (
                  <MenuItem key={col.name} value={col.name}>
                    {col.name} ({col.count} docs)
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Chunking Strategy</InputLabel>
              <Select
                value={chunkStrategy}
                onChange={(e) => setChunkStrategy(e.target.value)}
                label="Chunking Strategy"
              >
                <MenuItem value="recursive">Generic Recursive (Best for most documents)</MenuItem>
                <MenuItem value="markdown">Markdown Header (Best for .md files)</MenuItem>
              </Select>
            </FormControl>

            <Box sx={{ mb: 2 }}>
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
                  { value: 500, label: '500' },
                  { value: 1000, label: '1000' }
                ]}
              />
            </Box>

            <Stack direction="row" spacing={2}>
              <Button
                variant="contained"
                onClick={handleUpload}
                disabled={uploading || files.length === 0}
                fullWidth
                size="large"
                startIcon={<CloudUpload />}
              >
                Upload to {targetCollection}
              </Button>
              <Button
                variant="outlined"
                onClick={handleCancel}
                disabled={uploading}
                fullWidth
                size="large"
              >
                Cancel
              </Button>
            </Stack>
          </Box>
        )}

        {/* STATE 2: Uploading */}
        {uploadStep === 2 && uploading && (
          <Box>
            <Typography variant="body1" gutterBottom>
              Uploading {files.length} file(s) to {targetCollection}...
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
              </Box>
            ) : (
              <Typography>
                ❌ Error: {result.message}
              </Typography>
            )}
          </Alert>
        )}
      </Stack>
    </Paper>
  );
}
