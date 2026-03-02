import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Divider,
  IconButton,
  Tooltip,
  Chip,
  Collapse,
  List,
  ListItemButton,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import {
  Description as DescriptionIcon,
  Code as CodeIcon,
  AccountTree as FlowIcon,
  Assessment as AnalysisIcon,
  TableChart as TableIcon,
  Download as DownloadIcon,
  Print as PrintIcon,
  ExpandLess,
  ExpandMore,
  FolderOpen,
  InsertDriveFile
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import mermaid from 'mermaid';

// Initialize Mermaid
mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  securityLevel: 'loose',
  flowchart: {
    useMaxWidth: true,
    htmlLabels: true,
    curve: 'basis'
  }
});

// Tab Configuration
const DOCS_CONFIG = [
  {
    id: 'overview',
    label: 'Overview',
    icon: <DescriptionIcon />,
    file: 'COMPLETE_DOCUMENTATION_REPORT.md',
    description: 'Complete documentation summary',
    path: 'planung/1-code-streamlit/'
  },
  {
    id: 'code',
    label: 'Code Docs',
    icon: <CodeIcon />,
    file: 'CODE_DOCUMENTATION.md',
    description: 'All functions and classes (3,798 lines)',
    path: 'planung/1-code-streamlit/streamlit_code_rag/',
    large: true
  },
  {
    id: 'flowcharts',
    label: 'Flowcharts',
    icon: <FlowIcon />,
    file: 'PROCESS_FLOWCHARTS.md',
    description: '6 critical process flowcharts',
    path: 'planung/1-code-streamlit/streamlit_code_rag/'
  },
  {
    id: 'analysis',
    label: 'Analysis',
    icon: <AnalysisIcon />,
    file: 'ANALYSIS_REPORT.md',
    description: 'React migration plan analysis',
    path: 'planung/react/'
  },
  {
    id: 'coverage',
    label: 'Coverage',
    icon: <TableIcon />,
    file: 'coverage_report.json',
    description: 'RAG coverage metrics',
    path: 'planung/1-code-streamlit/streamlit_code_rag/',
    isJson: true
  }
];

// Custom Mermaid Component
function MermaidDiagram({ code }) {
  const [svg, setSvg] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!code) return;

    const renderDiagram = async () => {
      try {
        const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
        const { svg } = await mermaid.render(id, code);
        setSvg(svg);
        setError(null);
      } catch (err) {
        console.error('Mermaid render error:', err);
        setError(err.message);
      }
    };

    renderDiagram();
  }, [code]);

  if (error) {
    return (
      <Alert severity="error" sx={{ my: 2 }}>
        Mermaid rendering error: {error}
      </Alert>
    );
  }

  return (
    <Box
      sx={{
        my: 3,
        p: 2,
        bgcolor: '#fafafa',
        borderRadius: 2,
        overflow: 'auto',
        border: '1px solid #e0e0e0',
        '& svg': {
          maxWidth: '100%',
          height: 'auto'
        }
      }}
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
}

