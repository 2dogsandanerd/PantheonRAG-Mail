import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Grid, Box, Chip, CircularProgress } from '@mui/material';
import { Speed, Timer, Memory, Storage } from '@mui/icons-material';
import { getPerformanceMetrics } from '../../api/client';

export default function PerformanceMetrics() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const data = await getPerformanceMetrics();
        setMetrics(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch performance metrics:', err);
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <Card sx={{
        background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)',
        border: '1px solid #444',
        minHeight: 200,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <CircularProgress color="primary" />
      </Card>
    );
  }

  if (error || !metrics) {
    return (
      <Card sx={{
        background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)',
        border: '1px solid #444'
      }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            ⚡ Performance Metrics
          </Typography>
          <Typography color="error">
            Keine Daten verfügbar
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Performance-Metriken werden automatisch während des Betriebs erfasst.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  // Prüfen ob echte Daten vorhanden sind (nicht nur Default-Werte)
  const hasRealData = metrics.rag_query_time?.avg !== 0.5 || metrics.llm_response_time?.avg !== 2.3;

  const metricCards = [
    {
      title: 'RAG Query Time',
      icon: <Speed />,
      values: [
        { label: 'Avg', value: `${(metrics.rag_query_time?.avg || 0)}s`, color: 'info.main' },
        { label: 'Min', value: `${(metrics.rag_query_time?.min || 0)}s`, color: 'success.main' },
        { label: 'Max', value: `${(metrics.rag_query_time?.max || 0)}s`, color: 'warning.main' }
      ],
      color: 'info.main'
    },
    {
      title: 'LLM Response Time',
      icon: <Timer />,
      values: [
        { label: 'Avg', value: `${(metrics.llm_response_time?.avg || 0)}s`, color: 'info.main' },
        { label: 'Min', value: `${(metrics.llm_response_time?.min || 0)}s`, color: 'success.main' },
        { label: 'Max', value: `${(metrics.llm_response_time?.max || 0)}s`, color: 'warning.main' }
      ],
      color: 'primary.main'
    },
    {
      title: 'Email Fetch Time',
      icon: <Memory />,
      values: [
        { label: 'Avg', value: `${(metrics.email_fetch_time?.avg || 0)}s`, color: 'info.main' },
        { label: 'Min', value: `${(metrics.email_fetch_time?.min || 0)}s`, color: 'success.main' },
        { label: 'Max', value: `${(metrics.email_fetch_time?.max || 0)}s`, color: 'warning.main' }
      ],
      color: 'secondary.main'
    },
    {
      title: 'End-to-End Time',
      icon: <Storage />,
      values: [
        { label: 'Avg', value: `${(metrics.end_to_end_time?.avg || 0)}s`, color: 'info.main' },
        { label: 'Min', value: `${(metrics.end_to_end_time?.min || 0)}s`, color: 'success.main' },
        { label: 'Max', value: `${(metrics.end_to_end_time?.max || 0)}s`, color: 'warning.main' }
      ],
      color: 'success.main'
    }
  ];

  return (
    <Card sx={{
      background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)',
      border: '1px solid #444'
    }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          ⚡ Performance Metrics
        </Typography>

        {!hasRealData && (
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
            ℹ️ Noch keine Performance-Daten erfasst. Metriken werden automatisch bei Systemnutzung aktualisiert.
          </Typography>
        )}

        <Grid container spacing={2}>
          {metricCards.map((metric, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card sx={{
                height: '100%',
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid rgba(255, 255, 255, 0.05)'
              }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <Box sx={{ color: metric.color }}>
                      {metric.icon}
                    </Box>
                    <Typography variant="subtitle2" color="text.secondary">
                      {metric.title}
                    </Typography>
                  </Box>

                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {metric.values.map((value, i) => (
                      <Box key={i} sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="caption" color="text.secondary">
                          {value.label}:
                        </Typography>
                        <Chip
                          label={value.value}
                          size="small"
                          sx={{
                            height: 20,
                            bgcolor: `${value.color}15`,
                            color: value.color,
                            fontWeight: 'bold'
                          }}
                        />
                      </Box>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </CardContent>
    </Card>
  );
}
