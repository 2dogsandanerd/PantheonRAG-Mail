import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Paper,
    Button,
    TextField,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    LinearProgress,
    Alert,
    Stack,
    Card,
    CardContent
} from '@mui/material';
import { FolderOpen, CloudUpload, CheckCircle, Error as ErrorIcon } from '@mui/icons-material';
import axios from 'axios';

const KnowledgeBase = () => {
    const [folderPath, setFolderPath] = useState('');
    const [collectionName, setCollectionName] = useState('');
    const [profile, setProfile] = useState('codebase');
    const [status, setStatus] = useState('idle'); // idle, scanning, processing, success, error
    const [progress, setProgress] = useState(0);
    const [statusMessage, setStatusMessage] = useState('');
    const [taskId, setTaskId] = useState(null);
    const [error, setError] = useState(null);

    // Get Backend URL from Electron API
    const backendUrl = window.electronAPI?.getBackendURL() || 'http://localhost:33800';

    const handleSelectFolder = async () => {
        try {
            const path = await window.electronAPI.selectFolder();
            if (path) {
                setFolderPath(path);
                // Auto-suggest collection name from folder name
                const folderName = path.split(/[/\\]/).pop();
                if (!collectionName) {
                    setCollectionName(folderName.toLowerCase().replace(/[^a-z0-9]/g, '_'));
                }
            }
        } catch (err) {
            console.error("Failed to select folder:", err);
            setError("Failed to open folder dialog.");
        }
    };

    const handleIngest = async () => {
        if (!folderPath || !collectionName) {
            setError("Please select a folder and provide a collection name.");
            return;
        }

        setStatus('scanning');
        setError(null);
        setProgress(0);

        try {
            // 1. Start Ingestion
            const response = await axios.post(`${backendUrl}/api/v1/rag/ingestion/ingest-folder`, {
                folder_path: folderPath,
                collection_name: collectionName,
                profile: profile,
                recursive: true
            });

            const { task_id, files_found } = response.data;
            setTaskId(task_id);
            setStatusMessage(`Scanning complete. Found ${files_found} files. Starting ingestion...`);
            setStatus('processing');

        } catch (err) {
            console.error("Ingestion failed:", err);
            setStatus('error');
            setError(err.response?.data?.detail || "Failed to start ingestion.");
        }
    };

    // Poll Task Status
    useEffect(() => {
        let interval;
        if (status === 'processing' && taskId) {
            interval = setInterval(async () => {
                try {
                    const res = await axios.get(`${backendUrl}/api/v1/tasks/${taskId}`);
                    const task = res.data;

                    if (task.state === 'SUCCESS') {
                        setStatus('success');
                        setProgress(100);
                        setStatusMessage("Ingestion complete!");
                        clearInterval(interval);
                    } else if (task.state === 'FAILURE') {
                        setStatus('error');
                        setError(task.result?.error || "Task failed.");
                        clearInterval(interval);
                    } else if (task.state === 'PROCESSING') {
                        // Update progress
                        // Assuming task.meta contains progress info
                        const meta = task.info || {}; // Celery result backend often puts meta in 'info' or 'result' depending on config
                        if (meta.progress) {
                            setProgress(meta.progress);
                            setStatusMessage(`Processing: ${meta.current_file || ''} (${meta.processed}/${meta.total})`);
                        }
                    }
                } catch (err) {
                    console.error("Polling failed:", err);
                }
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [status, taskId, backendUrl]);

    return (
        <Box sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
            <Typography variant="h4" gutterBottom>
                Knowledge Base Ingestion
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
                Scan local folders to add code or documents to your RAG system.
            </Typography>

            <Paper sx={{ p: 4, mt: 3 }}>
                <Stack spacing={3}>

                    {/* Folder Selection */}
                    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                        <TextField
                            fullWidth
                            label="Folder Path"
                            value={folderPath}
                            InputProps={{
                                readOnly: true,
                            }}
                            variant="outlined"
                        />
                        <Button
                            variant="contained"
                            startIcon={<FolderOpen />}
                            onClick={handleSelectFolder}
                            sx={{ height: 56, minWidth: 150 }}
                        >
                            Select Folder
                        </Button>
                    </Box>

                    {/* Configuration */}
                    <Box sx={{ display: 'flex', gap: 2 }}>
                        <TextField
                            fullWidth
                            label="Collection Name"
                            value={collectionName}
                            onChange={(e) => setCollectionName(e.target.value)}
                            helperText="Unique name for this knowledge base"
                        />
                        <FormControl fullWidth>
                            <InputLabel>Ingestion Profile</InputLabel>
                            <Select
                                value={profile}
                                label="Ingestion Profile"
                                onChange={(e) => setProfile(e.target.value)}
                            >
                                <MenuItem value="codebase">Codebase (Python, JS, MD)</MenuItem>
                                <MenuItem value="documents">Documents (PDF, DOCX)</MenuItem>
                                <MenuItem value="default">Default (All)</MenuItem>
                            </Select>
                        </FormControl>
                    </Box>

                    {/* Action Button */}
                    <Button
                        variant="contained"
                        color="primary"
                        size="large"
                        startIcon={<CloudUpload />}
                        onClick={handleIngest}
                        disabled={status === 'processing' || status === 'scanning'}
                        fullWidth
                    >
                        {status === 'processing' ? 'Ingesting...' : 'Start Ingestion'}
                    </Button>

                    {/* Status & Progress */}
                    {status !== 'idle' && (
                        <Card variant="outlined" sx={{ bgcolor: 'background.default' }}>
                            <CardContent>
                                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1, justifyContent: 'space-between' }}>
                                    <Typography variant="subtitle2" color="text.secondary">
                                        {statusMessage}
                                    </Typography>
                                    <Typography variant="body2" fontWeight="bold">
                                        {Math.round(progress)}%
                                    </Typography>
                                </Box>
                                <LinearProgress
                                    variant={status === 'scanning' ? 'indeterminate' : 'determinate'}
                                    value={progress}
                                    color={status === 'error' ? 'error' : 'primary'}
                                    sx={{ height: 10, borderRadius: 5 }}
                                />
                            </CardContent>
                        </Card>
                    )}

                    {/* Success/Error Messages */}
                    {status === 'success' && (
                        <Alert icon={<CheckCircle fontSize="inherit" />} severity="success">
                            Ingestion completed successfully! You can now chat with this collection.
                        </Alert>
                    )}
                    {status === 'error' && (
                        <Alert icon={<ErrorIcon fontSize="inherit" />} severity="error">
                            {error}
                        </Alert>
                    )}

                </Stack>
            </Paper>
        </Box>
    );
};

export default KnowledgeBase;
