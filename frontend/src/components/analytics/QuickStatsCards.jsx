import React, { useEffect, useState } from 'react';
import { Grid, Card, CardContent, Typography, Box, CircularProgress } from '@mui/material';
import { Email, Edit, School, Storage, TrendingUp, Schedule } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { getDashboardStatistics } from '../../api/client';

const getStatIcon = (type) => {
  switch (type) {
    case 'emails': return <Email />;
    case 'drafts': return <Edit />;
    case 'learning': return <School />;
    case 'rag': return <Storage />;
    case 'uptime': return <Schedule />;
    default: return <TrendingUp />;
  }
};

const getStatColor = (type) => {
  switch (type) {
    case 'emails': return 'primary.main';
    case 'drafts': return 'warning.main';
    case 'learning': return 'success.main';
    case 'rag': return 'info.main';
    case 'uptime': return 'secondary.main';
    default: return 'text.primary';
  }
};

export default function QuickStatsCards() {
  const { t } = useTranslation();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = async () => {
    try {
      setError(null);
      const data = await getDashboardStatistics();
      setStats(data);
    } catch (err) {
      setError(`Failed to load dashboard stats: ${err.message}`);
      console.error('Error loading dashboard stats:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();

    // ❌ POLLING REMOVED - Phase 2/3: Event-based updates via WebSocket
    // const interval = setInterval(fetchStats, 30000);
    // return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography color="error" variant="body2">
          {error}
        </Typography>
      </Box>
    );
  }

  if (!stats) return null;

  const cards = [
    { 
      type: 'emails',
      icon: <Email />, 
      label: t('dashboard.stats.unreadEmails', 'Unread Emails'), 
      value: stats.unread_emails || 0, 
      color: 'primary.main' 
    },
    { 
      type: 'drafts',
      icon: <Edit />, 
      label: t('dashboard.stats.pendingDrafts', 'Pending Drafts'), 
      value: stats.pending_drafts || 0, 
      color: 'warning.main' 
    },
    { 
      type: 'learning',
      icon: <School />, 
      label: t('dashboard.stats.learningPairs', 'Learning Pairs'), 
      value: stats.learning_pairs || 0, 
      color: 'success.main' 
    },
    { 
      type: 'rag',
      icon: <Storage />, 
      label: t('dashboard.stats.ragDocuments', 'RAG Documents'), 
      value: stats.rag_documents || 0, 
      color: 'info.main' 
    }
  ];

  return (
    <Grid container spacing={2}>
      {cards.map((card, i) => (
        <Grid item xs={12} sm={6} md={3} key={i}>
          <Card 
            sx={{ 
              height: '100%',
              '&:hover': {
                boxShadow: 3,
                transform: 'translateY(-2px)',
                transition: 'all 0.2s ease-in-out'
              }
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Box sx={{ color: card.color }}>
                  {card.icon}
                </Box>
                <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 'medium' }}>
                  {card.label}
                </Typography>
              </Box>
              
              <Typography 
                variant="h3" 
                sx={{ 
                  color: card.color,
                  fontWeight: 'bold',
                  lineHeight: 1
                }}
              >
                {card.value.toLocaleString()}
              </Typography>

              {/* Additional info for specific stats */}
              {card.type === 'emails' && card.value > 0 && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  {card.value === 1 ? '1 unread email' : `${card.value} unread emails`}
                </Typography>
              )}
              
              {card.type === 'drafts' && card.value > 0 && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  {card.value === 1 ? '1 draft pending' : `${card.value} drafts pending`}
                </Typography>
              )}

              {card.type === 'learning' && card.value > 0 && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  {card.value === 1 ? '1 learning pair' : `${card.value} learning pairs`}
                </Typography>
              )}

              {card.type === 'rag' && card.value > 0 && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  {card.value === 1 ? '1 document indexed' : `${card.value} documents indexed`}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}

