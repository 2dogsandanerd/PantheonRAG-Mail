import React, { useState, useEffect, useRef } from 'react';
import {
    Box,
    Paper,
    TextField,
    IconButton,
    Typography,
    Avatar,
    Chip,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    CircularProgress,
    Divider,
    Stack
} from '@mui/material';
import {
    Send as SendIcon,
    Person as PersonIcon,
    SmartToy as BotIcon,
    Clear as ClearIcon
} from '@mui/icons-material';
import axios from 'axios';

const ChatInterface = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [selectedCollection, setSelectedCollection] = useState('');
    const [collections, setCollections] = useState([]);
    const [loading, setLoading] = useState(false);
    const [loadingCollections, setLoadingCollections] = useState(true);
    const messagesEndRef = useRef(null);
    const backendUrl = window.electronAPI?.getBackendURL() || 'http://localhost:33800';

    // Scroll to bottom when messages change
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Load collections on mount
    useEffect(() => {
        loadCollections();
        loadChatHistory();
    }, []);

    const loadCollections = async () => {
        try {
            const response = await axios.get(`${backendUrl}/api/v1/rag/collections`);
            setCollections(response.data.collections || []);
            // Keep selectedCollection empty to search all collections by default
        } catch (error) {
            console.error('Failed to load collections:', error);
        } finally {
            setLoadingCollections(false);
        }
    };

    const loadChatHistory = () => {
        const saved = localStorage.getItem('chat_history');
        if (saved) {
            try {
                setMessages(JSON.parse(saved));
            } catch (e) {
                console.error('Failed to parse chat history');
            }
        }
    };

    const saveChatHistory = (msgs) => {
        localStorage.setItem('chat_history', JSON.stringify(msgs));
    };

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage = {
            id: Date.now(),
            role: 'user',
            content: input,
            timestamp: new Date().toISOString()
        };

        const newMessages = [...messages, userMessage];
        setMessages(newMessages);
        saveChatHistory(newMessages);
        setInput('');
        setLoading(true);

        try {
            // Use advanced multi-collection query with reranker
            const response = await axios.post(`${backendUrl}/api/v1/rag/query`, {
                query: input,
                collections: selectedCollection ? [selectedCollection] : collections.map(c => c.name), // All collections if none selected
                k: 10, // Get more results for reranker
                use_reranker: true, // Use reranker for better results
                temperature: 0.3 // Slightly creative but factual
            });

            const botMessage = {
                id: Date.now() + 1,
                role: 'assistant',
                content: response.data.llm_response || 'No answer generated.',
                sources: response.data.context_chunks || [],
                collections_searched: selectedCollection ? [selectedCollection] : collections.map(c => c.name),
                timestamp: new Date().toISOString()
            };

            const updatedMessages = [...newMessages, botMessage];
            setMessages(updatedMessages);
            saveChatHistory(updatedMessages);
        } catch (error) {
            console.error('Query failed:', error);
            const errorMessage = {
                id: Date.now() + 1,
                role: 'assistant',
                content: `Error: ${error.response?.data?.detail || error.message || 'Failed to get response'}`,
                error: true,
                timestamp: new Date().toISOString()
            };
            const updatedMessages = [...newMessages, errorMessage];
            setMessages(updatedMessages);
            saveChatHistory(updatedMessages);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const clearChat = () => {
        setMessages([]);
        localStorage.removeItem('chat_history');
    };

    return (
        <Box sx={{ height: 'calc(100vh - 150px)', display: 'flex', flexDirection: 'column' }}>
            {/* Header */}
            <Paper sx={{ p: 2, mb: 2 }}>
                <Stack direction="row" spacing={2} alignItems="center">
                    <FormControl sx={{ minWidth: 250 }} size="small">
                        <InputLabel>Filter Collection (Optional)</InputLabel>
                        <Select
                            value={selectedCollection}
                            label="Filter Collection (Optional)"
                            onChange={(e) => setSelectedCollection(e.target.value)}
                            disabled={loadingCollections}
                        >
                            <MenuItem value="">
                                <em>All Collections ({collections.length})</em>
                            </MenuItem>
                            {collections.map((col) => (
                                <MenuItem key={col.name} value={col.name}>
                                    {col.name} ({col.document_count || 0} docs)
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>

                    <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                            🧠 Advanced RAG with Reranker & Multi-Collection Search
                        </Typography>
                        <Typography variant="caption" color="text.disabled">
                            {selectedCollection
                                ? `Searching in: ${selectedCollection}`
                                : `Searching across all ${collections.length} collections`}
                        </Typography>
                    </Box>

                    <IconButton onClick={clearChat} size="small" title="Clear chat">
                        <ClearIcon />
                    </IconButton>
                </Stack>
            </Paper>

            {/* Messages */}
            <Paper sx={{ flex: 1, overflow: 'auto', p: 2, mb: 2 }}>
                {messages.length === 0 ? (
                    <Box sx={{ textAlign: 'center', mt: 10 }}>
                        <BotIcon sx={{ fontSize: 60, color: 'text.disabled', mb: 2 }} />
                        <Typography variant="h6" color="text.secondary">
                            Start a conversation
                        </Typography>
                        <Typography variant="body2" color="text.disabled">
                            Ask questions about your knowledge base
                        </Typography>
                    </Box>
                ) : (
                    messages.map((msg) => (
                        <Box
                            key={msg.id}
                            sx={{
                                display: 'flex',
                                mb: 3,
                                flexDirection: msg.role === 'user' ? 'row-reverse' : 'row'
                            }}
                        >
                            <Avatar
                                sx={{
                                    bgcolor: msg.role === 'user' ? 'primary.main' : 'secondary.main',
                                    mx: 1
                                }}
                            >
                                {msg.role === 'user' ? <PersonIcon /> : <BotIcon />}
                            </Avatar>

                            <Box sx={{ maxWidth: '70%' }}>
                                <Paper
                                    sx={{
                                        p: 2,
                                        bgcolor: msg.error
                                            ? 'error.light'
                                            : msg.role === 'user'
                                                ? 'primary.light'
                                                : 'grey.100',
                                        color: msg.role === 'user' ? 'primary.contrastText' : 'text.primary'
                                    }}
                                >
                                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                                        {msg.content}
                                    </Typography>

                                    {msg.sources && msg.sources.length > 0 && (
                                        <Box sx={{ mt: 2 }}>
                                            <Divider sx={{ mb: 1 }} />
                                            <Typography variant="caption" color="text.secondary">
                                                Sources:
                                            </Typography>
                                            <Stack direction="row" spacing={1} sx={{ mt: 1, flexWrap: 'wrap' }}>
                                                {msg.sources.slice(0, 3).map((source, idx) => (
                                                    <Chip
                                                        key={idx}
                                                        label={source.metadata?.source || `Source ${idx + 1}`}
                                                        size="small"
                                                        variant="outlined"
                                                    />
                                                ))}
                                            </Stack>
                                        </Box>
                                    )}
                                </Paper>

                                <Typography variant="caption" color="text.disabled" sx={{ ml: 1, mt: 0.5 }}>
                                    {new Date(msg.timestamp).toLocaleTimeString()}
                                </Typography>
                            </Box>
                        </Box>
                    ))
                )}
                <div ref={messagesEndRef} />
            </Paper>

            {/* Input */}
            <Paper sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                    <TextField
                        fullWidth
                        multiline
                        maxRows={4}
                        placeholder="Ask a question..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        disabled={loading || collections.length === 0}
                        variant="outlined"
                    />
                    <IconButton
                        color="primary"
                        onClick={handleSend}
                        disabled={loading || !input.trim() || collections.length === 0}
                        sx={{ alignSelf: 'flex-end' }}
                    >
                        {loading ? <CircularProgress size={24} /> : <SendIcon />}
                    </IconButton>
                </Box>
            </Paper>
        </Box>
    );
};

export default ChatInterface;
