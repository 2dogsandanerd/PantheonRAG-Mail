import React, { useEffect, useState } from 'react';
import { 
  Paper, Typography, List, ListItem, ListItemText, ListItemIcon,
  Box, Chip, CircularProgress, Alert, IconButton, Tooltip
} from '@mui/material';
import { 
  Refresh, Email, Edit, School, Storage, Psychology, 
  CheckCircle, Error, Warning, Info 
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { getRecentActivities } from '../../api/client';

const getActivityIcon = (type) => {
  switch (type) {
    case 'email_received': return <Email />;
    case 'draft_created': return <Edit />;
    case 'learning_pair': return <School />;
    case 'rag_query': return <Storage />;
    case 'llm_call': return <Psychology />;
    default: return <Info />;
  }
};

const getActivityColor = (type, status) => {
  if (status === 'PAIR_COMPLETED' || status === 'success') {
    return 'success';
  }
  if (status === 'error' || status === 'failed') {
    return 'error';
  }
  if (status === 'pending' || status === 'DRAFT_CREATED') {
    return 'warning';
  }
  return 'info';
};

const getStatusIcon = (status) => {
  if (status === 'PAIR_COMPLETED' || status === 'success') {
    return <CheckCircle sx={{ fontSize: 16 }} />;
  }
  if (status === 'error' || status === 'failed') {
    return <Error sx={{ fontSize: 16 }} />;
  }
  if (status === 'pending' || status === 'DRAFT_CREATED') {
    return <Warning sx={{ fontSize: 16 }} />;
  }
  return <Info sx={{ fontSize: 16 }} />;
};

const formatTimestamp = (timestamp) => {
  try {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) {
      return 'Just now';
    } else if (diffMins < 60) {
      return `${diffMins}m ago`;
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else if (diffDays < 7) {
      return `${diffDays}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  } catch {
    return 'Unknown';
  }
};

export default function ActivityFeed() {
  const { t } = useTranslation();
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchActivities = async (showRefreshing = false) => {
    try {
      if (showRefreshing) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);
      
      const data = await getRecentActivities(10);
      setActivities(data.activities || []);
    } catch (err) {
      setError(`Failed to load activities: ${err.message}`);
      console.error('Error loading activities:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    fetchActivities(true);
  };

  useEffect(() => {
    fetchActivities();

    // ❌ POLLING REMOVED - Phase 2/3: Event-based updates via WebSocket
    // const interval = setInterval(() => fetchActivities(), 30000);
    // return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Paper sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          📋 Recent Activity
        </Typography>
        <Tooltip title="Refresh activities">
          <IconButton 
            onClick={handleRefresh} 
            disabled={refreshing}
            size="small"
          >
            <Refresh sx={{ 
              fontSize: 20,
              animation: refreshing ? 'spin 1s linear infinite' : 'none',
              '@keyframes spin': {
                '0%': { transform: 'rotate(0deg)' },
                '100%': { transform: 'rotate(360deg)' }
              }
            }} />
          </IconButton>
        </Tooltip>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {activities.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="body2" color="text.secondary">
            No recent activities found
          </Typography>
        </Box>
      ) : (
        <List sx={{ maxHeight: 400, overflow: 'auto' }}>
          {activities.map((activity, i) => (
            <ListItem 
              key={i}
              sx={{ 
                borderBottom: i < activities.length - 1 ? '1px solid' : 'none',
                borderColor: 'divider',
                py: 1.5
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 1,
                  color: getActivityColor(activity.type, activity.status) + '.main'
                }}>
                  {getActivityIcon(activity.type)}
                  {activity.status && getStatusIcon(activity.status)}
                </Box>
              </ListItemIcon>
              
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                    <Typography variant="body2" sx={{ flex: 1 }}>
                      {activity.message}
                    </Typography>
                    {activity.status && (
                      <Chip
                        label={activity.status}
                        size="small"
                        color={getActivityColor(activity.type, activity.status)}
                        variant="outlined"
                      />
                    )}
                  </Box>
                }
                secondary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      {formatTimestamp(activity.timestamp)}
                    </Typography>
                    {activity.icon && (
                      <Typography variant="caption">
                        {activity.icon}
                      </Typography>
                    )}
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      )}

      {activities.length > 0 && (
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            Showing last {activities.length} activities
          </Typography>
        </Box>
      )}
    </Paper>
  );
}

