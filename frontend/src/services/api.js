import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// API Service
export const chatAPI = {
  // Create Customer
  createCustomer: (data) => api.post('/customers', data),

  // Send Message
  sendMessage: (data) => api.post('/chat', data),

  // Get Customer List
  getCustomers: (params) => api.get('/customers', { params }),

  // Get Conversation History
  getConversations: (customerId) => api.get(`/conversations/${customerId}`),

  // Get Single Conversation (via conversation_id)
  getConversation: (conversationId) => api.get(`/conversation/${conversationId}`),

  // Customer Classification
  classifyCustomer: (customerId) => api.post(`/classify/${customerId}`),

  // Record Handoff
  recordHandoff: (data) => api.post('/handoff', data),

  // Handoff Management
  getHandoffs: (params) => api.get('/handoffs', { params }),
  sendHumanMessage: (data) => api.post('/messages/human', data),
  updateHandoffStatus: (handoffId, data) => api.put(`/handoffs/${handoffId}/status`, data)
};

export default api;
