import React, { useState, useEffect } from 'react';
import {
    Box,
    Button,
    Typography,
    CircularProgress,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Alert
} from '@mui/material';
import { CheckCircle, Error as ErrorIcon, Refresh } from '@mui/icons-material';
import axios from 'axios';

const SystemCheck = () => {
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);

    const runCheck = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await axios.post('http://localhost:33800/api/v1/onboarding/run/system_check');
            setResults(response.data);
        } catch (err) {
            setError("Failed to run system check. Is the backend running?");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        runCheck();
    }, []);

    if (loading) {
        return (
            <Box display="flex" flexDirection="column" alignItems="center" p={3}>
                <CircularProgress size={40} sx={{ mb: 2 }} />
                <Typography>Running system diagnostics...</Typography>
            </Box>
        );
    }

    if (error) {
        return (
            <Box>
                <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>
                <Button startIcon={<Refresh />} onClick={runCheck} variant="contained">Retry</Button>
            </Box>
        );
    }

    if (!results) return null;

    return (
        <Box>
            <Typography variant="h6" gutterBottom>
                System Status: {results.overall_status === 'ok' ?
                    <span style={{ color: 'green' }}>Healthy ✅</span> :
                    <span style={{ color: 'red' }}>Issues Found ❌</span>}
            </Typography>

            <List>
                {results.checks.map((check, index) => (
                    <ListItem key={index}>
                        <ListItemIcon>
                            {check.status === 'ok' ?
                                <CheckCircle color="success" /> :
                                <ErrorIcon color="error" />
                            }
                        </ListItemIcon>
                        <ListItemText
                            primary={check.component}
                            secondary={
                                <React.Fragment>
                                    <Typography component="span" variant="body2" color="text.primary">
                                        {check.message}
                                    </Typography>
                                    {check.details && (
                                        <Typography component="div" variant="caption" color="error" sx={{ mt: 0.5 }}>
                                            Details: {check.details}
                                        </Typography>
                                    )}
                                </React.Fragment>
                            }
                        />
                    </ListItem>
                ))}
            </List>

            <Box mt={2}>
                <Button startIcon={<Refresh />} onClick={runCheck} variant="outlined">Re-run Checks</Button>
            </Box>
        </Box>
    );
};

export default SystemCheck;
