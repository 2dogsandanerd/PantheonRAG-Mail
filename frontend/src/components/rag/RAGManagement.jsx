import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Tabs, Tab, Container, Alert, CircularProgress, Paper,
  Stack, Chip, Button, useTheme
} from '@mui/material';
import { Settings as SettingsIcon, Psychology } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import CollectionManager from './CollectionManager';
import DocumentUploader from './DocumentUploader';
import DocumentUploaderEnhanced from './DocumentUploaderEnhanced';
import DoclingIngestion from './DoclingIngestion';
import SmartDoclingUploader from './SmartDoclingUploader';
import IntelligentUploader from './IntelligentUploader';
import DocumentBrowser from './DocumentBrowser';
import QueryTester from './QueryTester';
import RagignoreGeneratorModal from './RagignoreGeneratorModal';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`rag-tabpanel-${index}`}
      aria-labelledby={`rag-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export default function RAGManagement() {
  const { t } = useTranslation();
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [currentCollection, setCurrentCollection] = useState('');
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploaderType, setUploaderType] = useState('docling'); // 'legacy', 'enhanced', 'docling'
  const [isUploading, setIsUploading] = useState(false); // Track upload state to disable tabs
  const [ragignoreModalOpen, setRagignoreModalOpen] = useState(false);

  // Services status
  const [servicesStatus, setServicesStatus] = useState({
    chroma: { running: false },
    ollama: { running: false }
  });
  const [config, setConfig] = useState({});

  const loadCollections = async () => {
    try {
      setLoading(true);
      setError(null);
      const { getRAGCollections } = await import('../../api/client');
      const data = await getRAGCollections();
      setCollections(data.collections || []);

      // Set default collection if none selected or if the current one is no longer valid
      if (data.collections && data.collections.length > 0) {
        if (!currentCollection || !data.collections.some(col => col.name === currentCollection)) {
          setCurrentCollection(data.collections[0].name);
        }
      } else {
        setCurrentCollection(''); // No collections available
      }
    } catch (err) {
      setError(`Failed to load collections: ${err.message}`);
      console.error('Error loading collections:', err);
      setCurrentCollection(''); // Clear current collection on error
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCollections();
    // loadServicesStatus(); // ❌ DISABLED Phase 0: Status now from Dashboard only

    // ❌ DISABLED Phase 0: Services status polling removed
    // const interval = setInterval(loadServicesStatus, 5000);
    // return () => clearInterval(interval);
  }, []);

  const handleCollectionChange = (newCollection) => {
    setCurrentCollection(newCollection);
  };

  const handleCollectionUpdate = () => {
    loadCollections();
  };

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
          🧠 RAG Management
        </Typography>
        <Button
          variant="outlined"
          onClick={() => setRagignoreModalOpen(true)}
          startIcon={<span>🤖</span>}
        >
          Auto-Generate .ragignore
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* ❌ DISABLED: ChromaDB & Services Status - Now shown in Dashboard only
      <Paper sx={{ p: 3, mb: 3, border: `1px solid ${theme.palette.divider}` }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          🔧 Services Status
        </Typography>

        <Stack direction="row" spacing={3} sx={{ flexWrap: 'wrap', gap: 2, mb: 2 }}>
          <Box sx={{
            flex: '1 1 250px',
            p: 2,
            background: theme.palette.background.default,
            borderRadius: 1,
            border: `1px solid ${theme.palette.divider}`
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Box sx={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                backgroundColor: servicesStatus.chroma?.running ? 'success.main' : 'error.main',
                mr: 1,
                boxShadow: servicesStatus.chroma?.running
                  ? `0 0 8px ${theme.palette.success.main}`
                  : `0 0 8px ${theme.palette.error.main}`
              }} />
              <Typography variant="subtitle2" sx={{ color: 'text.primary', fontWeight: 'bold' }}>
                ChromaDB (Vector Database)
              </Typography>
            </Box>
            {servicesStatus.chroma?.host && (
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                {servicesStatus.chroma.host}{servicesStatus.chroma.port ? `:${servicesStatus.chroma.port}` : ''}
              </Typography>
            )}
            <Typography
              variant="body2"
              sx={{
                color: servicesStatus.chroma?.running ? 'success.main' : 'error.main',
                fontWeight: 'medium'
              }}
            >
              {servicesStatus.chroma?.running ? '✅ Online' : '❌ Offline'}
            </Typography>
          </Box>

          <Box sx={{
            flex: '1 1 250px',
            p: 2,
            background: theme.palette.background.default,
            borderRadius: 1,
            border: `1px solid ${theme.palette.divider}`
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Box sx={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                backgroundColor: servicesStatus.ollama?.running ? 'success.main' : 'error.main',
                mr: 1,
                boxShadow: servicesStatus.ollama?.running
                  ? `0 0 8px ${theme.palette.success.main}`
                  : `0 0 8px ${theme.palette.error.main}`
              }} />
              <Typography variant="subtitle2" sx={{ color: 'text.primary', fontWeight: 'bold' }}>
                Ollama (LLM Provider)
              </Typography>
            </Box>
            {servicesStatus.ollama?.host && (
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                {servicesStatus.ollama.host}{servicesStatus.ollama.port ? `:${servicesStatus.ollama.port}` : ''}
              </Typography>
            )}
            <Typography
              variant="body2"
              sx={{
                color: servicesStatus.ollama?.running ? 'success.main' : 'error.main',
                fontWeight: 'medium'
              }}
            >
              {servicesStatus.ollama?.running ? '✅ Online' : '❌ Offline'}
            </Typography>
          </Box>

          <Box sx={{
            flex: '1 1 250px',
            p: 2,
            background: theme.palette.background.default,
            borderRadius: 1,
            border: `1px solid ${theme.palette.divider}`
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Psychology sx={{ fontSize: 16, mr: 1, color: 'primary.main' }} />
              <Typography variant="subtitle2" sx={{ color: 'text.primary', fontWeight: 'bold' }}>
                Active LLM Model
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ color: 'text.primary', fontWeight: 'medium' }}>
              {config.LLM_MODEL || 'Not configured'}
            </Typography>
            <Typography variant="caption" sx={{ color: 'text.secondary' }}>
              Provider: {config.LLM_PROVIDER || 'N/A'}
            </Typography>
          </Box>
        </Stack>

        {!servicesStatus.chroma?.running && (
          <Alert
            severity="warning"
            sx={{ mt: 2 }}
            action={
              <Button
                color="inherit"
                size="small"
                startIcon={<SettingsIcon />}
                onClick={() => {
                  const event = new CustomEvent('navigate-to-settings', { detail: { tab: 0 } });
                  window.dispatchEvent(event);
                }}
              >
                Go to Settings
              </Button>
            }
          >
            <strong>ChromaDB is not running.</strong> Start ChromaDB in Settings → Services to create and manage collections.
          </Alert>
        )}
      </Paper>
      */}

      <CollectionManager
        currentCollection={currentCollection}
        onCollectionChange={handleCollectionChange}
        onCollectionUpdate={handleCollectionUpdate}
        collections={collections}
      />

      {/* Enterprise Core v4.0 Hinweis */}
      <Alert severity="info" sx={{ mb: 3, mt: 2 }}>
        <Typography variant="body2">
          <strong>💡 Hinweis:</strong> Dies ist die <strong>Open-Source Edition</strong> mit Basis-RAG (ChromaDB, Vektor-Suche).
          Für Enterprise-Features wie <strong>Multi-Lane Consensus Pipeline</strong>, <strong>Knowledge Graph (Neo4j)</strong>, 
          <strong> Mission-Based Intelligence</strong> und <strong>Six Sigma Quality Assurance</strong> siehe{' '}
          <a href="../planung/manifest_v4.0.md" target="_blank" rel="noopener noreferrer" style={{ fontWeight: 'bold' }}>
            PantheonRAG Enterprise Core v4.0
          </a>.
        </Typography>
      </Alert>

      {collections.length === 0 ? (
        <Alert severity="info" sx={{ mb: 3 }}>
          No RAG collections found. Please create a new collection to get started.
        </Alert>
      ) : (
        <>
          {/* Upload Warning - Show when upload is in progress */}
          {isUploading && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              <Stack direction="row" spacing={2} alignItems="center">
                <CircularProgress size={20} />
                <Typography variant="body2">
                  <strong>Upload in progress...</strong> Please wait while embeddings are being generated. Do not switch tabs or close the application.
                </Typography>
              </Stack>
            </Alert>
          )}

          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs
              value={activeTab}
              onChange={(e, v) => !isUploading && setActiveTab(v)}
              aria-label="RAG management tabs"
              variant="scrollable"
              scrollButtons="auto"
            >
              <Tab label="📤 Upload Documents" disabled={!currentCollection || isUploading} />
              <Tab label="📋 Browse Documents" disabled={!currentCollection || isUploading} />
              <Tab label="🔍 Test Queries" disabled={!currentCollection || isUploading} />
            </Tabs>
          </Box>

          <TabPanel value={activeTab} index={0}>
            <Alert severity="info" sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold', mb: 1 }}>
                📌 Welchen Uploader soll ich nutzen?
              </Typography>
              <Box component="ul" sx={{ m: 0, pl: 2 }}>
                <li>
                  <Typography variant="body2">
                    <strong>Docling (Async)</strong> - EMPFOHLEN für die meisten Fälle
                    <br />
                    <Typography variant="caption" color="text.secondary">
                      Unterstützt: PDF, DOCX, XLSX, PPTX, MD, TXT, CSV, HTML
                    </Typography>
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    <strong>Legacy</strong> - Schnell für einzelne .md oder .txt Dateien
                  </Typography>
                </li>
                <li>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    <strong>Smart Uploader</strong> - Für mehrere Dateien mit Auto-Sortierung
                  </Typography>
                </li>
              </Box>
            </Alert>

            {/* Uploader Type Selector */}
            <Box sx={{ mb: 2, display: 'flex', gap: 1 }}>
              <Chip
                label="🚀 Intelligent Uploader (NEW)"
                color={uploaderType === 'intelligent' ? 'primary' : 'default'}
                onClick={() => setUploaderType('intelligent')}
                clickable
              />
              <Chip
                label="Docling (Async)"
                color={uploaderType === 'docling' ? 'primary' : 'default'}
                onClick={() => setUploaderType('docling')}
                clickable
              />
              <Chip
                label="Enhanced (AI)"
                color={uploaderType === 'enhanced' ? 'primary' : 'default'}
                onClick={() => setUploaderType('enhanced')}
                clickable
              />
              <Chip
                label="Legacy (Einfach)"
                color={uploaderType === 'legacy' ? 'default' : 'default'}
                onClick={() => setUploaderType('legacy')}
                clickable
              />
            </Box>

            {uploaderType === 'intelligent' ? (
              <IntelligentUploader
                collections={collections}
                onUploadSuccess={handleCollectionUpdate}
              />
            ) : uploaderType === 'smart' ? (
              <SmartDoclingUploader
                collections={collections}
                onUploadSuccess={handleCollectionUpdate}
              />
            ) : uploaderType === 'docling' ? (
              <DoclingIngestion
                collections={collections}
                onIngestionSuccess={handleCollectionUpdate}
              />
            ) : uploaderType === 'enhanced' ? (
              <DocumentUploaderEnhanced
                collection={currentCollection}
                collections={collections}
                onUploadSuccess={handleCollectionUpdate}
                onUploadStateChange={setIsUploading}
              />
            ) : (
              <DocumentUploader
                collection={currentCollection}
                onUploadSuccess={handleCollectionUpdate}
                onUploadStateChange={setIsUploading}
              />
            )}
          </TabPanel>

          <TabPanel value={activeTab} index={1}>
            <DocumentBrowser
              collection={currentCollection}
              onDocumentDelete={handleCollectionUpdate}
            />
          </TabPanel>

          <TabPanel value={activeTab} index={2}>
            <QueryTester collection={currentCollection} />
          </TabPanel>
        </>
      )}

      {/* Ragignore Generator Modal */}
      <RagignoreGeneratorModal
        open={ragignoreModalOpen}
        onClose={() => setRagignoreModalOpen(false)}
        folderPath="/mnt/dev/eingang" // Default path, could be dynamic
        onSaveSuccess={() => {
          // Optional: Show a global notification
          console.log('.ragignore saved!');
        }}
      />
    </Container>
  );
}

