import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// API服务
export const chatAPI = {
  // 创建客户
  createCustomer: (data) => api.post('/customers', data),
  
  // 发送消息
  sendMessage: (data) => api.post('/chat', data),
  
  // 获取客户列表
  getCustomers: (params) => api.get('/customers', { params }),
  
  // 获取对话历史
  getConversations: (customerId) => api.get(`/conversations/${customerId}`),
  
  // 获取单个对话（通过conversation_id）
  getConversation: (conversationId) => api.get(`/conversation/${conversationId}`),
  
  // 客户分类
  classifyCustomer: (customerId) => api.post(`/classify/${customerId}`),
  
  // 记录转人工
  recordHandoff: (data) => api.post('/handoff', data),
  
  // 转人工管理
  getHandoffs: (params) => api.get('/handoffs', { params }),
  sendHumanMessage: (data) => api.post('/messages/human', data),
  updateHandoffStatus: (handoffId, data) => api.put(`/handoffs/${handoffId}/status`, data)
};

export default api;
