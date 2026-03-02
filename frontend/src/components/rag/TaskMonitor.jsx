import React, { useState, useEffect } from 'react';
import {
    Box,
    Paper,
    Typography,
    List,
    ListItem,
    ListItemText,
    ListItemIcon,
    Chip,
    IconButton,
    LinearProgress,
    Alert
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import CancelIcon from '@mui/icons-material/Cancel';
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';
import ScheduleIcon from '@mui/icons-material/Schedule';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import client from '../../api/client';

const TaskMonitor = () => {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchTasks = async () => {
        setLoading(true);
        try {
            const response = await client.get('/tasks/');
            setTasks(response.data.tasks || []);
            setError(null);
        } catch (err) {
            console.error("Failed to fetch tasks:", err);
            setError("Could not load tasks. Is Redis running?");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTasks();
        const interval = setInterval(fetchTasks, 3000); // Poll every 3s
        return () => clearInterval(interval);
    }, []);

    const handleCancel = async (taskId) => {
        if (!window.confirm("Are you sure you want to cancel this task?")) return;
        try {
            await client.post(`/tasks/${taskId}/cancel`);
            fetchTasks();
        } catch (err) {
            alert("Failed to cancel task");
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'ACTIVE': return 'primary';
            case 'SCHEDULED': return 'warning';
            case 'RESERVED': return 'info';
            default: return 'default';
        }
    };

    return (
        <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">Active Background Tasks</Typography>
                <IconButton onClick={fetchTasks} disabled={loading}>
                    <RefreshIcon />
                </IconButton>
            </Box>

            {error && <Alert severity="warning" sx={{ mb: 2 }}>{error}</Alert>}

            {tasks.length === 0 && !error ? (
                <Paper sx={{ p: 3, textAlign: 'center', color: 'text.secondary' }}>
                    <CheckCircleIcon sx={{ fontSize: 40, mb: 1, opacity: 0.5 }} />
                    <Typography>No active tasks. System is idle.</Typography>
                </Paper>
            ) : (
                <List>
                    {tasks.map((task) => (
                        <Paper key={task.id} sx={{ mb: 1 }}>
                            <ListItem
                                secondaryAction={
                                    <IconButton edge="end" aria-label="cancel" onClick={() => handleCancel(task.id)}>
                                        <CancelIcon />
                                    </IconButton>
                                }
                            >
                                <ListItemIcon>
                                    {task.status === 'SCHEDULED' ? <ScheduleIcon /> : <PlayCircleOutlineIcon color="primary" />}
                                </ListItemIcon>
                                <ListItemText
                                    primary={task.name}
                                    secondary={
                                        <Box>
                                            <Typography variant="caption" display="block">ID: {task.id}</Typography>
                                            <Typography variant="caption">Worker: {task.worker}</Typography>
                                            {task.args && <Typography variant="caption" display="block">Args: {JSON.stringify(task.args)}</Typography>}
                                        </Box>
                                    }
                                />
                                <Chip label={task.status} color={getStatusColor(task.status)} size="small" sx={{ mr: 2 }} />
                            </ListItem>
                            {task.status === 'ACTIVE' && <LinearProgress />}
                        </Paper>
                    ))}
                </List>
            )}
        </Box>
    );
};

export default TaskMonitor;
