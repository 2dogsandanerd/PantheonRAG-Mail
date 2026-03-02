import React from 'react';
import { Container, Typography, Grid, Box } from '@mui/material';
import EmailStatsChart from './statistics/EmailStatsChart';

export default function Statistics() {
  return (
    <Container maxWidth="xl">
      <Typography variant="h4" sx={{ mb: 3 }}>
        📊 Email Statistics & Analytics
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <EmailStatsChart />
        </Grid>
      </Grid>
    </Container>
  );
}