import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Collapse from '@mui/material/Collapse';
import { ExpandLess, ExpandMore, Description, Folder } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { getDocsTree, getDocFile } from '../api/client';

// Custom Tree Item Component
function TreeNode({ node, level = 0, onFileClick }) {
  const [open, setOpen] = useState(false);
  const isFolder = Array.isArray(node.children) && node.children.length > 0;
  const isFile = node.path && node.path.endsWith('.md');

  const handleClick = () => {
    if (isFolder) {
      setOpen(!open);
    } else if (isFile) {
      onFileClick(node.path);
    }
  };

  return (
    <>
      <ListItem disablePadding sx={{ pl: level * 2 }}>
        <ListItemButton onClick={handleClick}>
          <ListItemIcon sx={{ minWidth: 36 }}>
            {isFolder ? (open ? <ExpandLess /> : <ExpandMore />) : <Description fontSize="small" />}
          </ListItemIcon>
          <ListItemText
            primary={node.name}
            primaryTypographyProps={{
              fontSize: '0.9rem',
              fontWeight: isFolder ? 500 : 400
            }}
          />
        </ListItemButton>
      </ListItem>
      {isFolder && (
        <Collapse in={open} timeout="auto" unmountOnExit>
          <List component="div" disablePadding>
            {node.children.map((child, idx) => (
              <TreeNode
                key={child.path || `${node.name}-${idx}`}
                node={child}
                level={level + 1}
                onFileClick={onFileClick}
              />
            ))}
          </List>
        </Collapse>
      )}
    </>
  );
}

export default function Documentation() {
  const { t } = useTranslation();
  const [tree, setTree] = useState([]);
  const [content, setContent] = useState('');
  const [isLoadingTree, setIsLoadingTree] = useState(true);
  const [isLoadingFile, setIsLoadingFile] = useState(false);
  const [error, setError] = useState('');

  // Fetch the tree structure on component mount
  useEffect(() => {
    console.log('[Documentation] Fetching docs tree...');
    getDocsTree()
      .then((data) => {
        console.log('[Documentation] Docs tree loaded:', data);
        setTree(data || []);
      })
      .catch((err) => {
        console.error('[Documentation] Error loading tree:', err);
        setError(t('documentation.error.loadTree'));
      })
      .finally(() => {
        setIsLoadingTree(false);
      });
  }, [t]);

  // Handler for when a user clicks on a file
  const handleFileClick = (filepath) => {
    console.log('[Documentation] Loading file:', filepath);
    setIsLoadingFile(true);
    setError('');
    setContent('');

    getDocFile(filepath)
      .then((data) => {
        console.log('[Documentation] File loaded successfully, length:', data.length);
        setContent(data);
      })
      .catch((err) => {
        console.error('[Documentation] Error loading file:', err);
        setError(`${t('documentation.error.loadFile')}: ${filepath}`);
      })
      .finally(() => {
        setIsLoadingFile(false);
      });
  };

  return (
    <Grid container spacing={2} sx={{ height: 'calc(100vh - 120px)' }}>
      {/* Left Pane: Tree View */}
      <Grid item xs={4} md={3} sx={{ borderRight: 1, borderColor: 'divider', overflowY: 'auto' }}>
        <Typography variant="h6" sx={{ p: 2 }}>{t('documentation.fileTree')}</Typography>
        {isLoadingTree ? (
          <CircularProgress sx={{ m: 2 }} />
        ) : (
          <List component="nav" dense>
            {tree.map((node, idx) => (
              <TreeNode
                key={node.path || `root-${idx}`}
                node={node}
                onFileClick={handleFileClick}
              />
            ))}
          </List>
        )}
      </Grid>

      {/* Right Pane: Content View */}
      <Grid item xs={8} md={9} sx={{ overflowY: 'auto', p: 3 }}>
        {isLoadingFile && <CircularProgress sx={{ m: 2 }} />}

        {error && <Alert severity="error">{error}</Alert>}

        {!isLoadingFile && !error && (
          <Box>
            {content ? (
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  // Custom styling for markdown elements
                  h1: ({node, ...props}) => <Typography variant="h3" gutterBottom {...props} />,
                  h2: ({node, ...props}) => <Typography variant="h4" gutterBottom {...props} />,
                  h3: ({node, ...props}) => <Typography variant="h5" gutterBottom {...props} />,
                  h4: ({node, ...props}) => <Typography variant="h6" gutterBottom {...props} />,
                  p: ({node, ...props}) => <Typography paragraph {...props} />,
                  code: ({node, inline, ...props}) => (
                    <Box
                      component={inline ? 'code' : 'pre'}
                      sx={{
                        backgroundColor: '#f5f5f5',
                        padding: inline ? '2px 6px' : '12px',
                        borderRadius: 1,
                        fontFamily: 'monospace',
                        fontSize: '0.9em',
                        display: inline ? 'inline' : 'block',
                        overflowX: 'auto'
                      }}
                      {...props}
                    />
                  ),
                  a: ({node, ...props}) => (
                    <a
                      style={{ color: '#1976d2', textDecoration: 'none' }}
                      target="_blank"
                      rel="noopener noreferrer"
                      {...props}
                    />
                  ),
                }}
              >
                {content}
              </ReactMarkdown>
            ) : (
              <Box>
                <Typography variant="h5">{t('documentation.title')}</Typography>
                <Typography>{t('documentation.placeholder')}</Typography>
              </Box>
            )}
          </Box>
        )}
      </Grid>
    </Grid>
  );
}
