import React, { useState, useEffect } from 'react';
import { Box, Grid, Paper, Typography, Tooltip, useTheme } from '@mui/material';
import { Circle } from '@mui/icons-material';
import { getServicesStatus, getBackendHealth, API_ROOT } from '../../api/client';

const ServiceStatusCard = ({ name, status, host, port, error }) => {
  const theme = useTheme();

  // Handle different status formats - support both boolean and object formats
  let isRunning = false;
  let statusString = 'stopped';

  if (typeof status === 'object' && status !== null) {
    // New format: { running: boolean, status: string, ... }
    isRunning = status.running || status.status === 'running';
    statusString = status.status || (status.running ? 'running' : 'stopped');
  } else if (typeof status === 'boolean') {
    // Legacy format: just boolean
    isRunning = status;
    statusString = status ? 'running' : 'stopped';
  } else if (typeof status === 'string') {
    // Legacy format: just status string
    isRunning = status === 'running';
    statusString = status;
  }

  const tooltipTitle = () => {
    if (error) return `Error: ${error}`;
    if (isRunning) return `Running on ${host}:${port}`;
    return `Status: ${statusString || 'stopped'}`;
  };

  return (
    <Tooltip title={tooltipTitle()} arrow>
      <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2, border: `1px solid ${theme.palette.divider}` }}>
        <Circle sx={{ color: isRunning ? theme.palette.success.main : theme.palette.error.main, fontSize: '1rem' }} />
        <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
          {name}
        </Typography>
      </Paper>
    </Tooltip>
  );
};

const ServiceStatusWidget = () => {
  const [status, setStatus] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const getStatus = async () => {
    try {
      const [health, data] = await Promise.all([
        getBackendHealth().catch(() => ({ status: 'down' })),
        getServicesStatus()
      ]);
      const backendRunning = !!(health && (health.status === 'healthy' || health.status === 'ok'));
      setStatus({ backend: { running: backendRunning }, ...data });
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Failed to fetch service status:', error);
      // If the API call fails, the backend is down
      setStatus({ backend: { running: false }, ollama: { running: false }, chroma: { running: false } });
    }
  };

  useEffect(() => {
    getStatus(); // Initial fetch
    // ❌ POLLING REMOVED - Phase 2/3: Use WebSocket from Dashboard instead
    // const intervalId = setInterval(getStatus, 10000);
    // return () => clearInterval(intervalId);
  }, []);

  return (
    <Box sx={{ mb: 3 }}>
        <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
                <ServiceStatusCard
                  name="Backend"
                  status={status?.backend?.running}
                  host={(() => { try { const u = new URL(API_ROOT()); return u.hostname; } catch { return 'localhost'; } })()}
                  port={(() => { try { const u = new URL(API_ROOT()); return u.port || '33800'; } catch { return '33800'; } })()}
                />
            </Grid>
            <Grid item xs={12} sm={4}>
                <ServiceStatusCard name="Ollama" {...status?.ollama} />
            </Grid>
            <Grid item xs={12} sm={4}>
                <ServiceStatusCard name="ChromaDB" {...status?.chroma} />
            </Grid>
        </Grid>
    </Box>
  );
};

export default ServiceStatusWidget;
