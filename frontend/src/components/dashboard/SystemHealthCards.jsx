import React from 'react';
import { Grid, Card, CardContent, Typography, Box, Chip, Skeleton } from '@mui/material';
import { Circle, CheckCircle, Error, Timelapse, Storage, Email, Warning } from '@mui/icons-material';

/**
 * System Health Cards Component
 *
 * Displays real-time service status received via WebSocket props.
 * NO POLLING - receives data from parent Dashboard component.
 *
 * @param {Object} status - Service status from WebSocket (null if not yet received)
 * @param {boolean} loading - Whether status is still loading
 * @param {boolean} connected - Whether WebSocket is connected
 */
export default function SystemHealthCards({ status = null, loading = true, connected = false }) {
  // Use props directly - NO internal polling
  const health = status || {
    backend: { status: 'unknown' },
    ollama: { status: 'unknown', running: false },
    chroma: { status: 'unknown', running: false },
    email_client: { status: 'unknown', provider: 'unknown' }
  };

  // Add backend status based on WebSocket connection
  const backendStatus = connected ? 'online' : 'offline';

  const services = [
    {
      name: 'Backend',
      data: { status: backendStatus },
      icon: <Timelapse />
    },
    {
      name: 'Ollama',
      data: health.ollama,
      icon: <Circle sx={{ fontSize: 16 }} />
    },
    {
      name: 'ChromaDB',
      data: health.chroma,
      icon: <Storage />
    },
    {
      name: 'Email Client',
      data: health.email_client,
      icon: <Email />
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'online':
      case 'running':
      case 'connected':
        return 'success';
      case 'offline':
      case 'stopped':
      case 'disconnected':
        return 'error';
      case 'starting':
      case 'stopping':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'online':
      case 'running':
      case 'connected':
        return 'Online';
      case 'offline':
      case 'stopped':
      case 'disconnected':
        return 'Offline';
      case 'starting':
        return 'Starting';
      case 'stopping':
        return 'Stopping';
      default:
        return status || 'Unknown';
    }
  };

  return (
    <Grid container spacing={2}>
      {services.map((service, i) => {
        // Determine status - handle both 'status' and 'running' fields
        let status = service.data?.status || 'unknown';
        if (status === 'unknown' && typeof service.data?.running === 'boolean') {
          status = service.data.running ? 'running' : 'stopped';
        }

        const isOnline = ['online', 'running', 'connected'].includes(status);

        return (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <Card sx={{
              height: '100%',
              background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)',
              border: '1px solid #444'
            }}>
              <CardContent>
                {loading ? (
                  // Loading skeleton
                  <>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Skeleton variant="circular" width={16} height={16} />
                      <Skeleton variant="text" width="60%" />
                    </Box>
                    <Skeleton variant="rectangular" width={80} height={24} sx={{ mb: 1, borderRadius: 2 }} />
                  </>
                ) : (
                  // Actual content
                  <>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <Box sx={{
                        color: isOnline ? 'success.main' : 'error.main',
                        display: 'flex',
                        alignItems: 'center'
                      }}>
                        {service.icon}
                      </Box>
                      <Typography variant="subtitle2">{service.name}</Typography>
                    </Box>

                    <Chip
                      icon={isOnline ? <CheckCircle /> : <Error />}
                      label={getStatusText(status)}
                      color={getStatusColor(status)}
                      size="small"
                      sx={{ mb: 1 }}
                    />

                    {service.data?.uptime && (
                      <Typography variant="caption" sx={{ display: 'block', mt: 1, color: 'text.secondary' }}>
                        Uptime: {service.data.uptime}
                      </Typography>
                    )}

                    {service.data?.host && service.data?.port && (
                      <Typography variant="caption" sx={{ display: 'block', color: 'text.secondary' }}>
                        {service.data.host}:{service.data.port}
                      </Typography>
                    )}

                    {service.data?.error && (
                      <Typography variant="caption" sx={{ display: 'block', color: 'error.main', mt: 0.5 }}>
                        {service.data.error}
                      </Typography>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </Grid>
        );
      })}
    </Grid>
  );
}