// Table of Contents Component (for large docs)
function TableOfContents({ markdown, onNavigate }) {
  const [toc, setToc] = useState([]);
  const [expanded, setExpanded] = useState({});

  useEffect(() => {
    if (!markdown) return;

    // Extract headings
    const headingRegex = /^(#{1,3})\s+(.+)$/gm;
    const headings = [];
    let match;

    while ((match = headingRegex.exec(markdown)) !== null) {
      const level = match[1].length;
      const text = match[2].replace(/[📄🏛️🔧📊✅⚠️❌]/g, '').trim();
      const id = text.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-');

      headings.push({ level, text, id });
    }

    setToc(headings);

    // Auto-expand first level
    const initialExpanded = {};
    headings.filter(h => h.level === 2).forEach(h => {
      initialExpanded[h.id] = true;
    });
    setExpanded(initialExpanded);
  }, [markdown]);

  const toggleExpand = (id) => {
    setExpanded(prev => ({ ...prev, [id]: !prev[id] }));
  };

  if (toc.length === 0) return null;

  // Group TOC by level
  const groupedToc = [];
  let currentH2 = null;

  toc.forEach(item => {
    if (item.level === 2) {
      currentH2 = { ...item, children: [] };
      groupedToc.push(currentH2);
    } else if (item.level === 3 && currentH2) {
      currentH2.children.push(item);
    }
  });

  return (
    <Paper
      elevation={0}
      sx={{
        width: 280,
        height: 'calc(100vh - 200px)',
        position: 'sticky',
        top: 20,
        overflow: 'auto',
        borderRight: 1,
        borderColor: 'divider'
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
          📑 On this page
        </Typography>
        <List dense disablePadding>
          {groupedToc.slice(0, 30).map((item) => (
            <React.Fragment key={item.id}>
              <ListItemButton
                onClick={() => {
                  onNavigate(item.id);
                  if (item.children.length > 0) {
                    toggleExpand(item.id);
                  }
                }}
                sx={{ py: 0.5, borderRadius: 1 }}
              >
                {item.children.length > 0 && (
                  <ListItemIcon sx={{ minWidth: 24 }}>
                    {expanded[item.id] ? <ExpandLess fontSize="small" /> : <ExpandMore fontSize="small" />}
                  </ListItemIcon>
                )}
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{ variant: 'caption', fontWeight: 500 }}
                />
              </ListItemButton>

              {item.children.length > 0 && (
                <Collapse in={expanded[item.id]} timeout="auto" unmountOnExit>
                  <List dense disablePadding sx={{ pl: 3 }}>
                    {item.children.map(child => (
                      <ListItemButton
                        key={child.id}
                        onClick={() => onNavigate(child.id)}
                        sx={{ py: 0.3, borderRadius: 1 }}
                      >
                        <ListItemText
                          primary={child.text}
                          primaryTypographyProps={{ variant: 'caption', color: 'text.secondary' }}
                        />
                      </ListItemButton>
                    ))}
                  </List>
                </Collapse>
              )}
            </React.Fragment>
          ))}
        </List>
      </Box>
    </Paper>
  );
}

// JSON Viewer Component
function JsonViewer({ data }) {
  return (
    <Paper sx={{ p: 3, bgcolor: '#1e1e1e', color: '#d4d4d4', overflow: 'auto' }}>
      <pre style={{ margin: 0, fontSize: '0.875rem', lineHeight: 1.6 }}>
        {JSON.stringify(data, null, 2)}
      </pre>
    </Paper>
  );
}

// Markdown Viewer Component
function MarkdownViewer({ markdown, showTOC }) {
  const contentRef = useRef(null);

  const handleNavigate = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <Box sx={{ display: 'flex', flex: 1 }}>
      {showTOC && <TableOfContents markdown={markdown} onNavigate={handleNavigate} />}

      <Box
        ref={contentRef}
        sx={{
          flex: 1,
          p: 4,
          maxWidth: showTOC ? '900px' : '1200px',
          mx: 'auto'
        }}
      >
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            // Headings with IDs
            h1: ({ children }) => {
              const text = String(children).replace(/[📄🏛️🔧📊✅⚠️❌]/g, '').trim();
              const id = text.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-');
              return (
                <Typography id={id} variant="h3" component="h1" sx={{ mt: 4, mb: 2, fontWeight: 700 }}>
                  {children}
                </Typography>
              );
            },
            h2: ({ children }) => {
              const text = String(children).replace(/[📄🏛️🔧📊✅⚠️❌]/g, '').trim();
              const id = text.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-');
              return (
                <Typography id={id} variant="h4" component="h2" sx={{ mt: 3, mb: 2, fontWeight: 600 }}>
                  {children}
                </Typography>
              );
            },
            h3: ({ children }) => {
              const text = String(children).replace(/[📄🏛️🔧📊✅⚠️❌]/g, '').trim();
              const id = text.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-');
              return (
                <Typography id={id} variant="h5" component="h3" sx={{ mt: 2, mb: 1.5, fontWeight: 600 }}>
                  {children}
                </Typography>
              );
            },

            // Paragraphs
            p: ({ children }) => (
              <Typography variant="body1" paragraph sx={{ lineHeight: 1.8 }}>
                {children}
              </Typography>
            ),

            // Code blocks with syntax highlighting and Mermaid support
            code: ({ node, inline, className, children, ...props }) => {
              const match = /language-(\w+)/.exec(className || '');
              const language = match ? match[1] : '';
              const code = String(children).replace(/\n$/, '');

              if (!inline && language === 'mermaid') {
                return <MermaidDiagram code={code} />;
              }

              if (!inline && match) {
                return (
                  <Box sx={{ my: 2 }}>
                    <SyntaxHighlighter
                      style={vscDarkPlus}
                      language={language}
                      PreTag="div"
                      customStyle={{
                        borderRadius: '8px',
                        fontSize: '0.875rem'
                      }}
                      {...props}
                    >
                      {code}
                    </SyntaxHighlighter>
                  </Box>
                );
              }

              return (
                <code
                  style={{
                    backgroundColor: '#f5f5f5',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    fontSize: '0.875em',
                    fontFamily: 'Consolas, Monaco, "Courier New", monospace',
                    border: '1px solid #e0e0e0'
                  }}
                  {...props}
                >
                  {children}
                </code>
              );
            },

            // Tables
            table: ({ children }) => (
              <Box sx={{ overflowX: 'auto', my: 2 }}>
                <table style={{ borderCollapse: 'collapse', width: '100%', border: '1px solid #ddd' }}>
                  {children}
                </table>
              </Box>
            ),
            th: ({ children }) => (
              <th style={{
                border: '1px solid #ddd',
                padding: '12px',
                backgroundColor: '#f5f5f5',
                textAlign: 'left',
                fontWeight: 600
              }}>
                {children}
              </th>
            ),
            td: ({ children }) => (
              <td style={{
                border: '1px solid #ddd',
                padding: '12px'
              }}>
                {children}
              </td>
            ),

            // Lists
            ul: ({ children }) => (
              <Box component="ul" sx={{ pl: 3, my: 1.5 }}>{children}</Box>
            ),
            ol: ({ children }) => (
              <Box component="ol" sx={{ pl: 3, my: 1.5 }}>{children}</Box>
            ),

            // Blockquotes
            blockquote: ({ children }) => (
              <Box
                sx={{
                  borderLeft: 4,
                  borderColor: 'primary.main',
                  bgcolor: '#f5f9ff',
                  p: 2,
                  my: 2,
                  borderRadius: 1
                }}
              >
                {children}
              </Box>
            ),

            // Horizontal rules
            hr: () => <Divider sx={{ my: 3 }} />,

            // Links
            a: ({ href, children }) => (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  color: '#1976d2',
                  textDecoration: 'none',
                  borderBottom: '1px solid #1976d240'
                }}
              >
                {children}
              </a>
            )
          }}
        >
          {markdown}
        </ReactMarkdown>
      </Box>
    </Box>
  );
}

