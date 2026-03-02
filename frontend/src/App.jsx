
import React, { useState, useEffect } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import { Box, Tabs, Tab, Container, Backdrop, CircularProgress, Button, Typography } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import { Settings as SettingsIcon, Email, Dashboard as DashboardIcon, School, Description, Storage, BarChart, Drafts as DraftsIcon, Code as DevIcon, Build as BuildIcon, Speed as SpeedIcon, LibraryBooks, Chat as ChatIcon } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { SnackbarProvider } from 'notistack';
import { theme } from './theme';
import './i18n'; // Initialize i18n
import Settings from './components/Settings';
import Inbox from './components/Inbox';
import DraftView from './components/DraftView';
import Dashboard from './components/Dashboard';
import Learning from './components/Learning';
import DraftsList from './components/DraftsList';
import Documentation from './components/Documentation';
import RAGManagement from './components/rag/RAGManagement';
import Statistics from './components/Statistics';
import DevTools from './components/DevTools';
import RAGCockpit from './components/RAGCockpit';
import OnboardingWizard from './components/OnboardingWizard';
import PerformanceDashboard from './components/PerformanceDashboard';
import KnowledgeBase from './components/KnowledgeBase';
import ChatInterface from './components/ChatInterface';
import { useServiceStatus } from './hooks/useServiceStatus';
import LoginForm from './components/LoginForm';
import { authService } from './api/auth';

function App() {
  const { t } = useTranslation();
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [activeTab, setActiveTab] = useState(0); // 0=Dashboard, 1=Inbox, 2=Drafts, 3=Learning, 4=RAG Management, 5=Statistics, 6=Performance, 7=Settings, 8=Docs, 9=Dev, 10=Setup, 11=KnowledgeBase, 12=Chat

  // Auth State
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authLoading, setAuthLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState(null);

  // Authentication Check
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const user = await authService.getMe();
        setCurrentUser(user);
        setIsAuthenticated(true);
      } catch (error) {
        setIsAuthenticated(false);
      } finally {
        setAuthLoading(false);
      }
    };
    checkAuth();
  }, []);

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    authService.logout();
    setIsAuthenticated(false);
    setCurrentUser(null);
  };

  // Draft-Modus Configuration State
  const [draftMode, setDraftMode] = useState('folder'); // 'folder' | 'auto'
  const [draftFolderName, setDraftFolderName] = useState('AI_DRAFT');

  // 🔧 FIX: WebSocket connection at App level - prevents leak from Dashboard mount/unmount
  // Get WebSocket URL from Electron API (uses dynamic backend port)
  const wsUrl = window.electronAPI?.getWebSocketURL();
  const serviceStatus = useServiceStatus({ wsUrl });

  const handleEmailSelect = (email) => {
    setSelectedEmail(email);
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  if (authLoading) {
    return (
      <Backdrop open sx={{ color: '#fff', flexDirection: 'column', gap: 2 }}>
        <CircularProgress color="inherit" />
        <div style={{ color: '#fff', marginTop: 8 }}>PantheonMail lädt...</div>
      </Backdrop>
    );
  }

  if (!isAuthenticated) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <LoginForm onLoginSuccess={handleLoginSuccess} />
      </ThemeProvider>
    );
  }

  return (
    <SnackbarProvider maxSnack={3} anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
          {/* Header with Tabs */}
          <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
            <Tabs
              value={activeTab}
              onChange={handleTabChange}
              variant="fullWidth"
              sx={{ px: 2 }}
            >
              <Tab icon={<DashboardIcon />} label={t('tabs.dashboard')} iconPosition="start" />
              <Tab icon={<Email />} label={t('tabs.emailInbox')} iconPosition="start" />
              <Tab icon={<DraftsIcon />} label={t('tabs.drafts')} iconPosition="start" />
              <Tab icon={<School />} label={t('tabs.learning')} iconPosition="start" />
              <Tab icon={<Storage />} label={t('tabs.ragManagement')} iconPosition="start" />
              <Tab icon={<BarChart />} label={t('tabs.statistics')} iconPosition="start" />
              <Tab icon={<SpeedIcon />} label="Performance" iconPosition="start" />
              <Tab icon={<SettingsIcon />} label={t('tabs.settings')} iconPosition="start" />
              <Tab icon={<Description />} label={t('tabs.documentation')} iconPosition="start" />
              <Tab icon={<DevIcon />} label={t('tabs.ragCockpit')} iconPosition="start" />
              <Tab icon={<BuildIcon />} label="Setup" iconPosition="start" />
              <Tab icon={<LibraryBooks />} label="Knowledge Base" iconPosition="start" />
              <Tab icon={<ChatIcon />} label="Chat" iconPosition="start" />
            </Tabs>
            <Box sx={{ display: 'flex', alignItems: 'center', px: 2, py: 0.5, justifyContent: 'flex-end', borderTop: '1px solid', borderColor: 'divider' }}>
              <Typography variant="caption" color="text.secondary" sx={{ mr: 1 }}>
                {currentUser?.username}
              </Typography>
              <Button size="small" variant="outlined" onClick={handleLogout}>
                Abmelden
              </Button>
            </Box>
          </Box>

          {/* Content Area */}
          <Container maxWidth="xl" sx={{ flexGrow: 1, py: 3, overflowY: 'auto' }}>
            {/* ServiceStatusWidget REMOVED - Phase 0: Was on ALL tabs causing request flood */}
            {activeTab === 0 && <Dashboard serviceStatus={serviceStatus} />}

            {activeTab === 1 && (
              <Box sx={{ display: 'flex', gap: 3, height: '100%' }}>
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Inbox
                    onEmailSelect={handleEmailSelect}
                    draftMode={draftMode}
                    draftFolderName={draftFolderName}
                  />
                </Box>
                <Box sx={{ flex: 2, minWidth: 0 }}>
                  <DraftView
                    selectedEmail={selectedEmail}
                    draftMode={draftMode}
                    draftFolderName={draftFolderName}
                  />
                </Box>
              </Box>
            )}

            {activeTab === 2 && <DraftsList />}

            {activeTab === 3 && <Learning />}

            {activeTab === 4 && <RAGManagement />}

            {activeTab === 5 && <Statistics />}

            {activeTab === 6 && <PerformanceDashboard />}

            {activeTab === 7 && (
              <Settings
                onDraftModeChange={setDraftMode}
                onDraftFolderChange={setDraftFolderName}
                draftMode={draftMode}
                draftFolderName={draftFolderName}
              />
            )}

            {activeTab === 8 && <Documentation />}

            {activeTab === 9 && <RAGCockpit />}

            {activeTab === 10 && <OnboardingWizard />}

            {activeTab === 11 && <KnowledgeBase />}

            {activeTab === 12 && <ChatInterface />}
          </Container>
        </Box>
      </ThemeProvider>
    </SnackbarProvider>
  );
}

export default App;
