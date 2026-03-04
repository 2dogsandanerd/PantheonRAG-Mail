import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Button,
    Alert,
    CircularProgress
} from '@mui/material';
import { Save } from '@mui/icons-material';
import axios from 'axios';

const ModelSelector = () => {
    const [currentModel, setCurrentModel] = useState('');
    const [availableModels, setAvailableModels] = useState([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState(null); // { type: 'success' | 'error', text: '' }

    useEffect(() => {
        const fetchData = async () => {
            try {
                // 1. Fetch available models
                const modelsResp = await axios.get('http://localhost:33800/api/v1/config/models');
                setAvailableModels(modelsResp.data.models);

                // 2. Fetch current config
                const configResp = await axios.get('http://localhost:33800/api/v1/config/config');
                if (configResp.data && configResp.data.LLM_MODEL) {
                    setCurrentModel(configResp.data.LLM_MODEL);
                }
            } catch (err) {
                console.error("Failed to fetch data", err);
                // Fallback if API fails
                setAvailableModels([
                    { id: 'gpt-4', name: 'OpenAI GPT-4 (Fallback)' },
                    { id: 'mistral', name: 'Mistral (Fallback)' }
                ]);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const handleSave = async () => {
        setSaving(true);
        setMessage(null);
        try {
            await axios.post('http://localhost:33800/api/v1/config/config', {
                LLM_MODEL: currentModel
            });
            setMessage({ type: 'success', text: 'Model configuration saved successfully!' });
        } catch (err) {
            console.error("Failed to save model", err);
            setMessage({ type: 'error', text: 'Failed to save configuration.' });
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return <CircularProgress size={24} />;
    }

    return (
        <Box maxWidth="sm">
            <Typography variant="h6" gutterBottom>
                Select Language Model
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
                Choose the AI model that will be used to generate email replies.
                Local models (Ollama) ensure privacy but require more system resources.
            </Typography>

            {message && (
                <Alert severity={message.type} sx={{ mb: 2 }}>
                    {message.text}
                </Alert>
            )}

            <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel id="model-select-label">AI Model</InputLabel>
                <Select
                    labelId="model-select-label"
                    value={currentModel}
                    label="AI Model"
                    onChange={(e) => setCurrentModel(e.target.value)}
                >
                    {availableModels.map((model) => (
                        <MenuItem key={model.id} value={model.id}>
                            {model.name}
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>

            <Button
                variant="contained"
                startIcon={saving ? <CircularProgress size={20} color="inherit" /> : <Save />}
                onClick={handleSave}
                disabled={saving || !currentModel}
            >
                Save Configuration
            </Button>
        </Box>
    );
};

export default ModelSelector;
