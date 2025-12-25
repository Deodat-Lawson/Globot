import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import ChatWidget from './components/ChatWidget/ChatWidget';
import CustomerList from './components/Admin/CustomerList';
import ConversationDetail from './components/Admin/ConversationDetail';
import HandoffQueue from './components/Admin/HandoffQueue';
import HandoffDetail from './components/Admin/HandoffDetail';
import './App.css';

function App() {
  // 判断是客户端还是管理端
  const isAdminPath = window.location.pathname.startsWith('/admin');

  return (
    <ConfigProvider locale={zhCN}>
      <BrowserRouter>
        <Routes>
          {/* 客户端 - Chat Widget */}
          <Route path="/" element={
            <div className="customer-page">
              <div className="hero-section">
                <h1>DJI 工业级无人机</h1>
                <p>专业的解决方案，为您的业务赋能</p>
              </div>
              <ChatWidget />
            </div>
          } />

          {/* 管理后台 */}
          <Route path="/admin" element={<Navigate to="/admin/customers" replace />} />
          <Route path="/admin/customers" element={
            <div className="admin-layout">
              <div className="admin-header">
                <h2>DJI Sales AI Assistant - 管理后台</h2>
              </div>
              <CustomerList />
            </div>
          } />
          <Route path="/admin/conversations/:customerId" element={
            <div className="admin-layout">
              <div className="admin-header">
                <h2>DJI Sales AI Assistant - 对话详情</h2>
              </div>
              <ConversationDetail />
            </div>
          } />
          
          {/* 转人工队列 */}
          <Route path="/admin/handoffs" element={
            <div className="admin-layout">
              <div className="admin-header">
                <h2>DJI Sales AI Assistant - 转人工队列</h2>
              </div>
              <HandoffQueue />
            </div>
          } />
          <Route path="/admin/handoff/:handoffId" element={
            <div className="admin-layout">
              <div className="admin-header">
                <h2>DJI Sales AI Assistant - 人工处理</h2>
              </div>
              <HandoffDetail />
            </div>
          } />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
