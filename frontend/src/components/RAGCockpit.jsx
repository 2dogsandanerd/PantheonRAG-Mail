import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  CircularProgress,
  Paper,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Slider,
  FormControlLabel,
  Checkbox,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  Chip,
  OutlinedInput,
  ListItemText,
  ListItemIcon,
  Tabs,
  Tab,
  Switch,
  Divider,
  Alert
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SettingsIcon from '@mui/icons-material/Settings';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import MonitorHeartIcon from '@mui/icons-material/MonitorHeart';
import { queryCockpit, getRAGCollections, getOllamaModels, getSystemConfig, updateSystemConfig } from '../api/rag';

const RAGCockpit = () => {
  const [tabValue, setTabValue] = useState(0);

  // Playground State
  const [query, setQuery] = useState('What is the capital of France?');
  const [collections, setCollections] = useState([]);
  const [availableCollections, setAvailableCollections] = useState([]);
  const [ollamaModels, setOllamaModels] = useState([]);
  const [selectedCollections, setSelectedCollections] = useState([]);
  const [k, setK] = useState(10);
  const [temperature, setTemperature] = useState(0.1);
  const [llmModel, setLlmModel] = useState('llama3:latest');
  const [systemPrompt, setSystemPrompt] = useState('You are a helpful assistant. Answer the user\'s query based on the provided context.');
  const [useReranker, setUseReranker] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Config State
  const [config, setConfig] = useState(null);
  const [configLoading, setConfigLoading] = useState(false);

  // Load initial data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [colsRes, modelsRes, configRes] = await Promise.all([
          getRAGCollections(),
          getOllamaModels(),
          getSystemConfig()
        ]);

        if (colsRes.collections) {
          setAvailableCollections(colsRes.collections.map(col => col.name));
          setSelectedCollections(colsRes.collections.slice(0, 2).map(col => col.name));
        }

        if (modelsRes.models) {
          setOllamaModels(modelsRes.models.map(model => model.name || model.model));
        }

        setConfig(configRes);

        // Initialize playground defaults from config
        if (configRes) {
          // Access temperature from the flat .env structure
          setTemperature(configRes.TEMPERATURE || 0.1);
          setK(configRes.RERANK_TOP_K || 10); // Use rerank top k as default K
          setUseReranker(configRes.USE_RERANKER === 'true' || configRes.USE_RERANKER === true);
        }

      } catch (err) {
        console.error('Error loading initial data:', err);
        setError('Failed to load system data: ' + err.message);
      }
    };
    fetchData();
  }, []);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleQuery = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await queryCockpit(
        query,
        selectedCollections,
        k,
        llmModel,
        temperature,
        systemPrompt,
        useReranker
      );
      setResult(response);
    } catch (err) {
      setError(err.message || 'An unknown error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const handleConfigUpdate = async (key, value, section) => {
    try {
      setConfigLoading(true);
      await updateSystemConfig(key, value);
      // Optimistic update
      setConfig(prev => ({
        ...prev,
        [section]: {
          ...prev[section],
          [key.split('.').pop().toLowerCase()]: value // This is a simplification, key mapping might be needed
        }
      }));
      // Reload full config to be safe
      const newConfig = await getSystemConfig();
      setConfig(newConfig);
    } catch (err) {
      setError("Failed to update config: " + err.message);
    } finally {
      setConfigLoading(false);
    }
  };

  const handleCollectionChange = (event) => {
    const value = event.target.value;
    setSelectedCollections(typeof value === 'string' ? value.split(',') : value);
  };

  const renderPlayground = () => (
    <Grid container spacing={2}>
      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 2, height: '100%' }}>
          <Typography variant="h6" gutterBottom>Settings</Typography>

          <FormControl fullWidth margin="normal">
            <InputLabel>Collections</InputLabel>
            <Select
              multiple
              value={selectedCollections}
              onChange={handleCollectionChange}
              input={<OutlinedInput label="Collections" />}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => <Chip key={value} label={value} size="small" />)}
                </Box>
              )}
            >
              {availableCollections.map((col) => (
                <MenuItem key={col} value={col}>{col}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth margin="normal">
            <InputLabel>Model</InputLabel>
            <Select value={llmModel} label="Model" onChange={(e) => setLlmModel(e.target.value)}>
              {ollamaModels.map((m) => <MenuItem key={m} value={m}>{m}</MenuItem>)}
            </Select>
          </FormControl>

          <Typography gutterBottom sx={{ mt: 2 }}>Temperature: {temperature}</Typography>
          <Slider
            value={temperature}
            onChange={(e, v) => setTemperature(v)}
            min={0} max={2} step={0.1}
            valueLabelDisplay="auto"
          />

          <Typography gutterBottom sx={{ mt: 2 }}>Top-K: {k}</Typography>
          <Slider
            value={k}
            onChange={(e, v) => setK(v)}
            min={1} max={20} step={1}
            valueLabelDisplay="auto"
          />

          <FormControlLabel
            control={<Switch checked={useReranker} onChange={(e) => setUseReranker(e.target.checked)} />}
            label="Use Reranker"
            sx={{ mt: 2 }}
          />

          <TextField
            fullWidth
            label="System Prompt"
            multiline
            rows={4}
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            margin="normal"
            size="small"
          />
        </Paper>
      </Grid>

      <Grid item xs={12} md={8}>
        <Paper sx={{ p: 2, mb: 2 }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              label="Enter your query..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
            />
            <Button
              variant="contained"
              onClick={handleQuery}
              disabled={loading}
              startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <PlayArrowIcon />}
            >
              Run
            </Button>
          </Box>
        </Paper>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        {result && (
          <Box>
            <Paper sx={{ p: 2, mb: 2, bgcolor: '#f5f5f5' }}>
              <Typography variant="subtitle2" color="textSecondary">LLM Response</Typography>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>{result.response}</Typography>

              {result.metadata?.verification && (
                <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Chip
                    label={result.metadata.verification.is_supported ? "Verified" : "Unverified"}
                    color={result.metadata.verification.is_supported ? "success" : "warning"}
                    size="small"
                  />
                  <Typography variant="caption">{result.metadata.verification.reasoning}</Typography>
                </Box>
              )}
            </Paper>

            <Typography variant="h6" gutterBottom>Retrieved Context</Typography>
            {result.context.map((chunk, i) => (
              <Accordion key={i} disableGutters elevation={1} sx={{ mb: 1 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%', mr: 2 }}>
                    <Typography variant="subtitle2">{chunk.source_collection}</Typography>
                    <Typography variant="caption">Score: {chunk.relevance_score?.toFixed(3)}</Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2" color="textSecondary" gutterBottom>Source: {chunk.metadata?.source}</Typography>
                  <Typography variant="body2">{chunk.content}</Typography>
                </AccordionDetails>
              </Accordion>
            ))}

            <Accordion sx={{ mt: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>Debug Metadata</AccordionSummary>
              <AccordionDetails>
                <pre style={{ fontSize: '0.75rem', overflow: 'auto' }}>
                  {JSON.stringify(result.metadata, null, 2)}
                </pre>
              </AccordionDetails>
            </Accordion>
          </Box>
        )}
      </Grid>
    </Grid>
  );

  const renderConfig = () => {
    if (!config) return <CircularProgress />;

    return (
      <Grid container spacing={3}>
        {/* Retrieval Settings */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Retrieval Engine</Typography>
            <Divider sx={{ mb: 2 }} />

            <Typography gutterBottom>Hybrid Search Alpha (Keyword vs Vector)</Typography>
            <Slider
              value={config.retrieval.hybrid_search_alpha}
              onChangeCommitted={(e, v) => handleConfigUpdate('HYBRID_SEARCH_ALPHA', v, 'retrieval')}
              min={0} max={1} step={0.1}
              marks={[{ value: 0, label: 'Keyword' }, { value: 1, label: 'Vector' }]}
              valueLabelDisplay="auto"
            />

            <Box sx={{ mt: 3 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={config.retrieval.use_reranker}
                    onChange={(e) => handleConfigUpdate('USE_RERANKER', e.target.checked, 'retrieval')}
                  />
                }
                label="Enable Re-Ranker (Cross-Encoder)"
              />
            </Box>

            <Typography gutterBottom sx={{ mt: 2 }}>Rerank Top-K</Typography>
            <Slider
              value={config.retrieval.rerank_top_k}
              onChangeCommitted={(e, v) => handleConfigUpdate('RERANK_TOP_K', v, 'retrieval')}
              min={1} max={20} step={1}
              valueLabelDisplay="auto"
            />
          </Paper>
        </Grid>

        {/* Intelligence Settings */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Intelligence Layer</Typography>
            <Divider sx={{ mb: 2 }} />

            <FormControlLabel
              control={
                <Switch
                  checked={config.intelligence.enable_query_expansion}
                  onChange={(e) => handleConfigUpdate('ENABLE_QUERY_EXPANSION', e.target.checked, 'intelligence')}
                />
              }
              label="Query Expansion (Synonyms)"
            />
            <Typography variant="caption" display="block" color="textSecondary">
              Generates multiple search queries to improve recall.
            </Typography>

            <Box sx={{ mt: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={config.intelligence.enable_self_correction}
                    onChange={(e) => handleConfigUpdate('ENABLE_SELF_CORRECTION', e.target.checked, 'intelligence')}
                  />
                }
                label="Self-Correction (Hallucination Check)"
              />
              <Typography variant="caption" display="block" color="textSecondary">
                Verifies if the answer is supported by context.
              </Typography>
            </Box>
          </Paper>
        </Grid>

        {/* Feature Flags */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>System Features</Typography>
            <Divider sx={{ mb: 2 }} />
            <FormControlLabel
              control={
                <Switch
                  checked={config.features.enable_caching}
                  onChange={(e) => handleConfigUpdate('ENABLE_CACHING', e.target.checked, 'features')}
                />
              }
              label="Enable Redis Caching"
            />
          </Paper>
        </Grid>
      </Grid>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">RAG Cockpit</Typography>
        {configLoading && <CircularProgress size={24} />}
      </Box>

      <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab icon={<PlayArrowIcon />} label="Playground" />
        <Tab icon={<SettingsIcon />} label="System Config" />
        <Tab icon={<MonitorHeartIcon />} label="Task Monitor" />
      </Tabs>

      import TaskMonitor from './rag/TaskMonitor';

      // ... (inside RAGCockpit component)

      {tabValue === 0 && renderPlayground()}
      {tabValue === 1 && renderConfig()}
      {tabValue === 2 && <TaskMonitor />}
    </Box>
  );
};

export default RAGCockpit;
