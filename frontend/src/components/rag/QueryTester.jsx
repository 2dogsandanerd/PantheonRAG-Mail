import React, { useState } from 'react';
import {
  Paper, TextField, Button, Slider, Typography, Stack,
  Card, CardContent, Chip, Box, Alert, CircularProgress,
  Accordion, AccordionSummary, AccordionDetails, Divider,
  FormControlLabel, Switch
} from '@mui/material';
import {
  Search, ExpandMore, Psychology, Storage,
  TrendingUp, Description, CalendarToday
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { testRAGQuery, queryWithLLM } from '../../api/client';

const getRelevanceColor = (score) => {
  if (score >= 0.8) return 'success';
  if (score >= 0.6) return 'warning';
  return 'error';
};

const getRelevanceLabel = (score) => {
  if (score >= 0.8) return 'High';
  if (score >= 0.6) return 'Medium';
  return 'Low';
};

export default function QueryTester({ collection }) {
  const { t } = useTranslation();
  const [query, setQuery] = useState('');
  const [nResults, setNResults] = useState(5);
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState(null);
  const [queryHistory, setQueryHistory] = useState([]);
  const [showLLMAnswer, setShowLLMAnswer] = useState(true);
  const [llmAnswer, setLLMAnswer] = useState(null);
  const [advancedMode, setAdvancedMode] = useState(false);  // NEW: Multi-Collection mode
  const [domain, setDomain] = useState(null);  // NEW: Domain filter
  const [collectionStats, setCollectionStats] = useState({});  // NEW: Collection stats

  const handleSearch = async () => {
    if (!query.trim()) return;

    setSearching(true);
    setError(null);
    setLLMAnswer(null);
    setCollectionStats({});

    try {
      if (showLLMAnswer) {
        // Use LLM-answer endpoint with advanced mode
        const data = await queryWithLLM(query, collection, nResults, advancedMode, domain);
        setLLMAnswer(data.answer);
        setResults(data.source_chunks || []);
        setCollectionStats(data.collection_stats || {});

        setQueryHistory(prev => [
          {
            query,
            timestamp: new Date(),
            results: data.source_chunks?.length || 0,
            advancedMode,
            collections: Object.keys(data.collection_stats || {}).length
          },
          ...prev.slice(0, 9)
        ]);
      } else {
        // Use original chunk-only endpoint with advanced mode
        const data = await testRAGQuery(query, collection, nResults, advancedMode, domain);
        setResults(data.results || []);
        setCollectionStats(data.collection_stats || {});

        setQueryHistory(prev => [
          {
            query,
            timestamp: new Date(),
            results: data.results?.length || 0,
            advancedMode,
            collections: Object.keys(data.collection_stats || {}).length
          },
          ...prev.slice(0, 9)
        ]);
      }
    } catch (err) {
      setError(`Search failed: ${err.response?.data?.detail || err.message}`);
      console.error('Query test error:', err);
    } finally {
      setSearching(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
      handleSearch();
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return dateString;
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        🔍 Test RAG Queries {advancedMode ? '(Multi-Collection Mode)' : `in "${collection}"`}
      </Typography>

      <Stack spacing={3}>
        {/* Mode Toggles */}
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          <FormControlLabel
            control={
              <Switch
                checked={showLLMAnswer}
                onChange={(e) => setShowLLMAnswer(e.target.checked)}
                color="primary"
              />
            }
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Psychology />
                <Typography variant="body2">
                  Show LLM-Generated Answer
                </Typography>
              </Box>
            }
          />

          <FormControlLabel
            control={
              <Switch
                checked={advancedMode}
                onChange={(e) => setAdvancedMode(e.target.checked)}
                color="secondary"
              />
            }
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Storage />
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  🚀 Advanced Mode (Multi-Collection Query like DraftService)
                </Typography>
              </Box>
            }
          />

          {advancedMode && (
            <Alert severity="info" sx={{ mt: 1 }}>
              <Typography variant="body2">
                <strong>Advanced Mode aktiviert!</strong><br/>
                Das System fragt <strong>ALLE Collections</strong> ab und rankt die Ergebnisse nach Relevanz.<br/>
                Dies ist die <strong>GLEICHE Logik wie im DraftService</strong> - perfekt zum Testen des echten RAG-Systems!
              </Typography>
            </Alert>
          )}
        </Box>

        {/* Query Input */}
        <Box>
          <TextField
            fullWidth
            label="Search Query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your search query..."
            multiline
            rows={3}
            disabled={searching}
            helperText="Press Ctrl+Enter to search"
          />
        </Box>

        {/* Results Configuration */}
        <Box>
          <Typography variant="caption" gutterBottom>
            Number of Results: {nResults}
          </Typography>
          <Slider
            value={nResults}
            onChange={(e, v) => setNResults(v)}
            min={1}
            max={20}
            marks={[
              { value: 1, label: '1' },
              { value: 5, label: '5' },
              { value: 10, label: '10' },
              { value: 20, label: '20' }
            ]}
            disabled={searching}
          />
        </Box>

        {/* Search Button */}
        <Button
          variant="contained"
          startIcon={searching ? <CircularProgress size={20} /> : <Search />}
          onClick={handleSearch}
          disabled={searching || !query.trim()}
          size="large"
          fullWidth
        >
          {searching ? 'Searching...' : 'Search'}
        </Button>

        {/* Error Display */}
        {error && (
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Collection Stats Display (Advanced Mode) */}
        {advancedMode && Object.keys(collectionStats).length > 0 && (
          <Alert severity="info" icon={<Storage />}>
            <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
              📊 Multi-Collection Query Stats
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
              {Object.entries(collectionStats).map(([collName, count]) => (
                <Chip
                  key={collName}
                  label={`${collName}: ${count} chunks`}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              ))}
            </Box>
            <Typography variant="caption" sx={{ display: 'block', mt: 1, color: 'text.secondary' }}>
              Gesamt: {Object.keys(collectionStats).length} Collections abgefragt
            </Typography>
          </Alert>
        )}

        {/* LLM Answer Display */}
        {showLLMAnswer && llmAnswer && (
          <Alert severity="success" icon={<Psychology />}>
            <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
              🤖 LLM-Generated Answer
            </Typography>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', mt: 1 }}>
              {llmAnswer}
            </Typography>
          </Alert>
        )}

        {/* Source Chunks (Collapsible when LLM answer shown) */}
        {showLLMAnswer && results.length > 0 && llmAnswer && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="subtitle2">
                View Source Chunks ({results.length})
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Stack spacing={2}>
                {results.map((result, i) => (
                  <Card key={i} variant="outlined">
                    <CardContent>
                      <Box sx={{ display: 'flex', gap: 1, mb: 1, flexWrap: 'wrap' }}>
                        <Chip label={`Chunk #${i+1}`} size="small" />
                        {result.source_collection && advancedMode && (
                          <Chip
                            label={`📚 ${result.source_collection}`}
                            size="small"
                            color="secondary"
                            variant="outlined"
                          />
                        )}
                        <Chip
                          label={`${(result.relevance_score * 100).toFixed(1)}%`}
                          size="small"
                          color={getRelevanceColor(result.relevance_score)}
                        />
                      </Box>
                      <Typography variant="body2">
                        {result.content}
                      </Typography>
                    </CardContent>
                  </Card>
                ))}
              </Stack>
            </AccordionDetails>
          </Accordion>
        )}

        {/* Results (when LLM answer disabled) */}
        {!showLLMAnswer && results.length > 0 && (
          <Box>
            <Typography variant="subtitle1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Storage />
              Found {results.length} chunks
            </Typography>

            <Stack spacing={2}>
              {results.map((result, i) => (
                <Card key={i} variant="outlined">
                  <CardContent>
                    {/* Result Header */}
                    <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                      <Chip
                        label={`Rank #${result.rank}`}
                        size="small"
                        color="primary"
                      />
                      {result.source_collection && advancedMode && (
                        <Chip
                          label={`📚 ${result.source_collection}`}
                          size="small"
                          color="secondary"
                          variant="filled"
                          sx={{ fontWeight: 'bold' }}
                        />
                      )}
                      <Chip
                        label={`Relevance: ${(result.relevance_score * 100).toFixed(1)}%`}
                        size="small"
                        color={getRelevanceColor(result.relevance_score)}
                        icon={<TrendingUp />}
                      />
                      {result.metadata?.source && (
                        <Chip
                          label={result.metadata.source}
                          size="small"
                          variant="outlined"
                          icon={<Description />}
                        />
                      )}
                      {result.metadata?.uploaded_at && (
                        <Chip
                          label={formatDate(result.metadata.uploaded_at)}
                          size="small"
                          variant="outlined"
                          icon={<CalendarToday />}
                        />
                      )}
                    </Box>

                    {/* Content */}
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        mb: 2,
                        whiteSpace: 'pre-wrap',
                        lineHeight: 1.6
                      }}
                    >
                      {result.content}
                    </Typography>

                    {/* Metadata Details */}
                    {result.metadata && Object.keys(result.metadata).length > 0 && (
                      <Accordion>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Typography variant="caption">
                            Metadata Details
                          </Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Stack spacing={1}>
                            {Object.entries(result.metadata).map(([key, value]) => (
                              <Box key={key} sx={{ display: 'flex', gap: 1 }}>
                                <Typography variant="caption" sx={{ fontWeight: 'bold', minWidth: 100 }}>
                                  {key}:
                                </Typography>
                                <Typography variant="caption">
                                  {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                </Typography>
                              </Box>
                            ))}
                          </Stack>
                        </AccordionDetails>
                      </Accordion>
                    )}
                  </CardContent>
                </Card>
              ))}
            </Stack>
          </Box>
        )}

        {/* Query History */}
        {queryHistory.length > 0 && (
          <Box>
            <Typography variant="subtitle1" gutterBottom>
              Recent Queries
            </Typography>
            <Stack spacing={1}>
              {queryHistory.slice(0, 5).map((historyItem, index) => (
                <Card key={index} variant="outlined" sx={{ p: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" sx={{ flex: 1, mr: 2 }}>
                      {historyItem.query}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                      <Chip 
                        label={`${historyItem.results} results`} 
                        size="small" 
                        variant="outlined" 
                      />
                      <Typography variant="caption" color="text.secondary">
                        {historyItem.timestamp.toLocaleTimeString()}
                      </Typography>
                    </Box>
                  </Box>
                </Card>
              ))}
            </Stack>
          </Box>
        )}

        {/* Help Text */}
        <Alert severity="info">
          <Typography variant="body2">
            <strong>Tips for better results:</strong><br/>
            • Use specific keywords and phrases<br/>
            • Try different query lengths (short vs. long)<br/>
            • Test with different result counts to find optimal relevance<br/>
            • Use natural language questions for best semantic matching<br/>
            <br/>
            <strong>🚀 Advanced Mode (NEW):</strong><br/>
            • Enables Multi-Collection Query across ALL collections<br/>
            • Uses the SAME logic as DraftService for email generation<br/>
            • Perfect for testing your production RAG system<br/>
            • Shows which collections contributed to the results
          </Typography>
        </Alert>
      </Stack>
    </Paper>
  );
}

