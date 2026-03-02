
import axios from 'axios';

// Lazily get the backend URL from the preload script
export const getBackendURL = () => {
    if (window.electronAPI) {
        try {
            return window.electronAPI.getBackendURL();
        } catch (error) {
            console.error('Error getting backend URL:', error.message);
            // Fallback during initialization race condition
            return 'http://localhost:33800';
        }
    }
    // Fallback for non-electron environments
    return 'http://localhost:33800';
};

// Lazy initialization: get URL on first use, not at module load time
let API_ROOT = null;
let API_BASE_URL = null;

const getAPIRoot = () => {
    if (!API_ROOT) {
        API_ROOT = getBackendURL();
        API_BASE_URL = `${API_ROOT}/api/v1`;
    }
    return API_ROOT;
};

const getAPIBaseURL = () => {
    if (!API_BASE_URL) {
        getAPIRoot(); // Initialize both
    }
    return API_BASE_URL;
};

// Export the function to get API_ROOT dynamically
export { getAPIRoot as API_ROOT };

const client = axios.create({
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add interceptor to set baseURL dynamically
client.interceptors.request.use((config) => {
    config.baseURL = getAPIBaseURL();
    return config;
});

// Add interceptor for response error handling (Rate Limiting)
client.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 429) {
            const retryAfter = error.response.data?.retry_after || '60 seconds';
            const rateError = new Error(`Zu viele Anfragen. Bitte warte ${retryAfter}.`);
            rateError.isRateLimit = true;
            rateError.retryAfter = retryAfter;
            return Promise.reject(rateError);
        }
        return Promise.reject(error);
    }
);

/**
 * Configuration API
 */
export const getConfiguration = async () => {
    const response = await client.get('/config/config');
    return response.data;
};

export const saveConfiguration = async (configData) => {
    const response = await client.post('/config/config', configData);
    return response.data;
};

export const testConnections = async (configData) => {
    const response = await client.post('/config/config/test', configData);
    return response.data;
};

/**
 * Health Check API
 */
export const getBackendHealth = async () => {
    const response = await axios.get(`${getAPIRoot()}/api/health`);
    return response.data;
};

/**
 * Email API
 */

/**
 * Get inbox emails with optional max count
 * @param {number} maxCount - Maximum number of emails to retrieve (default: 10)
 * @returns {Promise<{emails: Array, count: number}>}
 */
export const getInbox = async (maxCount = 10) => {
    const response = await client.get('/email/inbox', {
        params: { max_results: maxCount }
    });
    return response.data;
};

/**
 * Get inbox emails with optional filtering
 * @param {number} maxCount - Maximum number of emails to retrieve (default: 10)
 * @param {string} filterMode - Filter mode: 'none', 'safety', 'auto' (default: 'none')
 * @returns {Promise<{emails: Array, count: number, filtered_emails?: Array, filtered_count?: number}>}
 */
export const getInboxWithFilter = async (maxCount = 10, filterMode = 'none') => {
    const response = await client.get('/email/inbox', {
        params: {
            max_results: maxCount,
            filter_mode: filterMode
        }
    });
    return response.data;
};

/**
 * Get emails from a specific folder/label
 * @param {string} folderName - Name of the folder/label (e.g., "AI_DRAFT")
 * @param {number} maxCount - Maximum number of emails to retrieve (default: 10)
 * @returns {Promise<{emails: Array, count: number}>}
 */
export const getInboxFromFolder = async (folderName, maxCount = 10) => {
    const response = await client.get('/email/inbox/folder', {
        params: {
            folder_name: folderName,
            max_results: maxCount
        }
    });
    return response.data;
};

/**
 * Clear inbox by marking all emails as read
 * @returns {Promise<{message: string, count: number}>}
 */
export const clearInbox = async () => {
    const response = await client.post('/email/clear-inbox');
    return response.data;
};

export const getThread = async (threadId) => {
    const response = await client.get(`/email/thread/${threadId}`);
    return response.data;
};

export const generateDraft = async (draftRequest) => {
    const response = await client.post('/email/draft', draftRequest);
    return response.data;
};

/**
 * Get draft emails with optional filters
 * @param {string} status - Filter by status (optional)
 * @param {number} limit - Maximum number of drafts to retrieve (default: 50)
 * @returns {Promise<{drafts: Array, count: number}>}
 */
export const getDrafts = async (status = null, limit = 50) => {
    const params = { limit };
    if (status) {
        params.status = status;
    }
    const response = await client.get('/email/drafts', { params });
    return response.data;
};

/**
 * Save a draft to the email provider
 * @param {Object} draftData - Draft data
 * @param {string} draftData.to - Recipient email address
 * @param {string} draftData.subject - Email subject
 * @param {string} draftData.body - Email body content
 * @param {string} draftData.thread_id - Thread ID for replies (optional)
 * @param {string} draftData.in_reply_to - Message ID to reply to (optional)
 * @returns {Promise<{draft_id: string, status: string, provider: string, learning_pair_id: number}>}
 */
export const saveDraft = async (draftData) => {
    const response = await client.post('/email/draft/save', draftData);
    return response.data;
};

/**
 * Learning API
 */
export const getLearningPairs = async () => {
    const response = await client.get('/learning/pairs');
    return response.data;
};

export const matchSentEmails = async () => {
    const response = await client.post('/learning/match-sent-emails');
    return response.data;
};

/**
 * Delete a draft by ID
 * @param {string} draftId - The draft ID to delete
 * @returns {Promise<{message: string}>}
 */
