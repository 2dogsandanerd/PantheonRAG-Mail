import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Grid, Box, Chip, CircularProgress } from '@mui/material';
import { SmartToy, Token, MonetizationOn, PieChart } from '@mui/icons-material';
import { getLLMStatistics } from '../../api/client';

export default function LLMStatistics() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const data = await getLLMStatistics();
        setStats(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch LLM statistics:', err);
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <Card sx={{
        background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)',
        border: '1px solid #444',
        minHeight: 300,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <CircularProgress color="primary" />
      </Card>
    );
  }

  if (error || !stats) {
    return (
      <Card sx={{
        background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)',
        border: '1px solid #444'
      }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🤖 LLM Statistics
          </Typography>
          <Typography color="error">
            Keine Daten verfügbar
          </Typography>
          <Typography variant="caption" color="text.secondary">
            LLM-Statistiken werden automatisch erfasst, sobald API-Aufrufe stattfinden.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  // Prüfen ob echte Daten vorhanden sind
  const hasData = stats.total_calls > 0 || stats.total_tokens?.input > 0;

  const statCards = [
    {
      title: 'Total LLM Calls',
      value: stats.total_calls?.toLocaleString() || '0',
      icon: <SmartToy />,
      color: 'primary.main'
    },
    {
      title: 'Tokens Used',
      value: `${((stats.total_tokens?.input || 0) + (stats.total_tokens?.output || 0)).toLocaleString()}`,
      subtitle: `${(stats.total_tokens?.input || 0).toLocaleString()} in / ${(stats.total_tokens?.output || 0).toLocaleString()} out`,
      icon: <Token />,
      color: 'info.main'
    },
    {
      title: 'Estimated Cost',
      value: `${(stats.estimated_cost || 0).toFixed(2)}`,
      icon: <MonetizationOn />,
      color: 'success.main'
    }
  ];

  const modelDistribution = stats.model_distribution 
    ? Object.entries(stats.model_distribution)
        .filter(([_, percentage]) => percentage > 0)
        .map(([model, percentage]) => ({
          model,
          percentage,
          color: getModelColor(model)
        }))
    : [];

  function getModelColor(model) {
    switch (model) {
      case 'llama3': return '#9C27B0';
      case 'gemini-flash': return '#4CAF50';
      case 'gpt-4': return '#2196F3';
      default: return '#9E9E9E';
    }
  }

  return (
    <Card sx={{
      background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)',
      border: '1px solid #444'
    }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          🤖 LLM Statistics
        </Typography>

        {!hasData && (
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
            ℹ️ Noch keine LLM-Aufrufe erfasst. Statistiken werden automatisch bei API-Nutzung aktualisiert.
          </Typography>
        )}

        <Grid container spacing={2} sx={{ mb: 3 }}>
          {statCards.map((stat, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card sx={{
                height: '100%',
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid rgba(255, 255, 255, 0.05)'
              }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Box sx={{ color: stat.color }}>
                      {stat.icon}
                    </Box>
                    <Typography variant="subtitle2" color="text.secondary">
                      {stat.title}
                    </Typography>
                  </Box>

                  <Typography variant="h4" sx={{ color: stat.color, mb: 1 }}>
                    {stat.value}
                  </Typography>

                  {stat.subtitle && (
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                      {stat.subtitle}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {modelDistribution.length > 0 && (
          <Card sx={{
            background: 'rgba(255, 255, 255, 0.02)',
            border: '1px solid rgba(255, 255, 255, 0.05)'
          }}>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <PieChart /> Model Distribution
              </Typography>

              <Grid container spacing={2}>
                {modelDistribution.map((model, index) => (
                  <Grid item xs={12} sm={4} key={index}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Box sx={{
                        width: 80,
                        height: 80,
                        borderRadius: '50%',
                        background: `conic-gradient(${model.color} 0% ${model.percentage}%, #444 ${model.percentage}% 100%)`,
                        margin: '0 auto 16px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#E0E0E0',
                        fontWeight: 'bold'
                      }}>
                        {model.percentage}%
                      </Box>
                      <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                        {model.model}
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        )}
      </CardContent>
    </Card>
  );
}
