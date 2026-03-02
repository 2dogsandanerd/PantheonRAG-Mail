import React, { useState, useEffect } from 'react';
import {
  Box, Typography, TextField, Button, Alert,
  Paper, Stack, Divider, Tabs, Tab, List, ListItem, ListItemText,
  ListItemIcon, CircularProgress, MenuItem, Select, FormControl, InputLabel,
  Chip, IconButton, Switch, FormControlLabel, Tooltip
} from '@mui/material';
import {
  Save, CheckCircle, Error as ErrorIcon,
  Cloud, Psychology, Settings as SettingsIcon, Language as LanguageIcon,
  Refresh, BugReport, Storage, Security, AutoAwesome
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import {
  getConfiguration, saveConfiguration, testConnections,
  getServicesStatus,
  getOllamaModels, testOllama, testChroma
} from '../api/client';
import SecuritySettings from './settings/SecuritySettings';


/**
 * TabPanel Component
 */
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function Settings() {
  const { t, i18n } = useTranslation();
  const [config, setConfig] = useState({});
  const [originalConfig, setOriginalConfig] = useState({});
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [testResults, setTestResults] = useState([]);
  const [message, setMessage] = useState('');
  const [tabIndex, setTabIndex] = useState(0);
  const [testing, setTesting] = useState(false);

  // Service management state
  const [servicesStatus, setServicesStatus] = useState({ ollama: { running: false }, chroma: { running: false } });
  const [ollamaModels, setOllamaModels] = useState([]);
  const [loadingService, setLoadingService] = useState(null);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const data = await getConfiguration();
        setConfig(data);
        setOriginalConfig(data); // Store original for comparison
        setHasUnsavedChanges(false);
        await refreshServiceStatus();
      } catch (error) {
        setMessage(`${t('common.error')}: ${error.message}`);
      }
    };
    fetchConfig();
  }, [t]);

  // Warn before leaving with unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '';
      }
    };
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [hasUnsavedChanges]);

  // ❌ DISABLED Phase 0: Auto-refresh deactivated - status now only on-demand
  // useEffect(() => {
  //   const interval = setInterval(async () => {
  //     await refreshServiceStatus();
  //   }, 5000);
  //   return () => clearInterval(interval);
  // }, []);

  const refreshServiceStatus = async () => {
    try {
      const status = await getServicesStatus();
      setServicesStatus(status);

      // Load Ollama models if Ollama is running
      if (status.ollama.running) {
        const modelsData = await getOllamaModels();
        setOllamaModels(modelsData.models || []);
      }
    } catch (error) {
      console.error('Failed to fetch service status:', error);
    }
  };

  const handleLanguageChange = (event) => {
    const newLang = event.target.value;
    i18n.changeLanguage(newLang);
    localStorage.setItem('language', newLang);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setConfig(prevConfig => {
      const newConfig = { ...prevConfig, [name]: value };
      // Check if config differs from original
      setHasUnsavedChanges(JSON.stringify(newConfig) !== JSON.stringify(originalConfig));
      return newConfig;
    });
  };

  const handleSave = async () => {
    setMessage(t('common.loading'));
    try {
      // Migrate DATABASE_URL -> lea_database_url on client side before sending
      const payload = { ...config };
      if (payload.DATABASE_URL && !payload.lea_database_url) {
        payload.lea_database_url = payload.DATABASE_URL;
      }
      // Remove old key to avoid re-writing it
      if (payload.DATABASE_URL) {
        delete payload.DATABASE_URL;
      }

      const response = await saveConfiguration(payload);
      setOriginalConfig(config); // Update original after successful save
      setHasUnsavedChanges(false);
      setMessage(t('settings.saved'));
    } catch (error) {
      setMessage(`${t('settings.error')}: ${error.message}`);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setMessage(t('settings.testing'));
    setTestResults([]);
    try {
      const results = await testConnections(config);
      setTestResults(results);
      const allSuccess = results.every(r => r.success);
      setMessage(allSuccess ? t('common.success') : t('common.error'));
    } catch (error) {
      setMessage(`${t('common.error')}: ${error.message}`);
    } finally {
      setTesting(false);
    }
  };



  const handleTestService = async (serviceName) => {
    setLoadingService(`test-${serviceName}`);
    try {
      let result;
      if (serviceName === 'ollama') {
        result = await testOllama();
      } else if (serviceName === 'chroma') {
        result = await testChroma();
      }
      setMessage(result.message + ` (${result.duration}s)`);
    } catch (error) {
      setMessage(`Test failed: ${error.message}`);
    } finally {
      setLoadingService(null);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'success';
      case 'starting': return 'warning';
      case 'stopping': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getStatusLabel = (status) => {
    return status ? status.charAt(0).toUpperCase() + status.slice(1) : 'Unknown';
  };

  const ServiceStatusChip = ({ serviceStatus }) => {
    const status = serviceStatus?.status || 'stopped';
    return (
      <Box>
        <Chip
          label={getStatusLabel(status)}
          color={getStatusColor(status)}
          size="small"
          icon={status === 'running' ? <CheckCircle /> : status === 'error' ? <ErrorIcon /> : null}
        />
        {serviceStatus?.running && serviceStatus?.host && serviceStatus?.port && (
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
            {t('settings.services.runningOn')}: {serviceStatus.host}:{serviceStatus.port}
          </Typography>
        )}
        {serviceStatus?.error && (
          <Typography variant="caption" color="error" sx={{ display: 'block', mt: 0.5 }}>
            {serviceStatus.error}
          </Typography>
        )}
      </Box>
    );
  };



  return (
    <Box sx={{ mb: 4 }}>
      {/* Language Switcher - Top Right */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">{t('settings.title')}</Typography>

        <FormControl variant="outlined" size="small" sx={{ minWidth: 150 }}>
          <InputLabel>{t('settings.language.select')}</InputLabel>
          <Select
            value={i18n.language}
            onChange={handleLanguageChange}
            label={t('settings.language.select')}
            startAdornment={<LanguageIcon sx={{ mr: 1, color: 'action.active' }} />}
          >
            <MenuItem value="en">{t('settings.language.english')}</MenuItem>
            <MenuItem value="de">{t('settings.language.german')}</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {hasUnsavedChanges && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          ⚠️ {t('settings.unsavedChanges') || 'Ungespeicherte Änderungen! Bitte auf "Speichern" klicken.'}
        </Alert>
      )}

      {message && (
        <Alert
          severity={message.includes(t('common.error')) || message.includes('Failed') ? 'error' : 'success'}
          sx={{ mb: 3 }}
          onClose={() => setMessage('')}
        >
          {message}
        </Alert>
      )}



      <Paper elevation={2}>
        <Tabs
          value={tabIndex}
          onChange={(e, newValue) => setTabIndex(newValue)}
          aria-label="settings tabs"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab icon={<Cloud />} label={t('settings.tabs.services')} iconPosition="start" />
          <Tab icon={<Psychology />} label={t('settings.tabs.llm')} iconPosition="start" />
          <Tab icon={<SettingsIcon />} label={t('settings.tabs.email')} iconPosition="start" />
          <Tab icon={<Storage />} label={t('settings.tabs.databases')} iconPosition="start" />
          <Tab icon={<Security />} label={t('settings.tabs.security', 'Security')} iconPosition="start" />
          <Tab icon={<AutoAwesome />} label="RAG Settings" iconPosition="start" />
        </Tabs>

        {/* TAB 1: Services */}
        <TabPanel value={tabIndex} index={0}>
          <Stack spacing={3}>
            {/* Ollama Service */}
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Stack spacing={2}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box>
                    <Typography variant="h6">Ollama Service</Typography>
                    <ServiceStatusChip serviceStatus={servicesStatus.ollama} />
                  </Box>

                </Box>

                <TextField
                  fullWidth
                  label={t('settings.services.ollamaHost')}
                  name="OLLAMA_HOST"
                  value={config.OLLAMA_HOST || ''}
                  onChange={handleChange}
                  placeholder="http://localhost:11434"
                  helperText={t('settings.services.ollamaHostHelp')}
                  variant="outlined"
                  disabled={servicesStatus.ollama.running}
                />

                <TextField
                  fullWidth
                  label="Ollama Binary Path"
                  name="OLLAMA_BINARY_PATH"
                  value={config.OLLAMA_BINARY_PATH || '/usr/local/bin/ollama'}
                  onChange={handleChange}
                  helperText="Path to Ollama binary"
                  variant="outlined"
                  disabled={servicesStatus.ollama.running}
                />
              </Stack>
            </Paper>

            {/* ChromaDB Service */}
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Stack spacing={2}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box>
                    <Typography variant="h6">ChromaDB Service</Typography>
                    <ServiceStatusChip serviceStatus={servicesStatus.chroma} />
                  </Box>

                </Box>

                <TextField
                  fullWidth
                  label={t('settings.services.chromaHost')}
                  name="CHROMA_HOST"
                  value={config.CHROMA_HOST || ''}
                  onChange={handleChange}
                  placeholder="http://localhost:8000"
                  helperText={t('settings.services.chromaHostHelp')}
                  variant="outlined"
                  disabled={servicesStatus.chroma.running}
                />
              </Stack>
            </Paper>

            <Divider />

            <Stack direction="row" spacing={2}>
              <Button
                variant="contained"
                color={hasUnsavedChanges ? "error" : "primary"}
                startIcon={<Save />}
                onClick={handleSave}
                sx={{
                  animation: hasUnsavedChanges ? 'pulse 2s infinite' : 'none',
                  '@keyframes pulse': {
                    '0%, 100%': { opacity: 1 },
                    '50%': { opacity: 0.7 }
                  }
                }}
              >
                {t('settings.save')}{hasUnsavedChanges && ' *'}
              </Button>

              <Button
                variant="outlined"
                startIcon={testing ? <CircularProgress size={20} /> : <CheckCircle />}
                onClick={handleTest}
                disabled={testing}
              >
                {testing ? t('settings.testing') : t('settings.test')}
              </Button>
            </Stack>
          </Stack>
        </TabPanel>

        {/* TAB 2: LLM */}
        <TabPanel value={tabIndex} index={1}>
          <Stack spacing={3}>
            <TextField
              fullWidth
              label={t('settings.llm.provider')}
              name="LLM_PROVIDER"
              value={config.LLM_PROVIDER || ''}
              onChange={handleChange}
              placeholder="ollama"
              helperText={t('settings.llm.providerHelp')}
              variant="outlined"
              disabled={!servicesStatus.ollama.running}
            />

            <FormControl fullWidth disabled={!servicesStatus.ollama.running || ollamaModels.length === 0}>
              <InputLabel>{t('settings.llm.model')}</InputLabel>
              <Select
                name="LLM_MODEL"
                value={config.LLM_MODEL || ''}
                onChange={handleChange}
                label={t('settings.llm.model')}
              >
                {ollamaModels.map(model => (
                  <MenuItem key={model.name} value={model.name}>{model.name}</MenuItem>
                ))}
              </Select>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                {ollamaModels.length === 0 ? 'Start Ollama to load models' : t('settings.llm.modelHelp')}
              </Typography>
            </FormControl>

            <TextField
              fullWidth
              label={t('settings.llm.embeddingProvider')}
              name="EMBEDDING_PROVIDER"
              value={config.EMBEDDING_PROVIDER || ''}
              onChange={handleChange}
              placeholder="ollama"
              helperText={t('settings.llm.embeddingProviderHelp')}
              variant="outlined"
              disabled={!servicesStatus.ollama.running}
            />

            <FormControl fullWidth disabled={!servicesStatus.ollama.running || ollamaModels.length === 0}>
              <InputLabel>{t('settings.llm.embeddingModel')}</InputLabel>
              <Select
                name="EMBEDDING_MODEL"
                value={config.EMBEDDING_MODEL || ''}
                onChange={handleChange}
                label={t('settings.llm.embeddingModel')}
              >
                {ollamaModels.map(model => (
                  <MenuItem key={model.name} value={model.name}>{model.name}</MenuItem>
                ))}
              </Select>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                {ollamaModels.length === 0 ? 'Start Ollama to load models' : t('settings.llm.embeddingModelHelp')}
              </Typography>
            </FormControl>

            {/* Embedding Dimensions Info */}
            {config.EMBEDDING_MODEL && servicesStatus.ollama.running && (
              <Box sx={{
                p: 2,
                bgcolor: 'background.default',
                borderRadius: 1,
                border: '1px solid',
                borderColor: 'divider'
              }}>
                <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                  📊 Embedding Configuration
                </Typography>
                <Stack spacing={1}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">Model:</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                      {config.EMBEDDING_MODEL}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">Provider:</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                      {config.EMBEDDING_PROVIDER || 'ollama'}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">Estimated Dimensions:</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                      {config.EMBEDDING_MODEL?.includes('nomic-embed-text') ? '768' :
                        config.EMBEDDING_MODEL?.includes('mxbai-embed-large') ? '1024' :
                          config.EMBEDDING_MODEL?.includes('minilm') ? '384' :
                            '768 (default)'}
                    </Typography>
                  </Box>
                </Stack>
                <Alert severity="info" sx={{ mt: 2 }}>
                  <Typography variant="caption">
                    ⚠️ <strong>Important:</strong> This embedding model will be used for NEW collections.
                    Existing collections will keep their original embedding model.
                  </Typography>
                </Alert>
              </Box>
            )}

            <Divider />

            <Button
              variant="contained"
              startIcon={<Save />}
              onClick={handleSave}
              disabled={!servicesStatus.ollama.running}
            >
              {t('settings.save')}
            </Button>
          </Stack>
        </TabPanel>

        {/* TAB 3: Email Configuration */}
        <TabPanel value={tabIndex} index={2}>
          <Stack spacing={3}>
            <Typography variant="h6" gutterBottom>
              {t('settings.email.title')}
            </Typography>

            <TextField
              fullWidth
              select
              label={t('settings.email.provider')}
              name="EMAIL_PROVIDER"
              value={config.EMAIL_PROVIDER || 'imap'}
              onChange={handleChange}
              helperText={t('settings.email.providerHelp')}
              variant="outlined"
              SelectProps={{
                native: true,
              }}
            >
              <option value="imap">{t('settings.email.providerImap')}</option>
            </TextField>
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
              {t('settings.email.gmailImapInfo')}
            </Typography>

            {config.EMAIL_PROVIDER === 'imap' && (
              <>
                <Divider><Typography variant="caption">{t('settings.email.imapSettings')}</Typography></Divider>

                <TextField
                  fullWidth
                  label={t('settings.email.emailAddress')}
                  name="EMAIL_USER"
                  value={config.EMAIL_USER || ''}
                  onChange={handleChange}
                  placeholder="your@email.com"
                  helperText={t('settings.email.emailAddressHelp')}
                  variant="outlined"
                  required
                />

                <TextField
                  fullWidth
                  label={t('settings.email.emailPassword')}
                  name="EMAIL_PASSWORD"
                  type="password"
                  value={config.EMAIL_PASSWORD || ''}
                  onChange={handleChange}
                  placeholder={t('settings.email.emailPasswordPlaceholder')}
                  helperText={t('settings.email.emailPasswordHelp')}
                  variant="outlined"
                  required
                />

                <TextField
                  fullWidth
                  label={t('settings.email.imapHost')}
                  name="IMAP_HOST"
                  value={config.IMAP_HOST || ''}
                  onChange={handleChange}
                  placeholder="imap.gmail.com"
                  helperText={t('settings.email.imapHostHelp')}
                  variant="outlined"
                  required
                />

                <TextField
                  fullWidth
                  label={t('settings.email.imapPort')}
                  name="IMAP_PORT"
                  type="number"
                  value={config.IMAP_PORT || '993'}
                  onChange={handleChange}
                  placeholder="993"
                  helperText={t('settings.email.imapPortHelp')}
                  variant="outlined"
                  required
                />

                <TextField
                  fullWidth
                  label={t('settings.email.smtpHost')}
                  name="SMTP_HOST"
                  value={config.SMTP_HOST || ''}
                  onChange={handleChange}
                  placeholder="smtp.gmail.com"
                  helperText={t('settings.email.smtpHostHelp')}
                  variant="outlined"
                  required
                />

                <TextField
                  fullWidth
                  label={t('settings.email.smtpPort')}
                  name="SMTP_PORT"
                  type="number"
                  value={config.SMTP_PORT || '587'}
                  onChange={handleChange}
                  placeholder="587"
                  helperText={t('settings.email.smtpPortHelp')}
                  variant="outlined"
                  required
                />
              </>
            )}

            {config.EMAIL_PROVIDER === 'gmail' && (
              <>
                <Divider><Typography variant="caption">{t('settings.email.gmailOauth')}</Typography></Divider>
                <Alert severity="info">
                  {t('settings.email.gmailOauthInfo')}
                </Alert>
              </>
            )}

            <Divider />

            <Button
              variant="contained"
              startIcon={<Save />}
              onClick={handleSave}
              fullWidth
            >
              {t('settings.save')}
            </Button>
          </Stack>
        </TabPanel>

        {/* TAB 4: Databases */}
        <TabPanel value={tabIndex} index={3}>
          <Stack spacing={3}>
            <Typography variant="h6" gutterBottom>
              {t('settings.databases.title')}
            </Typography>

            <TextField
              fullWidth
              label={t('settings.databases.learningDb')}
              name="lea_database_url"
              value={config.lea_database_url || config.DATABASE_URL || ''}
              onChange={handleChange}
              placeholder="sqlite:///./data/learning.db"
              helperText={t('settings.databases.learningDbHelp')}
              variant="outlined"
            />

            <TextField
              fullWidth
              label={t('settings.databases.ragDb')}
              name="RAG_DATABASE_URL"
              value={config.RAG_DATABASE_URL || ''}
              onChange={handleChange}
              placeholder="sqlite:///./data/gmail_rag.db"
              helperText={t('settings.databases.ragDbHelp')}
              variant="outlined"
            />

            <Divider />

            <Button
              variant="contained"
              startIcon={<Save />}
              onClick={handleSave}
              fullWidth
            >
              {t('settings.save')}
            </Button>
          </Stack>
        </TabPanel>

        {/* TAB 5: Security */}
        <TabPanel value={tabIndex} index={4}>
          <SecuritySettings />
        </TabPanel>

        {/* TAB 6: RAG Settings */}
        <TabPanel value={tabIndex} index={5}>
          <Stack spacing={3}>
            <Box>
              <Typography variant="h6" gutterBottom>
                🤖 Advanced RAG Features
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Configure advanced retrieval and ranking features for your RAG system.
                These settings affect query quality and performance.
              </Typography>
            </Box>

            <Divider />

            {/* Reranker Toggle */}
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Stack spacing={2}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 1 }}>
                      🎯 Cross-Encoder Reranker
                      <Chip
                        label="Recommended"
                        size="small"
                        color="success"
                        sx={{ height: 20 }}
                      />
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                      Re-ranks search results using a cross-encoder model for better precision.
                      Improves answer quality by 10-30% but adds ~200ms latency.
                    </Typography>
                  </Box>
                  <Tooltip title="Enable/Disable Reranker">
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.RERANKER_ENABLED === 'true' || config.RERANKER_ENABLED === true}
                          onChange={(e) => handleChange({
                            target: {
                              name: 'RERANKER_ENABLED',
                              value: e.target.checked ? 'true' : 'false'
                            }
                          })}
                          color="primary"
                        />
                      }
                      label=""
                      sx={{ m: 0 }}
                    />
                  </Tooltip>
                </Box>

                {(config.RERANKER_ENABLED === 'true' || config.RERANKER_ENABLED === true) && (
                  <Box sx={{ pl: 2, borderLeft: '3px solid', borderColor: 'primary.main' }}>
                    <TextField
                      fullWidth
                      label="Reranker Model"
                      name="RERANKER_MODEL"
                      value={config.RERANKER_MODEL || 'BAAI/bge-reranker-base'}
                      onChange={handleChange}
                      placeholder="BAAI/bge-reranker-base"
                      helperText="Cross-encoder model for reranking (local)"
                      variant="outlined"
                      size="small"
                      sx={{ mt: 1 }}
                    />
                    <TextField
                      fullWidth
                      label="Top K Results"
                      name="RERANKER_TOP_K"
                      type="number"
                      value={config.RERANKER_TOP_K || '5'}
                      onChange={handleChange}
                      placeholder="5"
                      helperText="Number of top results to return after reranking"
                      variant="outlined"
                      size="small"
                      sx={{ mt: 2 }}
                    />
                  </Box>
                )}
              </Stack>
            </Paper>

            {/* Parent-Child Retriever Toggle */}
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Stack spacing={2}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                      📚 Parent-Child Document Retriever
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                      Search in small chunks, but return full parent documents for better context.
                      Reduces hallucinations by providing complete information.
                    </Typography>
                  </Box>
                  <Tooltip title="Enable/Disable Parent-Child Retriever">
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.USE_PARENT_RETRIEVER === 'true' || config.USE_PARENT_RETRIEVER === true}
                          onChange={(e) => handleChange({
                            target: {
                              name: 'USE_PARENT_RETRIEVER',
                              value: e.target.checked ? 'true' : 'false'
                            }
                          })}
                          color="primary"
                        />
                      }
                      label=""
                      sx={{ m: 0 }}
                    />
                  </Tooltip>
                </Box>
              </Stack>
            </Paper>

            {/* Advanced Pipeline Toggle */}
            <Paper variant="outlined" sx={{ p: 2 }}>
              <Stack spacing={2}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 1 }}>
                      ⚡ Advanced RAG Pipeline
                      <Chip
                        label="Experimental"
                        size="small"
                        color="warning"
                        sx={{ height: 20 }}
                      />
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                      Enables query enhancement, hybrid retrieval, and advanced post-processing.
                      Best for complex queries but slower.
                    </Typography>
                  </Box>
                  <Tooltip title="Enable/Disable Advanced Pipeline">
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.USE_ADVANCED_PIPELINE === 'true' || config.USE_ADVANCED_PIPELINE === true}
                          onChange={(e) => handleChange({
                            target: {
                              name: 'USE_ADVANCED_PIPELINE',
                              value: e.target.checked ? 'true' : 'false'
                            }
                          })}
                          color="primary"
                        />
                      }
                      label=""
                      sx={{ m: 0 }}
                    />
                  </Tooltip>
                </Box>
              </Stack>
            </Paper>

            {/* Semantic Router (Coming Soon) */}
            <Paper variant="outlined" sx={{ p: 2, opacity: 0.6, position: 'relative' }}>
              <Chip
                label="Coming Soon"
                size="small"
                sx={{
                  position: 'absolute',
                  top: 8,
                  right: 8,
                  bgcolor: 'grey.300',
                  color: 'grey.700'
                }}
              />
              <Stack spacing={2}>
                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                    🧭 Semantic Router
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                    Automatically routes queries to specialized lanes (Math, News, Explain).
                    Each lane uses optimized retrieval strategies.
                  </Typography>
                </Box>
              </Stack>
            </Paper>

            <Divider />

            {/* Info Box */}
            <Alert severity="info">
              <Typography variant="body2">
                <strong>💡 Tip:</strong> Start with Reranker enabled for best quality.
                Enable Parent-Child Retriever if you have long documents.
                Advanced Pipeline is experimental and best for testing.
              </Typography>
            </Alert>

            {/* Save Button */}
            <Button
              variant="contained"
              color={hasUnsavedChanges ? "error" : "primary"}
              startIcon={<Save />}
              onClick={handleSave}
              fullWidth
              sx={{
                animation: hasUnsavedChanges ? 'pulse 2s infinite' : 'none',
                '@keyframes pulse': {
                  '0%, 100%': { opacity: 1 },
                  '50%': { opacity: 0.7 }
                }
              }}
            >
              {t('settings.save')}{hasUnsavedChanges && ' *'}
            </Button>
          </Stack>
        </TabPanel>
      </Paper>

      {/* Test Results Section */}
      {testResults.length > 0 && (
        <Paper elevation={2} sx={{ mt: 3, p: 2 }}>
          <Typography variant="h6" gutterBottom>
            {t('settings.testResults.title')}
          </Typography>
          <List>
            {testResults.map((result, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  {result.success ? (
                    <CheckCircle sx={{ color: 'success.main' }} />
                  ) : (
                    <ErrorIcon sx={{ color: 'error.main' }} />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={result.component}
                  secondary={`${result.message} (${result.duration.toFixed(2)}s)`}
                  primaryTypographyProps={{
                    color: result.success ? 'success.main' : 'error.main',
                    fontWeight: 'medium'
                  }}
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  );
}

export default Settings;