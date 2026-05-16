import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Shield, AlertCircle } from 'lucide-react';
import api from '../services/api';
import './Auth.css';

const Signup = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const getPasswordStrength = (pass) => {
    let strength = 0;
    if (pass.length > 5) strength += 25;
    if (pass.length > 8) strength += 25;
    if (/[A-Z]/.test(pass)) strength += 25;
    if (/[0-9]/.test(pass)) strength += 25;
    return strength;
  };

  const strength = getPasswordStrength(formData.password);
  let strengthColor = 'var(--border-color)';
  if (strength > 0) strengthColor = 'var(--danger)';
  if (strength >= 50) strengthColor = 'var(--warning)';
  if (strength >= 75) strengthColor = 'var(--success)';

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.id]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setIsLoading(true);

    try {
      await api.post('/auth/signup', { 
        username: formData.username,
        email: formData.email, 
        password: formData.password 
      });
      navigate('/login', { state: { message: 'Account created! Please log in.' } });
    } catch (err) {
      setError(err.response?.data?.msg || 'Failed to create account.');
    } finally {
      setIsLoading(false);
    }
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
            <h2>Create Account</h2>
            <p>Join SecurBank today</p>
          </div>

          {error && (
            <motion.div 
              className="auth-error"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <AlertCircle size={18} />
              <span>{error}</span>
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label className="label" htmlFor="username">Username</label>
              <input 
                type="text" 
                id="username" 
                className="input-field" 
                placeholder="johndoe"
                value={formData.username}
                onChange={handleChange}
                required 
              />
            </div>

            <div className="form-group">
              <label className="label" htmlFor="email">Email</label>
              <input 
                type="email" 
                id="email" 
                className="input-field" 
                placeholder="john@example.com"
                value={formData.email}
                onChange={handleChange}
                required 
              />
            </div>
            
            <div className="form-group">
              <label className="label" htmlFor="password">Password</label>
              <input 
                type="password" 
                id="password" 
                className="input-field" 
                placeholder="Min 6 characters"
                value={formData.password}
                onChange={handleChange}
                required 
              />
              <div className="password-strength">
                <div className="strength-bar">
                  <div 
                    className="strength-fill" 
                    style={{ width: `${strength}%`, backgroundColor: strengthColor }}
                  ></div>
                </div>
              </div>
            </div>

            <div className="form-group">
              <label className="label" htmlFor="confirmPassword">Confirm Password</label>
              <input 
                type="password" 
                id="confirmPassword" 
                className="input-field" 
                placeholder="Repeat password"
                value={formData.confirmPassword}
                onChange={handleChange}
                required 
              />
            </div>

            <button type="submit" className="btn btn-primary btn-block" disabled={isLoading} style={{ marginTop: '1rem' }}>
              {isLoading ? 'Creating Account...' : 'Sign Up'}
            </button>
          </form>

          <div className="auth-footer">
            <p>Already have an account? <Link to="/login">Sign in</Link></p>
            <Link to="/" className="back-link">Back to Home</Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Signup;
