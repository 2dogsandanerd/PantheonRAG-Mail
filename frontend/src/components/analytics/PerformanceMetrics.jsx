import React, { useEffect, useState } from 'react';
import { 
  Card, CardContent, Typography, Box, Grid, Chip, 
  CircularProgress, Alert, LinearProgress 
} from '@mui/material';
import { 
  Speed, Psychology, Storage, Email, 
  TrendingUp, TrendingDown, TrendingFlat 
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { getPerformanceMetrics } from '../../api/client';

const getTrendIcon = (value, threshold) => {
  if (value < threshold * 0.8) return <TrendingDown color="success" />;
  if (value > threshold * 1.2) return <TrendingUp color="warning" />;
  return <TrendingFlat color="info" />;
};

const getPerformanceColor = (value, threshold) => {
  if (value < threshold * 0.8) return 'success';
  if (value > threshold * 1.2) return 'warning';
  return 'info';
};

const formatTime = (seconds) => {
  if (seconds < 1) {
    return `${Math.round(seconds * 1000)}ms`;
  }
  return `${seconds.toFixed(1)}s`;
};

const MetricCard = ({ title, icon, value, min, max, threshold, unit = 's' }) => {
  const color = getPerformanceColor(value, threshold);
  const trendIcon = getTrendIcon(value, threshold);
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <Box sx={{ color: `${color}.main` }}>
            {icon}
          </Box>
          <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
            {title}
          </Typography>
          {trendIcon}
        </Box>

        <Typography variant="h4" sx={{ color: `${color}.main`, fontWeight: 'bold', mb: 1 }}>
          {formatTime(value)}
        </Typography>

        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="caption" color="text.secondary">
              Min: {formatTime(min)}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Max: {formatTime(max)}
            </Typography>
          </Box>
          
          <LinearProgress
            variant="determinate"
            value={Math.min((value / max) * 100, 100)}
            sx={{
              height: 6,
              borderRadius: 3,
              backgroundColor: 'grey.200',
              '& .MuiLinearProgress-bar': {
                backgroundColor: `${color}.main`,
                borderRadius: 3
              }
            }}
          />
        </Box>

        <Chip
          label={`Target: ${formatTime(threshold)}`}
          size="small"
          color={color}
          variant="outlined"
        />
      </CardContent>
    </Card>
  );
};

export default function PerformanceMetrics() {
  const { t } = useTranslation();
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setError(null);
        const data = await getPerformanceMetrics();
        setMetrics(data);
      } catch (err) {
        setError(`Failed to load performance metrics: ${err.message}`);
        console.error('Error loading performance metrics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Alert severity="error">
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!metrics) return null;

  const performanceData = [
    {
      title: 'RAG Query Time',
      icon: <Storage />,
      value: metrics.rag_query_time?.avg || 0,
      min: metrics.rag_query_time?.min || 0,
      max: metrics.rag_query_time?.max || 0,
      threshold: 1.0
    },
    {
      title: 'LLM Response Time',
      icon: <Psychology />,
      value: metrics.llm_response_time?.avg || 0,
      min: metrics.llm_response_time?.min || 0,
      max: metrics.llm_response_time?.max || 0,
      threshold: 3.0
    },
    {
      title: 'Email Fetch Time',
      icon: <Email />,
      value: metrics.email_fetch_time?.avg || 0,
      min: metrics.email_fetch_time?.min || 0,
      max: metrics.email_fetch_time?.max || 0,
      threshold: 1.5
    },
    {
      title: 'End-to-End Time',
      icon: <Speed />,
      value: metrics.end_to_end_time?.avg || 0,
      min: metrics.end_to_end_time?.min || 0,
      max: metrics.end_to_end_time?.max || 0,
      threshold: 5.0
    }
  ];

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          ⚡ Performance Metrics
        </Typography>

        <Grid container spacing={2}>
          {performanceData.map((metric, index) => (
            <Grid item xs={12} sm={6} key={index}>
              <MetricCard {...metric} />
            </Grid>
          ))}
        </Grid>

        {/* Summary */}
        <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="subtitle2" gutterBottom>
            Performance Summary
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Average end-to-end processing time: {formatTime(metrics.end_to_end_time?.avg || 0)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Fastest operation: RAG Query ({formatTime(metrics.rag_query_time?.min || 0)})
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Slowest operation: LLM Response ({formatTime(metrics.llm_response_time?.max || 0)})
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}

