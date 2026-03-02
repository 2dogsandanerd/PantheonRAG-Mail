import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Grid, Alert, AlertTitle,
  Chip, IconButton, Tooltip, CircularProgress, LinearProgress
} from '@mui/material';
import {
  TrendingUp, Email, CheckCircle, Chat, Refresh,
  CheckCircle as CheckCircleIcon, Error, Warning
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useSnackbar } from 'notistack';
import { getDashboardStats } from '../api/client';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorDisplay } from './ErrorDisplay';
import SystemHealthCards from './dashboard/SystemHealthCards';
// ❌ DEACTIVATED: Activity Feed requires /api/v1/statistics/activities endpoint
// To reactivate:
// 1. Implement get_recent_activities() in backend/src/services/statistics_service.py
// 2. Add endpoint GET /api/v1/statistics/activities in backend/src/api/v1/statistics.py
// 3. Uncomment the import and component usage below
// import ActivityFeed from './dashboard/ActivityFeed';
// import { useServiceStatus } from '../hooks/useServiceStatus'; // ❌ MOVED to App.jsx to prevent WebSocket leak

/**
 * Stat Card Component
 *
 * Displays a single stat with icon, value, and title.
 *
 * @param {string} title - Stat label
 * @param {number} value - Stat value
 * @param {Component} icon - MUI Icon component
 * @param {string} color - MUI color (e.g., 'primary.main', 'success.main')
 */
const StatCard = ({ title, value, icon: Icon, color = 'primary.main' }) => (
  <Card
    sx={{
      height: '100%',
      transition: 'transform 0.2s, box-shadow 0.2s',
      '&:hover': {
        transform: 'translateY(-4px)',
        boxShadow: 4,
      },
      background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)',
      border: '1px solid #444'
    }}
  >
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        {Icon && (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 56,
              height: 56,
              borderRadius: 2,
              bgcolor: `${color}15`, // 15% opacity
            }}
          >
            <Icon sx={{ fontSize: 32, color: color }} />
          </Box>
        )}
        <Box>
          <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 0.5 }}>
            {value}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {title}
          </Typography>
        </Box>
      </Box>
    </CardContent>
  </Card>
);

/**
 * Connection Status Badge Component
 */
const ConnectionBadge = ({ connectionStatus, reconnectAttempt }) => {
  switch (connectionStatus) {
    case 'connecting':
      return (
        <Chip
          icon={<CircularProgress size={16} />}
          label="Connecting..."
          size="small"
          color="default"
        />
      );
    case 'connected':
      return (
        <Chip
          icon={<CheckCircleIcon />}
          label="Live"
          size="small"
          color="success"
        />
      );
    case 'reconnecting':
      return (
        <Chip
          icon={<CircularProgress size={16} />}
          label={reconnectAttempt > 0 ? `Reconnecting (${reconnectAttempt})` : 'Reconnecting...'}
          size="small"
          color="warning"
        />
      );
    case 'disconnected':
      return (
        <Chip
          icon={<Error />}
          label="Offline"
          size="small"
          color="error"
        />
      );
    default:
      return null;
  }
};

function Dashboard({ serviceStatus }) {
  const { t } = useTranslation();
  const { enqueueSnackbar } = useSnackbar();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [manualRefreshing, setManualRefreshing] = useState(false);

  // WebSocket connection passed from App.jsx to prevent leak on mount/unmount

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const data = await getDashboardStats();
        setStats(data);
        setError(null);
      } catch (err) {
        setError(err.message);
        setStats(null);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  // Manual refresh handler
  const handleManualRefresh = async () => {
    setManualRefreshing(true);
    try {
      const result = await serviceStatus.refreshStatus();
      if (result.success) {
        enqueueSnackbar('Status refreshed', { variant: 'success' });
      } else {
        enqueueSnackbar('Refresh failed', { variant: 'error' });
      }
    } catch (err) {
      enqueueSnackbar('Refresh failed', { variant: 'error' });
    } finally {
      setManualRefreshing(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message={t('common.loading')} />;
  }

  if (error) {
    return (
      <ErrorDisplay
        error={error}
        title={t('common.error')}
        onRetry={() => window.location.reload()}
      />
    );
  }

  return (
    <Box sx={{ mb: 4 }}>
      {/* Header with Connection Status and Manual Refresh */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5">
          {t('dashboard.title')}
        </Typography>

        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          {/* Connection Status Badge */}
          <ConnectionBadge
            connectionStatus={serviceStatus.connectionStatus}
            reconnectAttempt={serviceStatus.reconnectAttempt}
          />

          {/* Manual Refresh Button */}
          <Tooltip
            title={
              serviceStatus.connected
                ? "Force refresh"
                : "Refresh now (WebSocket offline)"
            }
          >
            <IconButton
              onClick={handleManualRefresh}
              disabled={manualRefreshing}
              color={serviceStatus.connected ? "default" : "primary"}
              size="small"
            >
              {manualRefreshing ? <CircularProgress size={20} /> : <Refresh />}
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Reconnection Alert */}
      {serviceStatus.connectionStatus === 'disconnected' && (
        <Alert severity="error" sx={{ mb: 2 }}>
          <AlertTitle>Connection Lost</AlertTitle>
          Real-time updates are paused. Attempting to reconnect...
        </Alert>
      )}

      {serviceStatus.connectionStatus === 'reconnecting' && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <AlertTitle>Reconnecting...</AlertTitle>
          Attempt {serviceStatus.reconnectAttempt} - establishing WebSocket connection...
          <LinearProgress sx={{ mt: 1 }} />
        </Alert>
      )}

      {/* System Health Cards - Pass WebSocket data */}
      <Box sx={{ mb: 3 }}>
        <SystemHealthCards
          status={serviceStatus.data}
          loading={serviceStatus.loading}
          connected={serviceStatus.connected}
        />
      </Box>

      {/* Quick Stats Cards */}
      {!stats && (
        <Alert severity="info">
          <AlertTitle>{t('common.error')}</AlertTitle>
          {t('inbox.noEmails')}
        </Alert>
      )}

      {stats && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title={t('dashboard.stats.learningPairs')}
              value={stats.learning?.total_pairs || 0}
              icon={Email}
              color="primary.main"
            />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title={t('dashboard.stats.totalEmails')}
              value={stats.learning?.completed_pairs || 0}
              icon={CheckCircle}
              color="success.main"
            />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title={t('dashboard.stats.draftsCreated')}
              value={stats.learning?.drafts_created || 0}
              icon={TrendingUp}
              color="warning.main"
            />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title={t('dashboard.stats.accuracy')}
              value={stats.conversations?.total_conversations || 0}
              icon={Chat}
              color="info.main"
            />
          </Grid>
        </Grid>
      )}

      {/* ❌ DEACTIVATED: Activity Feed
          Shows recent system activities (draft_created, learning_match, rag_query)
          To reactivate: See comment at top of file
      */}
      {/* <Grid container spacing={3}>
        <Grid item xs={12}>
          <ActivityFeed />
        </Grid>
      </Grid> */}
    </Box>
  );
}

export default Dashboard;
