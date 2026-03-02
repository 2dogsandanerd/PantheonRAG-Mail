import client from './client';

/**
 * Query the RAG Cockpit endpoint for a detailed analysis response.
 * @param {string} query - The user's query.
 * @param {Array<string>} collections - A list of collection names to query.
 * @param {number} k - The number of results to retrieve.
 * @returns {Promise<Object>} The full, detailed response from the QueryService.
 */
export const queryCockpit = async (query, collections, k, llmModel, temperature, systemPrompt, useReranker, rerankTopK, enableExpansion, enableCorrection) => {
  const response = await client.post('/rag/cockpit/query', {
    query,
    collections,
    k,
    llm_model: llmModel,
    temperature,
    system_prompt: systemPrompt,
    use_reranker: useReranker || false,
    rerank_top_k: rerankTopK,
    // Pass new flags via custom headers or extend the endpoint model later.
    // For now, we assume the backend reads these from config, but we can override via query params if we update the endpoint.
    // IMPORTANT: The current /cockpit/query endpoint might not accept expansion flags in body yet.
    // We rely on global config for now, or we update the backend model.
  });
  return response.data;
};

/**
 * Get available RAG collections from the backend.
 * @returns {Promise<Object>} Object containing collections array.
 */
export const getRAGCollections = async () => {
  const response = await client.get('/rag/collections');
  return response.data;
};

/**
 * Get available Ollama models from the backend.
 * @returns {Promise<Object>} Object containing models array.
 */
export const getOllamaModels = async () => {
  const response = await client.get('/services/ollama/models');
  return response.data;
};

// --- Admin Config API (Phase J) ---

export const getSystemConfig = async () => {
  const response = await client.get('/admin/config');
  return response.data;
};

export const updateSystemConfig = async (key, value) => {
  const response = await client.patch('/admin/config', { key, value });
  return response.data;
};

// --- Task Monitor API (Phase G) ---

export const getTaskStatus = async (taskId) => {
  const response = await client.get(`/tasks/${taskId}`);
  return response.data;
};

// --- Ingestion Generators API (Phase 2) ---

/**
 * Generate .ragignore file from folder analysis.
 *
 * @param {string} folderPath - Path to analyze
 * @param {boolean} includeExamples - Include comment examples (default: true)
 * @param {boolean} aggressive - More aggressive exclusions (default: false)
 * @returns {Promise<Object>} Generated .ragignore with statistics
 */
export const generateRagignore = async (folderPath, includeExamples = true, aggressive = false) => {
  try {
    const formData = new FormData();
    formData.append('folder_path', folderPath);
    formData.append('include_examples', includeExamples);
    formData.append('aggressive', aggressive);

    const response = await client.post('/rag/ingestion/generate-ragignore', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    console.error('Error generating .ragignore:', error);
    throw error;
  }
};

/**
 * Save .ragignore file to disk.
 *
 * @param {string} folderPath - Folder where to save .ragignore
 * @param {string} content - .ragignore file content
 * @returns {Promise<Object>} Save result
 */
export const saveRagignore = async (folderPath, content) => {
  try {
    const formData = new FormData();
    formData.append('folder_path', folderPath);
    formData.append('content', content);

    const response = await client.post('/rag/ingestion/save-ragignore', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    console.error('Error saving .ragignore:', error);
    throw error;
  }
};
