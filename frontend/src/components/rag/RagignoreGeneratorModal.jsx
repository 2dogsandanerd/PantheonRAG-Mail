import React, { useState } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Stepper,
    Step,
    StepLabel,
    TextField,
    FormControlLabel,
    Checkbox,
    Typography,
    Box,
    CircularProgress,
    Alert,
    Paper,
    Divider,
    Grid,
    Tooltip,
    IconButton
} from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import SaveIcon from '@mui/icons-material/Save';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { generateRagignore, saveRagignore } from '../../api/rag';

const steps = ['Configuration', 'Review & Edit', 'Save'];

const RagignoreGeneratorModal = ({ open, onClose, folderPath, onSaveSuccess }) => {
    const [activeStep, setActiveStep] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [successMsg, setSuccessMsg] = useState(null);

    // Config State
    const [config, setConfig] = useState({
        folderPath: folderPath || '',
        includeExamples: true,
        aggressive: false
    });

    // Generated Result State
    const [result, setResult] = useState({
        ragignore: '',
        analysis_summary: null,
        reasoning: '',
        detected_categories: {}
    });

    const handleNext = async () => {
        setError(null);

        if (activeStep === 0) {
            // Step 1 -> 2: Generate
            setLoading(true);
            try {
                const data = await generateRagignore(
                    config.folderPath,
                    config.includeExamples,
                    config.aggressive
                );
                setResult(data);
                setActiveStep(1);
            } catch (err) {
                setError(err.response?.data?.detail || 'Failed to generate .ragignore');
            } finally {
                setLoading(false);
            }
        } else if (activeStep === 1) {
            // Step 2 -> 3: Save
            setLoading(true);
            try {
                await saveRagignore(config.folderPath, result.ragignore);
                setSuccessMsg('.ragignore saved successfully!');
                if (onSaveSuccess) onSaveSuccess();
                setActiveStep(2);
            } catch (err) {
                setError(err.response?.data?.detail || 'Failed to save .ragignore');
            } finally {
                setLoading(false);
            }
        } else {
            // Step 3: Close
            handleClose();
        }
    };

    const handleBack = () => {
        setActiveStep((prev) => prev - 1);
        setError(null);
    };

    const handleClose = () => {
        onClose();
        // Reset state after transition
        setTimeout(() => {
            setActiveStep(0);
            setResult({ ragignore: '', analysis_summary: null });
            setError(null);
            setSuccessMsg(null);
        }, 300);
    };

    const copyToClipboard = () => {
        navigator.clipboard.writeText(result.ragignore);
    };

    return (
        <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
            <DialogTitle>Generate .ragignore File</DialogTitle>

            <DialogContent dividers>
                <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
                    {steps.map((label) => (
                        <Step key={label}>
                            <StepLabel>{label}</StepLabel>
                        </Step>
                    ))}
                </Stepper>

                {error && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {error}
                    </Alert>
                )}

                {/* Step 1: Configuration */}
                {activeStep === 0 && (
                    <Box>
                        <Typography variant="body1" gutterBottom>
                            Analyze your folder structure and generate an optimized .ragignore file to exclude irrelevant files from RAG ingestion.
                        </Typography>

                        <TextField
                            fullWidth
                            label="Folder Path"
                            value={config.folderPath}
                            onChange={(e) => setConfig({ ...config, folderPath: e.target.value })}
                            margin="normal"
                            helperText="Absolute path to the project root"
                        />

                        <Box sx={{ mt: 2 }}>
                            <FormControlLabel
                                control={
                                    <Checkbox
                                        checked={config.includeExamples}
                                        onChange={(e) => setConfig({ ...config, includeExamples: e.target.checked })}
                                    />
                                }
                                label="Include helpful comments and examples"
                            />
                            <br />
                            <FormControlLabel
                                control={
                                    <Checkbox
                                        checked={config.aggressive}
                                        onChange={(e) => setConfig({ ...config, aggressive: e.target.checked })}
                                    />
                                }
                                label="Aggressive Mode (Exclude more strictly)"
                            />
                        </Box>
                    </Box>
                )}

                {/* Step 2: Review & Edit */}
                {activeStep === 1 && result && (
                    <Grid container spacing={2}>
                        <Grid item xs={12} md={8}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                <Typography variant="subtitle2">Preview & Edit:</Typography>
                                <Tooltip title="Copy to Clipboard">
                                    <IconButton size="small" onClick={copyToClipboard}>
                                        <ContentCopyIcon fontSize="small" />
                                    </IconButton>
                                </Tooltip>
                            </Box>
                            <TextField
                                fullWidth
                                multiline
                                rows={15}
                                value={result.ragignore}
                                onChange={(e) => setResult({ ...result, ragignore: e.target.value })}
                                variant="outlined"
                                sx={{ fontFamily: 'monospace' }}
                            />
                        </Grid>
                        <Grid item xs={12} md={4}>
                            <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
                                <Typography variant="h6" gutterBottom>Analysis</Typography>

                                {result.analysis_summary && (
                                    <Box sx={{ mb: 2 }}>
                                        <Typography variant="body2"><strong>Total Files:</strong> {result.analysis_summary.total_files}</Typography>
                                        <Typography variant="body2" color="error"><strong>Ignored:</strong> {result.analysis_summary.files_to_ignore}</Typography>
                                        <Typography variant="body2" color="success.main"><strong>Kept:</strong> {result.analysis_summary.files_to_keep}</Typography>
                                        <Divider sx={{ my: 1 }} />
                                        <Typography variant="body2">
                                            <strong>Size Reduction:</strong> ~{result.analysis_summary.estimated_size_reduction_mb} MB
                                        </Typography>
                                    </Box>
                                )}

                                <Typography variant="subtitle2" gutterBottom>Reasoning:</Typography>
                                <Typography variant="caption" color="text.secondary">
                                    {result.reasoning}
                                </Typography>
                            </Paper>
                        </Grid>
                    </Grid>
                )}

                {/* Step 3: Success */}
                {activeStep === 2 && (
                    <Box sx={{ textAlign: 'center', py: 4 }}>
                        <CheckCircleIcon color="success" sx={{ fontSize: 60, mb: 2 }} />
                        <Typography variant="h5" gutterBottom>
                            Success!
                        </Typography>
                        <Typography variant="body1">
                            The .ragignore file has been saved to:
                        </Typography>
                        <Paper variant="outlined" sx={{ p: 1, mt: 2, display: 'inline-block', bgcolor: 'grey.100' }}>
                            <code>{config.folderPath}/.ragignore</code>
                        </Paper>
                    </Box>
                )}

            </DialogContent>

            <DialogActions>
                {activeStep < 2 && (
                    <Button onClick={activeStep === 0 ? handleClose : handleBack} disabled={loading}>
                        {activeStep === 0 ? 'Cancel' : 'Back'}
                    </Button>
                )}

                <Button
                    variant="contained"
                    onClick={handleNext}
                    disabled={loading || (activeStep === 0 && !config.folderPath)}
                    startIcon={loading ? <CircularProgress size={20} color="inherit" /> : (activeStep === 1 ? <SaveIcon /> : null)}
                >
                    {loading ? 'Processing...' : (activeStep === 0 ? 'Generate Preview' : (activeStep === 1 ? 'Save File' : 'Close'))}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default RagignoreGeneratorModal;
