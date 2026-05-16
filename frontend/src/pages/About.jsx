import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Shield, Brain, Server, Check } from 'lucide-react';
import PageTransition from '../components/layout/PageTransition';
import PublicNavbar from '../components/layout/PublicNavbar';
import Footer from '../components/layout/Footer';

const About = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <PublicNavbar />
      <PageTransition>
        <div className="container" style={{ maxWidth: '800px', margin: '0 auto', padding: '4rem 0' }}>
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
            style={{ marginBottom: '4rem', textAlign: 'center' }}
          >
            <h1 style={{ fontSize: '3rem', fontWeight: 800, marginBottom: '1rem', color: 'var(--accent)' }}>About SecurBank</h1>
            <p style={{ fontSize: '1.25rem', color: 'var(--text-secondary)' }}>
              Pioneering the future of financial security through advanced machine learning.
            </p>
          </motion.div>

          <section style={{ marginBottom: '4rem' }}>
            <h2 style={{ fontSize: '1.75rem', marginBottom: '1rem' }}>Our Mission</h2>
            <p style={{ fontSize: '1.1rem', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
              SecurBank was founded as an academic project with a clear goal: to build a robust, 
              scalable, and highly accurate fraud detection system for online banking. By leveraging 
              state-of-the-art machine learning algorithms, we aim to protect financial institutions 
              and their customers from increasingly sophisticated cyber threats.
            </p>
          </section>

          <section style={{ marginBottom: '4rem' }}>
            <h2 style={{ fontSize: '1.75rem', marginBottom: '2rem' }}>How It Works</h2>
            <div style={{ display: 'grid', gap: '2rem', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
              <div className="card glass">
                <Server size={32} color="var(--accent)" style={{ marginBottom: '1rem' }} />
                <h3 style={{ marginBottom: '0.5rem' }}>Data Processing</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                  Raw transaction data is ingested and cleaned. Missing values are imputed and categorical features are one-hot and frequency encoded.
                </p>
              </div>
              <div className="card glass">
                <Brain size={32} color="var(--warning)" style={{ marginBottom: '1rem' }} />
                <h3 style={{ marginBottom: '0.5rem' }}>Machine Learning</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                  An ensemble of models including Random Forest and XGBoost evaluate the transaction against historical fraud patterns.
                </p>
              </div>
              <div className="card glass">
                <Shield size={32} color="var(--success)" style={{ marginBottom: '1rem' }} />
                <h3 style={{ marginBottom: '0.5rem' }}>Risk Assessment</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                  A final risk score and confidence metric is generated. High-risk transactions trigger simulated alerts and are flagged for review.
                </p>
              </div>
            </div>
          </section>

          <section style={{ marginBottom: '4rem' }}>
            <h2 style={{ fontSize: '1.75rem', marginBottom: '1rem' }}>Technology Stack</h2>
            <ul style={{ listStyle: 'none', padding: 0, display: 'grid', gap: '1rem', gridTemplateColumns: '1fr 1fr' }}>
              {[
                "React 19 & Vite (Frontend)",
                "Flask & REST API (Backend)",
                "Scikit-Learn & XGBoost (ML Models)",
                "SHAP (Explainable AI)",
                "SQLite (Database)",
                "ReportLab (PDF Generation)"
              ].map((tech, i) => (
                <li key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'var(--text-secondary)' }}>
                  <div style={{ backgroundColor: 'var(--success-bg)', borderRadius: '50%', padding: '0.2rem' }}>
                    <Check size={16} color="var(--success)" />
                  </div>
                  {tech}
                </li>
              ))}
            </ul>
          </section>

          <div style={{ textAlign: 'center', marginTop: '4rem' }}>
            <Link to="/signup" className="btn btn-primary btn-lg">Join SecurBank Today</Link>
          </div>
        </div>
      </PageTransition>
      <Footer />
    </div>
  );
};

export default About;
