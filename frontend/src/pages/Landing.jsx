import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Shield, Activity, Lock, ArrowRight, CheckCircle } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../hooks/useAuth';
import { Sun, Moon } from 'lucide-react';
import './Landing.css';

const Landing = () => {
  const { theme, toggleTheme } = useTheme();
  const { user } = useAuth();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="landing-page">
      <nav className="landing-nav glass">
        <div className="nav-logo">
          <Shield className="logo-icon" size={28} />
          <span>SecurBank</span>
        </div>
        <div className="nav-links">
          <Link to="/about">About</Link>
          <Link to="/contact">Contact</Link>
          <button className="theme-toggle" onClick={toggleTheme}>
            {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
          </button>
          {user ? (
            <Link to="/dashboard" className="btn btn-primary">Go to Dashboard</Link>
          ) : (
            <>
              <Link to="/login" className="btn btn-outline">Log in</Link>
              <Link to="/signup" className="btn btn-primary">Sign up</Link>
            </>
          )}
        </div>
      </nav>

      <main>
        <section className="hero">
          <div className="hero-background"></div>
          <motion.div 
            className="hero-content"
            initial="hidden"
            animate="visible"
            variants={containerVariants}
          >
            <motion.h1 variants={itemVariants}>
              Advanced Fraud Detection <br/> for Modern Banking
            </motion.h1>
            <motion.p variants={itemVariants} className="hero-subtitle">
              Protect your financial institution with our state-of-the-art machine learning algorithms. Real-time monitoring, deep dataset insights, and intelligent risk assessment.
            </motion.p>
            <motion.div variants={itemVariants} className="hero-actions">
              {user ? (
                <Link to="/dashboard" className="btn btn-primary btn-lg">
                  Go to Dashboard <ArrowRight size={20} />
                </Link>
              ) : (
                <Link to="/signup" className="btn btn-primary btn-lg">
                  Get Started <ArrowRight size={20} />
                </Link>
              )}
              <Link to="/about" className="btn btn-outline btn-lg">
                Learn More
              </Link>
            </motion.div>
          </motion.div>
        </section>

        <section className="features container">
          <div className="section-header">
            <h2>Why Choose SecurBank?</h2>
            <p>Comprehensive protection built on advanced machine learning.</p>
          </div>
          <div className="features-grid">
            <div className="feature-card card glass">
              <div className="feature-icon"><Activity size={24} /></div>
              <h3>Real-Time Monitoring</h3>
              <p>Scan transactions as they happen with instant risk scoring and confidence metrics.</p>
            </div>
            <div className="feature-card card glass">
              <div className="feature-icon"><Shield size={24} /></div>
              <h3>ML-Powered Accuracy</h3>
              <p>Trained on massive datasets using Random Forest, XGBoost, and deep learning techniques.</p>
            </div>
            <div className="feature-card card glass">
              <div className="feature-icon"><Lock size={24} /></div>
              <h3>Secure & Compliant</h3>
              <p>Enterprise-grade security with role-based access control and detailed audit logs.</p>
            </div>
          </div>
        </section>

        <section className="stats">
          <div className="container stats-grid">
            <div className="stat-item">
              <h3>99.8%</h3>
              <p>Detection Accuracy</p>
            </div>
            <div className="stat-item">
              <h3>&lt;50ms</h3>
              <p>Processing Time</p>
            </div>
            <div className="stat-item">
              <h3>24/7</h3>
              <p>Continuous Monitoring</p>
            </div>
          </div>
        </section>
      </main>

      <footer className="landing-footer">
        <div className="container">
          <div className="footer-top">
            <div className="footer-brand">
              <Shield className="logo-icon" size={24} />
              <span>SecurBank</span>
            </div>
            <p>Protecting the future of finance.</p>
          </div>
          <div className="footer-bottom">
            <p>&copy; {new Date().getFullYear()} SecurBank. All rights reserved.</p>
            <div className="footer-links">
              <Link to="/about">About Us</Link>
              <Link to="/contact">Contact</Link>
              <Link to="/privacy">Privacy Policy</Link>
              <Link to="/terms">Terms of Service</Link>
              <Link to="/help">Help Center</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