export const deleteDraft = async (draftId) => {
    const response = await client.delete(`/email/draft/${draftId}`);
    return response.data;
};

/**
 * Dashboard API
 */
export const getDashboardStats = async () => {
    const response = await client.get('/dashboard/stats');
    return response.data;
};

export const getEmailStatistics = async (days = 30) => {
    const response = await client.get('/dashboard/email-stats', {
        params: { days }
    });
    return response.data;
};

/**
 * Get recent system activities
 * @param {number} limit - Maximum number of activities to retrieve (default: 10)
 * @returns {Promise<{activities: Array}>}
 */
export const getRecentActivities = async (limit = 10) => {
    const response = await client.get('/statistics/activities', {
        params: { limit }
    });
    return response.data;
};

/**
 * Service Management API
 */

export const getServicesStatus = async () => {
    const response = await client.get('/services/status');
    return response.data;
};

export const getOllamaModels = async () => {
    const response = await client.get('/services/ollama/models');
    return response.data;
};

export const testOllama = async () => {
    const response = await client.post('/services/ollama/test');
    return response.data;
};

export const testChroma = async () => {
    const response = await client.post('/services/chroma/test');
    return response.data;
};

/**
 * Documentation API
 */
export const getDocsTree = async () => {
    const response = await client.get('/docs/');
    return response.data;
};

export const getDocFile = async (filepath) => {
    const response = await client.get(`/docs/${filepath}`);
    return response.data.content; // Backend now returns {content: "markdown string"}
};

/** 
 * RAG Management API
 */

export const getRAGCollections = async () => {
    const response = await client.get('/rag/collections');
    return response.data;
};

export const createRAGCollection = async (name, description = "") => {
    const formData = new FormData();
    formData.append('collection_name', name);
    // Note: description is not currently used in backend but can be extended
    const response = await client.post('/rag/collections', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        }
    });
    return response.data;
};

export const deleteRAGCollection = async (collectionName) => {
    const response = await client.delete(`/rag/collections/${collectionName}`);
    return response.data;
};

export const getRAGCollectionStats = async (collectionName) => {
    const response = await client.get(`/rag/collections/${collectionName}/stats`);
    return response.data;
};

export const resetRAGCollection = async (collectionName) => {
    const response = await client.post(`/rag/collections/${collectionName}/reset`);
    return response.data;
};

export const getCollectionEmbeddingInfo = async (collectionName) => {
    const response = await client.get(`/rag/collections/${collectionName}/embedding-info`);
    return response.data;
};

export const validateUpload = async (collectionName) => {
    const formData = new FormData();
    formData.append('collection_name', collectionName);

    const response = await client.post('/rag/validate-upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        }
    });
    return response.data;
};

export const getRAGDocuments = async (collection, limit = 20, offset = 0) => {
    const response = await client.get(`/rag/collections/${collection}/documents`, {
        params: { limit, offset }
    });
    return response.data;
};

export const deleteRAGDocument = async (docId, collection) => {
    const response = await client.delete('/rag/documents/' + docId, {
        params: { collection_name: collection }
    });
    return response.data;
};

export const uploadRAGDocuments = async (files, collection, chunkSize, chunkOverlap) => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    formData.append('collection_name', collection);
    formData.append('chunk_size', chunkSize.toString());
    formData.append('chunk_overlap', chunkOverlap.toString());

    const response = await client.post('/rag/documents/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        }
    });
    return response.data;
};

export const analyzeDocument = async (contentSample) => {
    const formData = new FormData();
    formData.append('content_sample', contentSample);
    const response = await client.post('/rag/documents/analyze', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        }
    });
    return response.data;
};

export const testRAGQuery = async (query, collection, nResults, advancedMode = false, domain = null) => {
    const formData = new FormData();
    formData.append('query', query);
    formData.append('collection_name', collection);
    formData.append('n_results', nResults.toString());
    formData.append('advanced_mode', advancedMode.toString());  // NEW: Multi-Collection mode
    if (domain) {
        formData.append('domain', domain);  // NEW: Domain-based routing
    }

    const response = await client.post('/rag/query/test', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        }
    });
    return response.data;
};

export const queryWithLLM = async (query, collection, nResults, advancedMode = false, domain = null) => {
    const formData = new FormData();
    formData.append('query', query);
    formData.append('collection_name', collection);
    formData.append('n_results', nResults.toString());
    formData.append('generate_answer', 'true');  // ✅ Enable LLM answer generation
    formData.append('advanced_mode', advancedMode.toString());  // NEW: Multi-Collection mode
    if (domain) {
        formData.append('domain', domain);  // NEW: Domain-based routing
    }

    const response = await client.post('/rag/query/test', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        }
    });
    return response.data;
};

// =============================================
// Statistics & Analytics API Calls
// =============================================

export const getLLMStatistics = async () => {
    const response = await client.get('/statistics/llm');
    return response.data;
};

export const getRAGStatistics = async () => {
    const response = await client.get('/statistics/rag');
    return response.data;
};

export const getPerformanceMetrics = async () => {
    const response = await client.get('/statistics/performance');
    return response.data;
};

export const getEngagementScore = async () => {
    const response = await client.get('/analytics/engagement-score');
    return response.data;
};

export const getConversationStats = async () => {
    const response = await client.get('/analytics/conversation-stats');
    return response.data;
};

export const getDailyEmailCounts = async (days = 30) => {
    const response = await client.get(`/statistics/daily-counts?days=${days}`);
    return response.data;
};

export default client;
