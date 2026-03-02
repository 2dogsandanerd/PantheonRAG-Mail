import React, { useEffect, useState } from 'react';
import { Paper, Typography, List, ListItem, ListItemText, ListItemIcon, Box, Chip, CircularProgress, Alert } from '@mui/material';
import { Email, Edit, School, Storage, CheckCircle, Error, Warning } from '@mui/icons-material';
import { getRecentActivities } from '../../api/client';

const getActivityIcon = (activity) => {
  switch (activity.type) {
    case 'email_received': return <Email />;
    case 'draft_created': return <Edit />;
    case 'learning_match': return <School />;
    case 'rag_query': return <Storage />;
    case 'warning': return <Warning />;
    default: return <Email />;
  }
};

const getActivityColor = (activity) => {
  switch (activity.severity) {
    case 'success': return 'success.main';
    case 'warning': return 'warning.main';
    case 'error': return 'error.main';
    default: return 'info.main';
  }
};

const getActivityEmoji = (activity) => {
  switch (activity.type) {
    case 'email_received': return '📧';
    case 'draft_created': return '✍️';
    case 'learning_match': return '📚';
    case 'rag_query': return '🧠';
    case 'warning': return '⚠️';
    case 'error': return '❌';
    default: return '📋';
  }
};

export default function ActivityFeed() {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchActivities = async () => {
      try {
        setLoading(true);
        const response = await getRecentActivities(10);
        setActivities(response.activities || []);
        setError(null);
      } catch (error) {
        console.error('Failed to fetch activities:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchActivities();
    // ❌ POLLING REMOVED - Phase 2/3: Event-based updates via WebSocket
    // const interval = setInterval(fetchActivities, 30000);
    // return () => clearInterval(interval);
  }, []);

  if (loading && activities.length === 0) {
    return (
      <Paper sx={{ p: 2, background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)', border: '1px solid #444' }}>
        <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
          📋 Recent Activity
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 4 }}>
          <CircularProgress size={32} />
          <Typography sx={{ ml: 2 }} color="text.secondary">Loading activities...</Typography>
        </Box>
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper sx={{ p: 2, background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)', border: '1px solid #444' }}>
        <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
          📋 Recent Activity
        </Typography>
        <Alert severity="error" sx={{ mt: 2 }}>
          Failed to load activities: {error}
        </Alert>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2, background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)', border: '1px solid #444' }}>
      <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
        📋 Recent Activity
      </Typography>

      {activities.length === 0 ? (
        <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 4 }}>
          No recent activities. Create some drafts to see activity here.
        </Typography>
      ) : (
        <List>
          {activities.map((activity, index) => (
          <ListItem
            key={index} 
            sx={{ 
              mb: 1, 
              p: 1.5, 
              background: 'rgba(255, 255, 255, 0.02)',
              borderRadius: 1,
              border: '1px solid rgba(255, 255, 255, 0.05)'
            }}
          >
            <ListItemIcon sx={{ minWidth: 40, color: getActivityColor(activity) }}>
              {getActivityIcon(activity)}
            </ListItemIcon>
            <ListItemText
              primary={
                <Typography variant="body2" sx={{ fontWeight: 500 }}>
                  {activity.message}
                </Typography>
              }
              secondary={
                <span style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
                  <Chip
                    label={getActivityEmoji(activity)}
                    size="small"
                    sx={{
                      height: 20,
                      width: 20,
                      fontSize: 10,
                      minWidth: 20,
                      p: 0,
                      '& .MuiChip-label': {
                        px: 0.5
                      }
                    }}
                  />
                  <Typography variant="caption" color="text.secondary" component="span">
                    {new Date(activity.timestamp).toLocaleString('de-DE', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </Typography>
                </span>
              }
              secondaryTypographyProps={{ component: 'div' }}
            />
          </ListItem>
          ))}
        </List>
      )}
    </Paper>
  );
}