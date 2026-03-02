import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Button, Alert, Paper, Grid,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Chip, Container, Tabs, Tab
} from '@mui/material';
import { Sync, CheckCircle, PendingActions, Analytics, Dashboard } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { getLearningPairs, matchSentEmails } from '../api/client';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorDisplay } from './ErrorDisplay';
import EngagementScoreCard from './analytics/EngagementScoreCard';
import MetricsGrid from './analytics/MetricsGrid';
import LearningProgressChart from './analytics/LearningProgressChart';
import ConversationStatsChart from './analytics/ConversationStatsChart';
import RecommendationsWidget from './analytics/RecommendationsWidget';

function Learning() {
  const { t } = useTranslation();
  const [pairs, setPairs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState(0);

  const fetchPairs = async () => {
    try {
      setLoading(true);
      setMessage('');
      const data = await getLearningPairs();
      setPairs(data.pairs || []);
      setError(null);
    } catch (err) {
      setError(err.message);
      setPairs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPairs();
  }, []);

  const handleMatch = async () => {
    setMessage('Matching sent emails...');
    try {
      const response = await matchSentEmails();
      setMessage(`Matching complete. Found ${response.pairs_updated} new pairs.`);
      fetchPairs(); // Refresh the list
    } catch (err) {
      setMessage(`Error during matching: ${err.message}`);
    }
  };

  const getStatusChip = (status) => {
    if (status === 'PAIR_COMPLETED') {
      return <Chip label={t('learning.status.pairCompleted')} color="success" icon={<CheckCircle />} size="small" />;
    }
    return <Chip label={t('learning.status.draftCreated')} color="warning" icon={<PendingActions />} size="small" />;
  };

  if (loading) {
    return <LoadingSpinner message={t('common.loading')} />;
  }

  if (error) {
    return (
      <ErrorDisplay
        error={error}
        title={t('common.error')}
        onRetry={fetchPairs}
      />
    );
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5">
            {t('learning.title')}
          </Typography>
          <Button
            variant="contained"
            startIcon={<Sync />}
            onClick={handleMatch}
            disabled={loading}
          >
            {t('learning.matchSentEmails')}
          </Button>
        </Box>

        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant="fullWidth"
          sx={{ mb: 3 }}
        >
          <Tab icon={<Dashboard />} label="Learning Dashboard" iconPosition="start" />
          <Tab icon={<Analytics />} label="Analytics" iconPosition="start" />
        </Tabs>

        {message && (
          <Alert severity="info" sx={{ mb: 3 }} onClose={() => setMessage('')}>
            {message}
          </Alert>
        )}

        {activeTab === 0 && (
          <>
            {/* Engagement Score and Metrics */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
              <Grid item xs={12} md={4}>
                <EngagementScoreCard />
              </Grid>
              <Grid item xs={12} md={8}>
                <MetricsGrid />
              </Grid>
            </Grid>

            {/* Charts */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
              <Grid item xs={12} md={6}>
                <LearningProgressChart />
              </Grid>
              <Grid item xs={12} md={6}>
                <ConversationStatsChart />
              </Grid>
            </Grid>

            {/* Recommendations */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
              <Grid item xs={12}>
                <RecommendationsWidget />
              </Grid>
            </Grid>
          </>
        )}

        {activeTab === 1 && (
          <TableContainer component={Paper} elevation={2}>
            <Table sx={{ minWidth: 650 }} aria-label="learning pairs table">
              <TableHead>
                <TableRow sx={{ bgcolor: 'primary.main' }}>
                  <TableCell sx={{ color: 'primary.contrastText', fontWeight: 'bold' }}>ID</TableCell>
                  <TableCell sx={{ color: 'primary.contrastText', fontWeight: 'bold' }}>Thread ID</TableCell>
                  <TableCell sx={{ color: 'primary.contrastText', fontWeight: 'bold' }}>Status</TableCell>
                  <TableCell sx={{ color: 'primary.contrastText', fontWeight: 'bold' }}>Created At</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {pairs.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} align="center">
                      <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                        No learning pairs found. Generate drafts to create pairs.
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  pairs.map((pair) => (
                    <TableRow
                      key={pair.id}
                      sx={{
                        '&:nth-of-type(odd)': { bgcolor: 'action.hover' },
                        '&:hover': { bgcolor: 'action.selected' },
                      }}
                    >
                      <TableCell>{pair.id}</TableCell>
                      <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                        {pair.thread_id}
                      </TableCell>
                      <TableCell>{getStatusChip(pair.status)}</TableCell>
                      <TableCell>
                        {new Date(pair.created_at).toLocaleString('de-DE', {
                          year: 'numeric',
                          month: '2-digit',
                          day: '2-digit',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Box>
    </Container>
  );
}

export default Learning;
