import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import {
  SignedIn,
  SignedOut,
  RedirectToSignIn,
  SignIn,
  SignUp,
  UserButton
} from '@clerk/clerk-react';
import './App.css';
import { DemoPage } from './pages/DemoPage';
import { PaymentPage } from './pages/PaymentPage';
import { PortSelectionPage } from './pages/PortSelectionPage';
import { AdminDashboard } from './pages/admin/AdminDashboard';
import { CommonHeader } from './components/CommonHeader';

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <BrowserRouter>
        <CommonHeader />
        <Routes>
          <Route path="/" element={<Navigate to="/pay" replace />} />
          <Route path="/pay" element={<PaymentPage />} />

          <Route
            path="/sign-in/*"
            element={<div style={{ display: 'flex', justifyContent: 'center', padding: '50px' }}><SignIn routing="path" path="/sign-in" /></div>}
          />
          <Route
            path="/sign-up/*"
            element={<div style={{ display: 'flex', justifyContent: 'center', padding: '50px' }}><SignUp routing="path" path="/sign-up" /></div>}
          />

          <Route
            path="/port"
            element={
              <>
                <SignedIn>
                  <PortSelectionPage />
                </SignedIn>
                <SignedOut>
                  <RedirectToSignIn />
                </SignedOut>
              </>
            }
          />
          <Route
            path="/demo"
            element={
              <>
                <SignedIn>
                  <DemoPage />
                </SignedIn>
                <SignedOut>
                  <RedirectToSignIn />
                </SignedOut>
              </>
            }
          />
          <Route
            path="/admin"
            element={
              <>
                <SignedIn>
                  <AdminDashboard />
                </SignedIn>
                <SignedOut>
                  <RedirectToSignIn />
                </SignedOut>
              </>
            }
          />
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
