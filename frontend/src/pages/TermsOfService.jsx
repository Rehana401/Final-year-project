import React from 'react';
import { motion } from 'framer-motion';
import { Scale, CheckCircle, AlertTriangle, Info } from 'lucide-react';
import PageTransition from '../components/layout/PageTransition';
import PublicNavbar from '../components/layout/PublicNavbar';
import Footer from '../components/layout/Footer';

const TermsOfService = () => {
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
            <h1 style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: '1rem', color: 'var(--accent)' }}>Terms of Service</h1>
            <p style={{ fontSize: '1.1rem', color: 'var(--text-secondary)' }}>
              Effective Date: May 16, 2026
            </p>
          </motion.div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
            <section className="card glass" style={{ padding: '2rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                <Scale size={28} color="var(--accent)" />
                <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Acceptance of Terms</h2>
              </div>
              <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                By accessing or using SecurBank's services, you agree to be bound by these Terms of Service. If you do not agree to all of these terms, do not use our services. These terms apply to all visitors, users, and others who access or use the service.
              </p>
            </section>

            <section className="card glass" style={{ padding: '2rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                <CheckCircle size={28} color="var(--success)" />
                <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Service Usage</h2>
              </div>
              <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                SecurBank provides a fraud detection simulation and analysis platform. You agree to use the service only for lawful purposes and in a way that does not infringe the rights of, restrict or inhibit anyone else's use and enjoyment of the service.
              </p>
            </section>

            <section className="card glass" style={{ padding: '2rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                <AlertTriangle size={28} color="var(--warning)" />
                <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Disclaimers</h2>
              </div>
              <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                While our ML models are highly accurate, SecurBank provides predictions based on statistical probability. We do not guarantee 100% accuracy in detecting all fraudulent activities and are not liable for decisions made based on system outputs.
              </p>
            </section>

            <section className="card glass" style={{ padding: '2rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
                <Info size={28} color="var(--accent)" />
                <h2 style={{ fontSize: '1.5rem', margin: 0 }}>Changes to Terms</h2>
              </div>
              <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7 }}>
                We reserve the right to modify or replace these terms at any time. If a revision is material, we will try to provide at least 30 days' notice prior to any new terms taking effect. What constitutes a material change will be determined at our sole discretion.
              </p>
            </section>
          </div>
        </div>
      </PageTransition>
      <Footer />
    </div>
  );
};

export default TermsOfService;
