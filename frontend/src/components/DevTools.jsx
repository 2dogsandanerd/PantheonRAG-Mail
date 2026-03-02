import React from 'react';
import { Container, Typography, Grid, Box, Alert } from '@mui/material';
import PerformanceMetrics from './statistics/PerformanceMetrics';
import LLMStatistics from './statistics/LLMStatistics';
import RAGStatistics from './statistics/RAGStatistics';

export default function DevTools() {
  return (
    <Container maxWidth="xl">
      <Typography variant="h4" sx={{ mb: 3 }}>
        🛠️ Developer Tools & Diagnostics
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        <strong>Developer Tools:</strong> Diese Sektion zeigt diagnostische Informationen und Echtzeit-Statistiken aus dem Backend.
        Die Daten werden live von den API-Endpoints geladen und spiegeln die tatsächliche Systemnutzung wider.
      </Alert>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <PerformanceMetrics />
        </Grid>

        <Grid item xs={12} md={6}>
          <LLMStatistics />
        </Grid>

        <Grid item xs={12} md={6}>
          <RAGStatistics />
        </Grid>
      </Grid>
    </Container>
  );
}
