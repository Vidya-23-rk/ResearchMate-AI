import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const backendAPI = {
  checkHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  searchPapers: async (query, limit = 40, offset = 0) => {
    const response = await api.get('/papers/search', {
      params: { query, limit, offset }
    });
    return response.data;
  },
  
  summarizeText: async (text) => {
    const response = await api.post('/papers/summarize-text', { text });
    return response.data;
  },

  uploadDocument: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/papers/upload', formData, {
      headers: { 'Content-Type': undefined }
    });
    return response.data;
  },
  
  summarizeDocument: async (documentId) => {
    const response = await api.post(`/papers/documents/${documentId}/summarize`);
    return response.data;
  },

  askQuestion: async (documentId, question) => {
    const response = await api.post(`/papers/documents/${documentId}/ask`, { question });
    return response.data;
  },

  getLibrary: async () => {
    const response = await api.get('/library');
    return response.data;
  },

  // Paper Comparison Matrix
  comparePapers: async (paperIds) => {
    const response = await api.post('/papers/compare', { paper_ids: paperIds });
    return response.data;
  },

  // Research Gap Detection
  detectGaps: async (paperIds) => {
    const response = await api.post('/papers/gaps', { paper_ids: paperIds });
    return response.data;
  },

  // Knowledge Graph data for a paper
  getPaperDetails: async (paperId) => {
    const response = await api.get(`/papers/${paperId}`);
    return response.data;
  },
};

export default api;
