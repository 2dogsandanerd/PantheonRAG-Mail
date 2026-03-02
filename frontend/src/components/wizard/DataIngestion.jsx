import React, { useState } from 'react';
import {
    Box,
    Typography,
    TextField,
    Button,
    CircularProgress,
    Alert,
    List,
    ListItem,
    ListItemText,
    Paper
} from '@mui/material';
import { FolderOpen, CloudUpload } from '@mui/icons-material';
import axios from 'axios';

const DataIngestion = () => {
    const [folderPath, setFolderPath] = useState('');
    const [loading, setLoading] = useState(false);
    const [scanResult, setScanResult] = useState(null);
    const [error, setError] = useState(null);

    const handleScan = async () => {
        if (!folderPath) return;

        setLoading(true);
        setError(null);
        setScanResult(null);

        const formData = new FormData();
        formData.append('folder_path', folderPath);
        formData.append('recursive', 'true');

        try {
            // Note: The endpoint expects form data
            const response = await axios.post('http://localhost:33800/api/v1/rag/ingestion/scan-folder', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            setScanResult(response.data);
        } catch (err) {
            console.error("Scan failed", err);
            setError(err.response?.data?.detail || "Failed to scan folder. Please check the path.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box maxWidth="md">
            <Typography variant="h6" gutterBottom>
                Data Ingestion
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
                Point the system to a local folder containing your documents (PDF, TXT, MD).
                The system will scan and index them for the RAG knowledge base.
            </Typography>

            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
                <TextField
                    fullWidth
                    label="Local Folder Path"
                    placeholder="/home/user/documents"
                    value={folderPath}
                    onChange={(e) => setFolderPath(e.target.value)}
                    variant="outlined"
                    size="small"
                />
                <Button
                    variant="contained"
                    startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <FolderOpen />}
                    onClick={handleScan}
                    disabled={loading || !folderPath}
                >
                    Scan
                </Button>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
            )}

            {scanResult && (
                <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                        Scan Results
                    </Typography>
                    <Typography variant="body2">
                        Found {scanResult.total_files} files ({scanResult.summary && Object.entries(scanResult.summary).map(([ext, count]) => `${ext}: ${count}`).join(', ')})
                    </Typography>

                    {scanResult.edition_limitations && (
                        <Alert severity="warning" sx={{ mt: 1 }}>
                            {scanResult.edition_limitations.message}
                        </Alert>
                    )}

                    <Box sx={{ mt: 2, maxHeight: 200, overflow: 'auto' }}>
                        <List dense>
                            {scanResult.files.slice(0, 10).map((file, index) => (
                                <ListItem key={index}>
                                    <ListItemText
                                        primary={file.filename}
                                        secondary={`${file.size_human} - ${file.path}`}
                                    />
                                </ListItem>
                            ))}
                            {scanResult.files.length > 10 && (
                                <ListItem>
                                    <ListItemText secondary={`...and ${scanResult.files.length - 10} more files`} />
                                </ListItem>
                            )}
                        </List>
                    </Box>

                    <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                        <Button
                            variant="contained"
                            color="secondary"
                            startIcon={<CloudUpload />}
                            disabled
                        >
                            Start Indexing (Coming Soon)
                        </Button>
                    </Box>
                </Paper>
            )}
        </Box>
    );
};

export default DataIngestion;
