/**
 * Intelligent Uploader - Complete RAG Ingestion Pipeline
 *
 * Features:
 * - Folder scanning (recursive)
 * - LLM-based collection routing
 * - Docling multi-format processing
 * - Background batch ingestion
 * - Real-time progress tracking
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
  TextField,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Chip,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  FormControlLabel,
  Checkbox,
  Stack
} from '@mui/material';
import {
  FolderOpen as FolderIcon,
  SmartToy as AIIcon,
  Upload as UploadIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Folder as FolderBrowserIcon
} from '@mui/icons-material';

const API_BASE_URL = 'http://localhost:33800/api/v1';

const steps = ['Scan Folder', 'AI Analysis', 'Review & Upload'];

export default function IntelligentUploader({ collections = [], onUploadSuccess }) {
  const [activeStep, setActiveStep] = useState(0);
  const pollingInterval = useRef(null);

  // Step 1: Folder Scan
  const [folderPath, setFolderPath] = useState('');
  const [recursive, setRecursive] = useState(true);
  const [maxDepth, setMaxDepth] = useState(10);
  const [scanning, setScanning] = useState(false);
  const [scannedFiles, setScannedFiles] = useState([]);

  // Step 2: AI Analysis
  const [analyzing, setAnalyzing] = useState(false);
  const [fileAssignments, setFileAssignments] = useState([]);

  // Step 3: Upload
  const [uploading, setUploading] = useState(false);
  const [taskId, setTaskId] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(null);

  // Global
  const [error, setError] = useState(null);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingInterval.current) {
        clearInterval(pollingInterval.current);
      }
    };
  }, []);

  // ========== STEP 1: FOLDER SCAN ==========

  const handleScanFolder = async () => {
    if (!folderPath) {
      setError('Please enter a folder path');
      return;
    }

    setScanning(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('folder_path', folderPath);
      formData.append('recursive', recursive);
      formData.append('max_depth', maxDepth);

      const response = await fetch(`${API_BASE_URL}/rag/scan-folder`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Folder scan failed');
      }

      const data = await response.json();
      setScannedFiles(data.files || []);

      if (data.files.length === 0) {
        setError('No files found in the specified folder');
      } else {
        setActiveStep(1);
      }

    } catch (err) {
      setError(err.message);
    } finally {
      setScanning(false);
    }
  };

  // ========== STEP 2: AI ANALYSIS ==========

  const handleAnalyzeFiles = async () => {
    setAnalyzing(true);
    setError(null);

    try {
      // Prepare file previews (read first 2000 chars of each file)
      const filePreviews = scannedFiles.slice(0, 50).map(file => ({
        path: file.path,
        preview: `File: ${file.filename}\nExtension: ${file.extension}\nSize: ${file.size_human}`
      }));

      const response = await fetch(`${API_BASE_URL}/rag/analyze-files`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ files: filePreviews })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const data = await response.json();

      // Map analysis results to files
      const assignments = scannedFiles.map(file => {
        const analysis = data.analyses?.find(a => a.file === file.path) || {};
        return {
          file: file,
          recommendedCollection: analysis.recommended_collection || 'generic',
          confidence: analysis.confidence || 0.5,
          reasoning: analysis.reasoning || 'No analysis available',
          userCollection: analysis.recommended_collection || 'generic' // User can edit this
        };
      });

      setFileAssignments(assignments);
      setActiveStep(2);

    } catch (err) {
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleCollectionChange = (index, newCollection) => {
    const updated = [...fileAssignments];
    updated[index].userCollection = newCollection;
    setFileAssignments(updated);
  };

  // ========== STEP 3: BATCH UPLOAD ==========

  const handleStartUpload = async () => {
    setUploading(true);
    setError(null);

    try {
      // Prepare assignments for batch ingestion
      const assignments = fileAssignments.map(assignment => ({
        file: assignment.file.path,
        collection: assignment.userCollection
      }));

      const requestBody = {
        assignments: assignments,
        chunk_config: {
          chunk_size: 500,
          chunk_overlap: 50
        }
      };

      const response = await fetch(`${API_BASE_URL}/rag/ingest-batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
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
    pollingInterval.current = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/rag/ingest-status/${id}`);

        if (!response.ok) {
          throw new Error('Failed to fetch status');
        }

        const data = await response.json();
        setUploadProgress(data);

        // Stop polling if complete or failed
        if (data.status === 'success' || data.status === 'failed') {
          clearInterval(pollingInterval.current);
          setUploading(false);

          if (data.status === 'success' && onUploadSuccess) {
            onUploadSuccess();
          }
        }

      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 1000);
  };

  const handleReset = () => {
    setActiveStep(0);
    setFolderPath('');
    setScannedFiles([]);
    setFileAssignments([]);
    setTaskId(null);
    setUploadProgress(null);
    setError(null);
  };

  // ========== RENDER ==========

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return renderFolderScan();
      case 1:
        return renderAnalysis();
      case 2:
        return renderReview();
      default:
        return null;
    }
  };

  const handleSelectFolder = async () => {
    try {
      const selectedPath = await window.electronAPI.selectFolder();
      if (selectedPath) {
        setFolderPath(selectedPath);
      }
    } catch (error) {
      console.error('Error selecting folder:', error);
      setError('Failed to open folder dialog');
    }
  };

  const renderFolderScan = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        📁 Step 1: Select Folder to Scan
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        Select the folder containing your documents. The system will scan recursively for all supported file types.
      </Alert>

      <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
        <TextField
          fullWidth
          label="Folder Path"
          placeholder="Select a folder containing your documents"
          value={folderPath}
          onChange={(e) => setFolderPath(e.target.value)}
        />
        <Button
          variant="outlined"
          startIcon={<FolderBrowserIcon />}
          onClick={handleSelectFolder}
          sx={{ height: '56px' }}
        >
          Browse
        </Button>
      </Stack>

      <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
        <FormControlLabel
          control={<Checkbox checked={recursive} onChange={(e) => setRecursive(e.target.checked)} />}
          label="Include Subdirectories"
        />
        <TextField
          label="Max Depth"
          type="number"
          value={maxDepth}
          onChange={(e) => setMaxDepth(parseInt(e.target.value))}
          sx={{ width: 150 }}
        />
      </Stack>

      <Button
        variant="contained"
        startIcon={scanning ? <CircularProgress size={20} /> : <FolderIcon />}
        onClick={handleScanFolder}
        disabled={scanning || !folderPath}
      >
        {scanning ? 'Scanning...' : 'Scan Folder'}
      </Button>

      {scannedFiles.length > 0 && (
        <Alert severity="success" sx={{ mt: 3 }}>
          Found {scannedFiles.length} files!
        </Alert>
      )}
    </Box>
  );

  const renderAnalysis = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        🤖 Step 2: AI-Powered Collection Assignment
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        The AI will analyze your files and suggest the best collection for each one.
      </Alert>

      <Typography variant="body2" sx={{ mb: 2 }}>
        Files to analyze: {scannedFiles.length}
      </Typography>

      <Button
        variant="contained"
        startIcon={analyzing ? <CircularProgress size={20} /> : <AIIcon />}
        onClick={handleAnalyzeFiles}
        disabled={analyzing}
      >
        {analyzing ? 'Analyzing...' : 'Analyze with AI'}
      </Button>
    </Box>
  );

  const renderReview = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        ✅ Step 3: Review & Upload
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        Review the AI suggestions and adjust if needed. Then start the upload.
      </Alert>

      <TableContainer component={Paper} sx={{ mb: 3, maxHeight: 400 }}>
        <Table size="small" stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell>File</TableCell>
              <TableCell>AI Suggestion</TableCell>
              <TableCell>Collection</TableCell>
              <TableCell>Confidence</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {fileAssignments.map((assignment, idx) => (
              <TableRow key={idx}>
                <TableCell>{assignment.file.filename}</TableCell>
                <TableCell>
                  <Chip
                    label={assignment.recommendedCollection}
                    color="primary"
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Select
                    value={assignment.userCollection}
                    onChange={(e) => handleCollectionChange(idx, e.target.value)}
                    size="small"
                  >
                    {collections.map(col => (
                      <MenuItem key={col.name} value={col.name}>
                        {col.name}
                      </MenuItem>
                    ))}
                  </Select>
                </TableCell>
                <TableCell>
                  <Chip
                    label={`${(assignment.confidence * 100).toFixed(0)}%`}
                    size="small"
                    color={assignment.confidence > 0.7 ? 'success' : 'warning'}
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Button
        variant="contained"
        startIcon={uploading ? <CircularProgress size={20} /> : <UploadIcon />}
        onClick={handleStartUpload}
        disabled={uploading}
      >
        {uploading ? 'Uploading...' : 'Start Upload'}
      </Button>

      {uploadProgress && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Upload Progress
          </Typography>
          <LinearProgress
            variant="determinate"
            value={(uploadProgress.progress?.processed_files / uploadProgress.progress?.total_files) * 100}
            sx={{ mb: 1 }}
          />
          <Typography variant="body2">
            {uploadProgress.progress?.processed_files} / {uploadProgress.progress?.total_files} files processed
          </Typography>
          {uploadProgress.status === 'success' && (
            <Alert severity="success" sx={{ mt: 2 }}>
              ✅ Upload complete! {uploadProgress.progress?.successful_files} files uploaded successfully.
            </Alert>
          )}
        </Box>
      )}
    </Box>
  );

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        🚀 Intelligent Document Uploader
      </Typography>

      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {renderStepContent()}

      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
        <Button
          onClick={handleReset}
          startIcon={<RefreshIcon />}
        >
          Reset
        </Button>

        {activeStep > 0 && !uploading && (
          <Button
            onClick={() => setActiveStep(activeStep - 1)}
          >
            Back
          </Button>
        )}
      </Box>
    </Paper>
  );
}
