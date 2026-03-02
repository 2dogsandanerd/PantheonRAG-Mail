import React, { useState } from 'react';
import { 
  Container, Typography, Grid, Box, Tabs, Tab, 
  Button, Stack, Alert, CircularProgress 
} from '@mui/material';
import { 
  Download, FileDownload, Assessment, 
  TrendingUp, Psychology, Storage 
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import EmailStatsChart from './statistics/EmailStatsChart';
import PerformanceMetrics from './statistics/PerformanceMetrics';
import LLMStatistics from './statistics/LLMStatistics';
import RAGStatistics from './statistics/RAGStatistics';
import { exportStatisticsCSV, exportStatisticsJSON } from '../api/client';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`stats-tabpanel-${index}`}
      aria-labelledby={`stats-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export default function Statistics() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState(0);
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState(null);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleExportCSV = async () => {
    try {
      setExporting(true);
      setExportError(null);
      
      const data = await exportStatisticsCSV();
      
      // Create and download file
      const blob = new Blob([data.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = data.filename || 'statistics_export.csv';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setExportError(`Failed to export CSV: ${error.message}`);
    } finally {
      setExporting(false);
    }
  };

  const handleExportJSON = async () => {
    try {
      setExporting(true);
      setExportError(null);
      
      const data = await exportStatisticsJSON();
      
      // Create and download file
      const blob = new Blob([data.data], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = data.filename || 'statistics_export.json';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setExportError(`Failed to export JSON: ${error.message}`);
    } finally {
      setExporting(false);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 1 }}>
          📊 Statistics & Analytics
        </Typography>
        
        <Stack direction="row" spacing={2}>
          <Button
            variant="outlined"
            startIcon={exporting ? <CircularProgress size={20} /> : <FileDownload />}
            onClick={handleExportCSV}
            disabled={exporting}
          >
            Export CSV
          </Button>
          <Button
            variant="outlined"
            startIcon={exporting ? <CircularProgress size={20} /> : <Download />}
            onClick={handleExportJSON}
            disabled={exporting}
          >
            Export JSON
          </Button>
        </Stack>
      </Box>

      {exportError && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setExportError(null)}>
          {exportError}
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange} 
          aria-label="statistics tabs"
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab 
            icon={<Assessment />} 
            label="Email Analytics" 
            iconPosition="start" 
          />
          <Tab 
            icon={<TrendingUp />} 
            label="Performance" 
            iconPosition="start" 
          />
          <Tab 
            icon={<Psychology />} 
            label="LLM Usage" 
            iconPosition="start" 
          />
          <Tab 
            icon={<Storage />} 
            label="RAG System" 
            iconPosition="start" 
          />
        </Tabs>
      </Box>

      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <EmailStatsChart />
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <PerformanceMetrics />
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <LLMStatistics />
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <RAGStatistics />
          </Grid>
        </Grid>
      </TabPanel>
    </Container>
  );
}

