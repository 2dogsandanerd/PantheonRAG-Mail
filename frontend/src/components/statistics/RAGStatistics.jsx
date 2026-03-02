import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Grid, Box, Chip, CircularProgress } from '@mui/material';
import { Storage, Search, Memory, Folder } from '@mui/icons-material';
import { getRAGStatistics } from '../../api/client';

export default function RAGStatistics() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const data = await getRAGStatistics();
        setStats(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch RAG statistics:', err);
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
            🧠 RAG Statistics
          </Typography>
          <Typography color="error">
            Keine Daten verfügbar
          </Typography>
          <Typography variant="caption" color="text.secondary">
            RAG-Statistiken werden automatisch erfasst, sobald Dokumentenabfragen stattfinden.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  // Prüfen ob echte Daten vorhanden sind
  const hasData = stats.total_documents > 0 || Object.keys(stats.collection_sizes || {}).length > 0;

  const statCards = [
    {
      title: 'Total Queries',
      value: (stats.total_queries || 0).toLocaleString(),
      icon: <Search />,
      color: 'primary.main'
    },
    {
      title: 'Avg Chunks Used',
      value: (stats.avg_chunks_used || 0).toFixed(1),
      icon: <Folder />,
      color: 'info.main'
    },
    {
      title: 'Cache Hit Rate',
      value: `${(stats.cache_hit_rate || 0).toFixed(1)}%`,
      icon: <Memory />,
      color: 'success.main'
    }
  ];

  const collections = stats.collection_sizes 
    ? Object.entries(stats.collection_sizes)
        .filter(([_, size]) => size > 0)
        .map(([name, size]) => {
          const total = Object.values(stats.collection_sizes).reduce((a, b) => a + b, 0);
          return {
            name,
            size,
            percentage: total > 0 ? ((size / total) * 100).toFixed(1) : 0
          };
        })
    : [];

  return (
    <Card sx={{
      background: 'linear-gradient(145deg, #2A2A2A, #1A1A1A)',
      border: '1px solid #444'
    }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          🧠 RAG Statistics
        </Typography>

        {!hasData && (
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
            ℹ️ Noch keine RAG-Dokumente indexiert. Statistiken werden automatisch bei Nutzung aktualisiert.
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
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {collections.length > 0 && (
          <Card sx={{
            background: 'rgba(255, 255, 255, 0.02)',
            border: '1px solid rgba(255, 255, 255, 0.05)'
          }}>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Storage /> Collections
              </Typography>

              <Grid container spacing={2}>
                {collections.map((collection, index) => (
                  <Grid item xs={12} sm={6} key={index}>
                    <Box sx={{
                      p: 2,
                      background: 'rgba(255, 255, 255, 0.03)',
                      borderRadius: 1,
                      border: '1px solid rgba(255, 255, 255, 0.05)'
                    }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="subtitle2">
                          {collection.name}
                        </Typography>
                        <Chip
                          label={`${collection.size} docs`}
                          size="small"
                          color="primary"
                          sx={{ height: 20 }}
                        />
                      </Box>

                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box sx={{
                          flex: 1,
                          height: 8,
                          background: 'rgba(255, 255, 255, 0.1)',
                          borderRadius: 4,
                          overflow: 'hidden'
                        }}>
                          <Box
                            sx={{
                              width: `${collection.percentage}%`,
                              height: '100%',
                              background: 'linear-gradient(90deg, #42a5f5, #2196f3)',
                              borderRadius: 4
                            }}
                          />
                        </Box>
                        <Typography variant="caption" color="text.secondary">
                          {collection.percentage}%
                        </Typography>
                      </Box>
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
