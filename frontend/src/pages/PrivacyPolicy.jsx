import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Lock, Eye, FileText } from 'lucide-react';
import PageTransition from '../components/layout/PageTransition';
import PublicNavbar from '../components/layout/PublicNavbar';
import Footer from '../components/layout/Footer';

const PrivacyPolicy = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <PublicNavbar />
      <PageTransition>
        <div className="container" style={{ maxWidth: '800px', margin: '0 auto', padding: '4rem 2rem' }}>
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            style={{ marginBottom: '3rem', textAlign: 'center' }}
          >
            <h1 style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: '1rem', color: 'var(--accent)' }}>Privacy Policy</h1>
            <p style={{ fontSize: '1.1rem', color: 'var(--text-secondary)' }}>
              Last updated: May 16, 2026
            </p>
          </motion.div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
            <section className="card glass" style={{ padding: '2rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                <Shield size={28} color="var(--accent)" />
                <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Introduction</h2>
              </div>
              <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                At SecurBank, we take your privacy seriously. This policy describes how we collect, use, and protect your personal data when you use our fraud detection services. As a project focused on banking security, protecting information is at the core of what we do.
              </p>
            </section>

            <section className="card glass" style={{ padding: '2rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                <Eye size={28} color="var(--warning)" />
                <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Information We Collect</h2>
              </div>
              <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: '1rem' }}>
                To provide our fraud detection services, we may collect:
              </p>
              <ul style={{ color: 'var(--text-secondary)', lineHeight: 1.7, paddingLeft: '1.5rem' }}>
                <li>Account details (email, account numbers)</li>
                <li>Transaction metadata (amounts, categories, types)</li>
                <li>Technical data (device types, browser information)</li>
                <li>Demographic data used for risk modeling (age)</li>
              </ul>
            </section>

            <section className="card glass" style={{ padding: '2rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                <Lock size={28} color="var(--success)" />
                <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Data Security</h2>
              </div>
              <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                We implement enterprise-grade security measures to protect your data. All transaction analyses are encrypted, and we use industry-standard protocols to ensure that your sensitive financial information remains confidential and secure from unauthorized access.
              </p>
            </section>

            <section className="card glass" style={{ padding: '2rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                <FileText size={28} color="var(--accent)" />
                <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Your Rights</h2>
              </div>
              <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                You have the right to access, update, or delete your personal information at any time. You can manage these settings through your profile dashboard or by contacting our support team if you have specific requests regarding your data portability.
              </p>
            </section>
          </div>
        </div>
      </PageTransition>
      <Footer />
    </div>
  );
};

export default PrivacyPolicy;
