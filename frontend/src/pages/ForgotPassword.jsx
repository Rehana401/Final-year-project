import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Shield, CheckCircle, AlertCircle } from 'lucide-react';
import api from '../services/api';
import './Auth.css';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState('idle'); // idle, loading, success, error
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('loading');
    
    // In a real app we'd call the API here
    // await api.post('/auth/forgot-password', { email });
    
    // Simulate API call for the demo
    setTimeout(() => {
      setStatus('success');
      setMessage(`If an account exists for ${email}, a password reset link has been sent.`);
    }, 1500);
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <motion.div 
          className="auth-card card glass"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div className="auth-header">
            <Shield className="logo-icon" size={40} />
            <h2>Reset Password</h2>
            <p>Enter your email to receive a reset link</p>
          </div>

          {status === 'success' ? (
            <motion.div 
              className="auth-success"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              style={{ textAlign: 'center', padding: '1rem', backgroundColor: 'var(--success-bg)', color: 'var(--success)', borderRadius: 'var(--radius-md)' }}
            >
              <CheckCircle size={48} style={{ margin: '0 auto 1rem' }} />
              <p style={{ fontWeight: 500 }}>{message}</p>
            </motion.div>
          ) : (
            <form onSubmit={handleSubmit} className="auth-form">
              <div className="form-group">
                <label className="label" htmlFor="email">Email</label>
                <input 
                  type="email" 
                  id="email" 
                  className="input-field" 
                  placeholder="Enter your registered email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required 
                />
              </div>

              <button type="submit" className="btn btn-primary btn-block" disabled={status === 'loading'} style={{ marginTop: '0.5rem' }}>
                {status === 'loading' ? 'Sending...' : 'Send Reset Link'}
              </button>
            </form>
          )}

          <div className="auth-footer">
            <p>Remembered your password? <Link to="/login">Sign in</Link></p>
            <Link to="/" className="back-link">Back to Home</Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default ForgotPassword;
