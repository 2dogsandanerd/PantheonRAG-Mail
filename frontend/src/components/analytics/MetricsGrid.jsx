import React, { useState, useEffect } from 'react';
import { Grid, Card, CardContent, Typography, Box, CircularProgress } from '@mui/material';
import { Message, Timer, CheckCircle, TrendingUp } from '@mui/icons-material';
import { getEngagementScore } from '../../api/client';

export default function MetricsGrid() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const response = await getEngagementScore();
        setData(response);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch engagement score:', err);
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <Grid container spacing={2}>
        {[1, 2, 3, 4].map((i) => (
          <Grid item xs={12} sm={6} md={3} key={i}>
            <Card sx={{
              background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)',
              border: '1px solid #444',
              minHeight: 120,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <CircularProgress size={24} color="primary" />
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  }

  if (error || !data) {
    return (
      <Card sx={{
        background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)',
        border: '1px solid #444'
      }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            📊 Analytics Metrics
          </Typography>
          <Typography color="error">
            Keine Daten verfügbar
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Analytics-Daten werden automatisch während der Systemnutzung erfasst.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const metrics = data.metrics || {};
  const hasData = metrics.total_conversations > 0 || metrics.reply_rate > 0;

  const metricCards = [
    {
      icon: <Message />,
      label: 'Total Conversations',
      value: (metrics.total_conversations || 0).toLocaleString(),
      color: 'primary.main'
    },
    {
      icon: <Timer />,
      label: 'Avg Response Time',
      value: `${(metrics.avg_response_time || 0)}h`,
      color: 'info.main'
    },
    {
      icon: <CheckCircle />,
      label: 'Reply Rate',
      value: `${(metrics.reply_rate || 0).toFixed(1)}%`,
      color: 'success.main'
    },
    {
      icon: <TrendingUp />,
      label: 'Avg Conversation Length',
      value: (metrics.avg_conversation_length || 0).toFixed(1),
      color: 'warning.main'
    }
  ];

  return (
    <Grid container spacing={2}>
      {metricCards.map((metric, i) => (
        <Grid item xs={12} sm={6} md={3} key={i}>
          <Card sx={{
            background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)',
            border: '1px solid #444'
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Box sx={{ color: metric.color }}>
                  {metric.icon}
                </Box>
                <Typography variant="caption" color="text.secondary">
                  {metric.label}
                </Typography>
              </Box>
              <Typography variant="h4" sx={{ color: metric.color }}>
                {metric.value}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      ))}
      {!hasData && (
        <Grid item xs={12}>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
            ℹ️ Noch keine Conversations erfasst. Metriken werden automatisch bei Systemnutzung aktualisiert.
          </Typography>
        </Grid>
      )}
    </Grid>
  );
}
