import React from 'react';
import { motion } from 'framer-motion';
import { HelpCircle, Search, Book, MessageSquare, Mail } from 'lucide-react';
import PageTransition from '../components/layout/PageTransition';
import PublicNavbar from '../components/layout/PublicNavbar';
import Footer from '../components/layout/Footer';

const HelpCenter = () => {
  const faqs = [
    {
      q: "How does the fraud detection system work?",
      a: "Our system uses an ensemble of machine learning models (Random Forest and XGBoost) to analyze transaction patterns against historical fraud data, assigning a risk score and confidence level to every transaction."
    },
    {
      q: "What should I do if a transaction is flagged as fraud?",
      a: "Flagged transactions should be reviewed immediately. You can view detailed feature importance (SHAP) to understand why the model flagged the transaction and then take appropriate action like blocking the card or contacting the user."
    },
    {
      q: "Can I upload multiple transactions at once?",
      a: "Yes! Use the 'Batch Analysis' feature in your dashboard to upload a CSV file containing multiple transactions for bulk processing and reporting."
    },
    {
      q: "Is my transaction data safe?",
      a: "Absolutely. We use enterprise-grade encryption and secure database practices to ensure that all data processed through our system is protected and only accessible by authorized users."
    }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <PublicNavbar />
      <PageTransition>
        <div className="container" style={{ maxWidth: '1000px', margin: '0 auto', padding: '4rem 2rem' }}>
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            style={{ marginBottom: '4rem', textAlign: 'center' }}
          >
            <h1 style={{ fontSize: '3rem', fontWeight: 800, marginBottom: '1.5rem', color: 'var(--accent)' }}>Help Center</h1>
            <p style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto' }}>
              Everything you need to know about using SecurBank to protect your financial operations.
            </p>
            
            <div style={{ position: 'relative', maxWidth: '600px', margin: '2.5rem auto 0' }}>
              <Search size={20} style={{ position: 'absolute', left: '1.25rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input 
                type="text" 
                placeholder="Search for help articles..." 
                className="input-field" 
                style={{ paddingLeft: '3.5rem', height: '3.5rem', fontSize: '1.1rem', borderRadius: 'var(--radius-lg)' }}
              />
            </div>
          </motion.div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', marginBottom: '5rem' }}>
            <div className="card glass" style={{ padding: '2rem', textAlign: 'center' }}>
              <Book size={40} color="var(--accent)" style={{ margin: '0 auto 1.5rem' }} />
              <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Documentation</h2>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>Explore our detailed guides on ML models, data formats, and system integration.</p>
              <button className="btn btn-outline" style={{ width: '100%' }}>Read Docs</button>
            </div>
            <div className="card glass" style={{ padding: '2rem', textAlign: 'center' }}>
              <MessageSquare size={40} color="var(--success)" style={{ margin: '0 auto 1.5rem' }} />
              <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Community Support</h2>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>Connect with other users and developers to share best practices and insights.</p>
              <button className="btn btn-outline" style={{ width: '100%' }}>Join Forum</button>
            </div>
            <div className="card glass" style={{ padding: '2rem', textAlign: 'center' }}>
              <Mail size={40} color="var(--warning)" style={{ margin: '0 auto 1.5rem' }} />
              <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Direct Support</h2>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>Can't find what you're looking for? Our support team is here to help you 24/7.</p>
              <button className="btn btn-outline" style={{ width: '100%' }}>Contact Us</button>
            </div>
          </div>

          <section>
            <h2 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '2.5rem', textAlign: 'center', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem' }}>
              <HelpCircle color="var(--accent)" /> Frequently Asked Questions
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {faqs.map((faq, i) => (
                <div key={i} className="card glass" style={{ padding: '1.5rem 2rem' }}>
                  <h3 style={{ fontSize: '1.125rem', marginBottom: '0.75rem', fontWeight: 600 }}>{faq.q}</h3>
                  <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>{faq.a}</p>
                </div>
              ))}
            </div>
          </section>
        </div>
      </PageTransition>
      <Footer />
    </div>
  );
};

export default HelpCenter;
