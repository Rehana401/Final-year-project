import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Mail, Phone, MapPin, Send } from 'lucide-react';
import PageTransition from '../components/layout/PageTransition';
import PublicNavbar from '../components/layout/PublicNavbar';
import Footer from '../components/layout/Footer';

const Contact = () => {
  const [formData, setFormData] = useState({ name: '', email: '', subject: '', message: '' });
  const [status, setStatus] = useState('idle');

  const handleSubmit = (e) => {
    e.preventDefault();
    setStatus('sending');
    setTimeout(() => {
      setStatus('sent');
      setFormData({ name: '', email: '', subject: '', message: '' });
      setTimeout(() => setStatus('idle'), 3000);
    }, 1500);
  };

  const handleChange = (e) => setFormData({ ...formData, [e.target.id]: e.target.value });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <PublicNavbar />
      <PageTransition>
        <div className="container" style={{ maxWidth: '1000px', margin: '0 auto', padding: '4rem 0' }}>
          <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
            <h1 style={{ fontSize: '3rem', fontWeight: 800, marginBottom: '1rem' }}>Get in Touch</h1>
            <p style={{ fontSize: '1.1rem', color: 'var(--text-secondary)' }}>Have questions about SecurBank? We're here to help.</p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '4rem' }}>
            
            {/* Contact Info */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
              <div className="card glass" style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', padding: '1.5rem' }}>
                <div style={{ backgroundColor: 'var(--accent-light)', padding: '1rem', borderRadius: '50%', color: 'var(--accent)' }}>
                  <Mail size={24} />
                </div>
                <div>
                  <h3 style={{ marginBottom: '0.25rem' }}>Email Us</h3>
                  <p style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>For general inquiries and support.</p>
                  <a href="mailto:support@securbank.com" style={{ fontWeight: 600 }}>support@securbank.com</a>
                </div>
              </div>

              <div className="card glass" style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', padding: '1.5rem' }}>
                <div style={{ backgroundColor: 'var(--accent-light)', padding: '1rem', borderRadius: '50%', color: 'var(--accent)' }}>
                  <Phone size={24} />
                </div>
                <div>
                  <h3 style={{ marginBottom: '0.25rem' }}>Call Us</h3>
                  <p style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Mon-Fri from 9am to 6pm.</p>
                  <a href="tel:+1234567890" style={{ fontWeight: 600 }}>+1 (234) 567-890</a>
                </div>
              </div>

              <div className="card glass" style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', padding: '1.5rem' }}>
                <div style={{ backgroundColor: 'var(--accent-light)', padding: '1rem', borderRadius: '50%', color: 'var(--accent)' }}>
                  <MapPin size={24} />
                </div>
                <div>
                  <h3 style={{ marginBottom: '0.25rem' }}>Visit Us</h3>
                  <p style={{ color: 'var(--text-secondary)' }}>University Campus,<br/>Computer Science Dept.</p>
                </div>
              </div>
            </div>

            {/* Contact Form */}
            <motion.div 
              className="card glass"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <h2 style={{ marginBottom: '1.5rem' }}>Send a Message</h2>
              <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <div>
                  <label className="label" htmlFor="name">Name</label>
                  <input type="text" id="name" className="input-field" value={formData.name} onChange={handleChange} required />
                </div>
                <div>
                  <label className="label" htmlFor="email">Email</label>
                  <input type="email" id="email" className="input-field" value={formData.email} onChange={handleChange} required />
                </div>
                <div>
                  <label className="label" htmlFor="subject">Subject</label>
                  <input type="text" id="subject" className="input-field" value={formData.subject} onChange={handleChange} required />
                </div>
                <div>
                  <label className="label" htmlFor="message">Message</label>
                  <textarea 
                    id="message" 
                    className="input-field" 
                    rows="5" 
                    value={formData.message} 
                    onChange={handleChange} 
                    required 
                    style={{ resize: 'vertical' }}
                  ></textarea>
                </div>
                <button 
                  type="submit" 
                  className={`btn ${status === 'sent' ? 'btn-outline' : 'btn-primary'}`} 
                  disabled={status !== 'idle'}
                  style={{ marginTop: '0.5rem', backgroundColor: status === 'sent' ? 'var(--success)' : '', color: status === 'sent' ? 'white' : '', borderColor: status === 'sent' ? 'var(--success)' : '' }}
                >
                  {status === 'sending' ? 'Sending...' : status === 'sent' ? 'Message Sent!' : <><Send size={18} /> Send Message</>}
                </button>
              </form>
            </motion.div>
          </div>
        </div>
      </PageTransition>
      <Footer />
    </div>
  );
};

export default Contact;
