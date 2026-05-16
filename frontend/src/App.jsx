import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute, AdminRoute } from './components/auth/ProtectedRoute';

import Sidebar from './components/layout/Sidebar';
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';

// Public pages
import Landing from './pages/Landing';
import Login from './pages/Login';
import Signup from './pages/Signup';
import ForgotPassword from './pages/ForgotPassword';
import About from './pages/About';
import Contact from './pages/Contact';
import PrivacyPolicy from './pages/PrivacyPolicy';
import TermsOfService from './pages/TermsOfService';
import HelpCenter from './pages/HelpCenter';

// User dashboard
import Overview from './pages/dashboard/Overview';
import Analyze from './pages/dashboard/Analyze';
import Monitor from './pages/dashboard/Monitor';
import Batch from './pages/dashboard/Batch';
import History from './pages/dashboard/History';

// Admin pages
import Insights from './pages/admin/Insights';
import Training from './pages/admin/Training';
import ManageUsers from './pages/admin/ManageUsers';

// Shared pages
import Profile from './pages/Profile';
import Settings from './pages/Settings';

const DashboardLayout = () => (
  <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--bg-primary)' }}>
    <Sidebar />
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minWidth: 0 }}>
      <Navbar />
      <main style={{ flex: 1, overflowY: 'auto', padding: '2rem' }}>
        <AnimatePresence mode="wait">
          {/* Outlet rendered via nested routes — children passed as props from React Router */}
        </AnimatePresence>
      </main>
      <Footer />
    </div>
  </div>
);

// Inline layout wrapper to avoid Outlet confusion
const AppShell = ({ children }) => (
  <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--bg-primary)' }}>
    <Sidebar />
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minWidth: 0 }}>
      <Navbar />
      <main style={{ flex: 1, overflowY: 'auto' }}>
        <AnimatePresence mode="wait">
          {children}
        </AnimatePresence>
      </main>
      <Footer />
    </div>
  </div>
);

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <Routes>
            {/* ── Public ── */}
            <Route path="/"                element={<Landing />} />
            <Route path="/login"           element={<Login />} />
            <Route path="/signup"          element={<Signup />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/about"           element={<About />} />
            <Route path="/contact"         element={<Contact />} />
            <Route path="/privacy"         element={<PrivacyPolicy />} />
            <Route path="/terms"           element={<TermsOfService />} />
            <Route path="/help"            element={<HelpCenter />} />

            {/* ── Protected (User) ── */}
            <Route element={<ProtectedRoute />}>
              <Route path="/dashboard" element={<AppShell><Overview /></AppShell>} />
              <Route path="/dashboard/analyze" element={<AppShell><Analyze /></AppShell>} />
              <Route path="/dashboard/monitor" element={<AppShell><Monitor /></AppShell>} />
              <Route path="/dashboard/batch"   element={<AppShell><Batch /></AppShell>} />
              <Route path="/dashboard/history" element={<AppShell><History /></AppShell>} />
              <Route path="/profile"   element={<AppShell><Profile /></AppShell>} />
              <Route path="/settings"  element={<AppShell><Settings /></AppShell>} />

              {/* ── Protected (Admin) ── */}
              <Route element={<AdminRoute />}>
                <Route path="/admin/insights" element={<AppShell><Insights /></AppShell>} />
                <Route path="/admin/training" element={<AppShell><Training /></AppShell>} />
                <Route path="/admin/users"    element={<AppShell><ManageUsers /></AppShell>} />
              </Route>
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;