// Main Documentation Component
export default function DocumentationEnhanced() {
  const [activeTab, setActiveTab] = useState('overview');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [jsonData, setJsonData] = useState(null);

  const activeConfig = DOCS_CONFIG.find(d => d.id === activeTab);

  useEffect(() => {
    loadDocument();
  }, [activeTab]);

  const loadDocument = async () => {
    setLoading(true);
    setError(null);
    setContent('');
    setJsonData(null);

    try {
      const config = DOCS_CONFIG.find(d => d.id === activeTab);
      const fullPath = `${config.path}${config.file}`;

      // Try fetch (development mode or served files)
      const response = await fetch(`/${fullPath}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);

      const text = await response.text();

      if (config.isJson) {
        setJsonData(JSON.parse(text));
      } else {
        setContent(text);
      }
    } catch (err) {
      console.error('Failed to load document:', err);
      setError(`Failed to load ${activeConfig.file}: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([content || JSON.stringify(jsonData, null, 2)], {
      type: activeConfig.isJson ? 'application/json' : 'text/markdown'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = activeConfig.file;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Header */}
      <Paper elevation={1} sx={{ borderRadius: 0, zIndex: 10 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', px: 3, py: 1.5, bgcolor: 'background.paper' }}>
          <Typography variant="h6" sx={{ flex: 1, fontWeight: 600 }}>
            📚 Streamlit Code Documentation
          </Typography>

          <Chip
            label={`${DOCS_CONFIG.length} Documents`}
            size="small"
            color="primary"
            variant="outlined"
            sx={{ mr: 2 }}
          />

          <Tooltip title="Download">
            <IconButton onClick={handleDownload} disabled={!content && !jsonData} size="small">
              <DownloadIcon />
            </IconButton>
          </Tooltip>

          <Tooltip title="Print">
            <IconButton onClick={handlePrint} disabled={!content && !jsonData} size="small">
              <PrintIcon />
            </IconButton>
          </Tooltip>
        </Box>

        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            borderTop: 1,
            borderColor: 'divider',
            '& .MuiTab-root': {
              minHeight: 80,
              alignItems: 'flex-start',
              textAlign: 'left'
            }
          }}
        >
          {DOCS_CONFIG.map(doc => (
            <Tab
              key={doc.id}
              value={doc.id}
              icon={doc.icon}
              iconPosition="start"
              label={
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>
                    {doc.label}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                    {doc.description}
                  </Typography>
                </Box>
              }
            />
          ))}
        </Tabs>
      </Paper>

      {/* Content Area */}
      <Box sx={{ flex: 1, overflow: 'auto', bgcolor: '#fafafa' }}>
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Box sx={{ p: 4 }}>
            <Alert severity="error" sx={{ maxWidth: 800, mx: 'auto' }}>
              {error}
            </Alert>
          </Box>
        )}

        {!loading && !error && jsonData && (
          <Box sx={{ p: 4 }}>
            <JsonViewer data={jsonData} />
          </Box>
        )}

        {!loading && !error && content && (
          <MarkdownViewer
            markdown={content}
            showTOC={activeConfig.large}
          />
        )}
      </Box>
    </Box>
  );
}
