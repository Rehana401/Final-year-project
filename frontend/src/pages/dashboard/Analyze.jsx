import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldCheck, ShieldAlert, AlertTriangle, FileText, Activity } from 'lucide-react';
import PageTransition from '../../components/layout/PageTransition';
import ConfidenceGauge from '../../components/charts/ConfidenceGauge';
import ShapChart from '../../components/charts/ShapChart';
import api from '../../services/api';

const ACCOUNT_TYPE_CATEGORIES = ["Savings", "Business", "Checking"];
const TRANSACTION_TYPE_CATEGORIES = ["Transfer", "Bill Payment", "Debit", "Withdrawal", "Credit", "Education", "Shopping"];
const MERCHANT_CATEGORY_CATEGORIES = ["Restaurant", "Groceries", "Entertainment", "Health", "Clothing", "Electronics"];
const DEVICE_TYPE_CATEGORIES = ["POS", "Desktop", "Mobile"];
const TRANSACTION_DEVICE_CATEGORIES = [
  "Self-service Banking Machine", "Wearable Device",
  "Tablet", "Desktop/Laptop", "Voice Assistant",
  "POS Mobile Device", "Banking Chatbot", "Web Browser",
  "Mobile Device", "Payment Gateway Device", "POS Mobile App",
  "Bank Branch", "POS Terminal",
];
const DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

const Analyze = () => {
  const now = new Date();
  const defaultH12 = now.getHours() % 12 || 12;
  const defaultPeriod = now.getHours() < 12 ? 'AM' : 'PM';

  const [formData, setFormData] = useState({
    account_number: '',
    transaction_amount: '25000',
    account_type: 'Savings',
    merchant_category: 'Restaurant',
    device_type: 'POS',
    age: '35',
    customer_email: '',
    account_balance: '50000',
    transaction_type: 'Transfer',
    transaction_device: 'Mobile Device',
    day_name: DAYS_OF_WEEK[now.getDay() === 0 ? 6 : now.getDay() - 1],
    txn_time: `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`,
  });

  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setResult(null);

    // Parse the 24-hour time string from the time input
    const [hourStr, minuteStr] = formData.txn_time.split(':');
    const hour = parseInt(hourStr, 10);
    const minute = minuteStr;
    const period = hour >= 12 ? 'PM' : 'AM';
    const hour12 = hour % 12 || 12;
    
    const dayOfWeek = DAYS_OF_WEEK.indexOf(formData.day_name);
    const timeStr = `${hour12}:${minute} ${period}`;

    const payload = {
      account_number: formData.account_number || 'N/A',
      customer_email: formData.customer_email || 'N/A',
      transaction_amount: formData.transaction_amount,
      account_balance: formData.account_balance,
      age: formData.age,
      account_type: formData.account_type,
      transaction_type: formData.transaction_type,
      merchant_category: formData.merchant_category,
      device_type: formData.device_type,
      transaction_device: formData.transaction_device,
      hour: hour,
      day_of_week: dayOfWeek,
      time: timeStr,
      day_name: formData.day_name,
    };

    try {
      const response = await api.post('/predict/single', payload);
      setResult(response.data.prediction);

      // Save to history
      try {
        await api.post('/history/', {
          transaction_details: response.data.raw_values,
          label: response.data.prediction.label,
          risk_score: response.data.prediction.risk_score,
          confidence: response.data.prediction.confidence,
          shap_values: response.data.prediction.shap_values
        });
      } catch (historyErr) {
        console.error("Failed to save history:", historyErr);
      }
    } catch (err) {
      if (!err.response) {
        setError('Network error: The backend server might be restarting or offline. Please try again.');
      } else {
        setError(err.response?.data?.msg || 'An error occurred during prediction.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <PageTransition>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.875rem', fontWeight: 700, marginBottom: '0.5rem' }}>Analyze Transaction</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Manually enter transaction details for real-time fraud assessment.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: '2rem' }}>
        
        {/* Form Column */}
        <div className="card glass">
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1.5rem' }}>Enter Transaction Details</h2>
          {error && (
            <div style={{ padding: '1rem', backgroundColor: 'var(--danger-bg)', color: 'var(--danger)', borderRadius: 'var(--radius-md)', marginBottom: '1rem' }}>
              {error}
            </div>
          )}
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            
            {/* Row 1: Account Number & Customer Email */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label className="label">Account Number</label>
                <input type="text" name="account_number" className="input-field" placeholder="e.g. 1234567890" value={formData.account_number} onChange={handleChange} />
              </div>
              <div>
                <label className="label">Customer Email</label>
                <input type="text" name="customer_email" className="input-field" placeholder="e.g. user@email.com" value={formData.customer_email} onChange={handleChange} />
              </div>
            </div>

            {/* Row 2: Amount & Balance */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label className="label">Transaction Amount (Rs)</label>
                <input type="number" name="transaction_amount" className="input-field" value={formData.transaction_amount} onChange={handleChange} required min="10" max="99000" step="1" />
              </div>
              <div>
                <label className="label">Account Balance (Rs)</label>
                <input type="number" name="account_balance" className="input-field" value={formData.account_balance} onChange={handleChange} required min="5000" max="100000" step="1" />
              </div>
            </div>

            {/* Row 3: Account Type & Transaction Type */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label className="label">Account Type</label>
                <select name="account_type" className="input-field" value={formData.account_type} onChange={handleChange}>
                  {ACCOUNT_TYPE_CATEGORIES.map(opt => <option key={opt}>{opt}</option>)}
                </select>
              </div>
              <div>
                <label className="label">Transaction Type</label>
                <select name="transaction_type" className="input-field" value={formData.transaction_type} onChange={handleChange}>
                  {TRANSACTION_TYPE_CATEGORIES.map(opt => <option key={opt}>{opt}</option>)}
                </select>
              </div>
            </div>

            {/* Row 4: Merchant Category & Device Type */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label className="label">Merchant Category</label>
                <select name="merchant_category" className="input-field" value={formData.merchant_category} onChange={handleChange}>
                  {MERCHANT_CATEGORY_CATEGORIES.map(opt => <option key={opt}>{opt}</option>)}
                </select>
              </div>
              <div>
                <label className="label">Device Type</label>
                <select name="device_type" className="input-field" value={formData.device_type} onChange={handleChange}>
                  {DEVICE_TYPE_CATEGORIES.map(opt => <option key={opt}>{opt}</option>)}
                </select>
              </div>
            </div>

            {/* Row 5: Transaction Device & Age */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label className="label">Transaction Device</label>
                <select name="transaction_device" className="input-field" value={formData.transaction_device} onChange={handleChange}>
                  {TRANSACTION_DEVICE_CATEGORIES.map(opt => <option key={opt}>{opt}</option>)}
                </select>
              </div>
              <div>
                <label className="label">Customer Age</label>
                <input type="number" name="age" className="input-field" value={formData.age} onChange={handleChange} required min="18" max="70" />
              </div>
            </div>

            {/* Row 6: Day of Week */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label className="label">Day of Week</label>
                <select name="day_name" className="input-field" value={formData.day_name} onChange={handleChange}>
                  {DAYS_OF_WEEK.map(d => <option key={d}>{d}</option>)}
                </select>
              </div>
              <div>
                <label className="label">Transaction Time</label>
                <input 
                  type="time" 
                  name="txn_time" 
                  className="input-field" 
                  value={formData.txn_time} 
                  onChange={handleChange} 
                  required 
                />
              </div>
            </div>

            <button type="submit" className="btn btn-primary" disabled={isLoading} style={{ marginTop: '1rem' }}>
              {isLoading ? 'Analyzing...' : '🔍 Analyze Transaction'}
            </button>
          </form>
        </div>

        {/* Results Column */}
        <div>
          <AnimatePresence mode="wait">
            {result ? (
              <motion.div
                key="result"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.4 }}
                style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}
              >
                {/* Status Card */}
                <div className="card glass" style={{ textAlign: 'center', borderColor: result.label === 'fraud' ? 'var(--danger)' : 'var(--success)' }}>
                  <div style={{ 
                    display: 'inline-flex', 
                    padding: '1rem', 
                    borderRadius: '50%', 
                    backgroundColor: result.label === 'fraud' ? 'var(--danger-bg)' : 'var(--success-bg)',
                    color: result.label === 'fraud' ? 'var(--danger)' : 'var(--success)',
                    marginBottom: '1rem'
                  }}>
                    {result.label === 'fraud' ? <ShieldAlert size={48} /> : <ShieldCheck size={48} />}
                  </div>
                  <h2 style={{ fontSize: '2rem', fontWeight: 800, color: result.label === 'fraud' ? 'var(--danger)' : 'var(--success)', textTransform: 'uppercase', letterSpacing: '2px' }}>
                    {result.label === 'fraud' ? '🚫 FRAUDULENT' : '✅ LEGITIMATE'}
                  </h2>
                  <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem', fontWeight: 500 }}>
                    Confidence: {(result.confidence * 100).toFixed(1)}% | Risk Score: {result.risk_score}/100 ({result.risk_tier})
                  </p>
                </div>

                {result.low_confidence && (
                  <div style={{ padding: '0.75rem 1rem', backgroundColor: 'var(--warning-bg)', color: 'var(--warning)', borderRadius: 'var(--radius-md)', fontWeight: 500 }}>
                    ⚠️ Low confidence prediction — results may not be reliable.
                  </div>
                )}

                {/* Metrics Row */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
                  {[
                    ['Prediction', result.label.toUpperCase()],
                    ['Confidence', `${(result.confidence * 100).toFixed(1)}%`],
                    ['Risk Score', `${result.risk_score}/100`],
                    ['Risk Tier', result.risk_tier],
                  ].map(([label, val]) => (
                    <div key={label} className="card glass" style={{ textAlign: 'center', padding: '1rem' }}>
                      <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>{label}</p>
                      <p style={{ fontSize: '1.125rem', fontWeight: 700 }}>{val}</p>
                    </div>
                  ))}
                </div>

                {/* Confidence Gauge */}
                <div className="card glass" style={{ padding: '1rem' }}>
                  <h3 style={{ fontSize: '1rem', marginBottom: '1rem', textAlign: 'center' }}>Fraud Probability</h3>
                  <ConfidenceGauge score={(result.fraud_probability || 0) * 100} />
                </div>

                {/* Risk Flags */}
                {result.risk_flags && Object.keys(result.risk_flags).length > 0 && (
                  <div className="card glass">
                    <h3 style={{ fontSize: '1.125rem', marginBottom: '1rem' }}>Risk Assessment</h3>
                    {Object.entries(result.risk_flags).map(([feature, info]) => (
                      <div key={feature} style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', fontSize: '0.9375rem' }}>
                        <span>{info.flag}</span>
                        <span><strong>{feature}</strong>: {info.note}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* SHAP Explainer */}
                {result.shap_values && Object.keys(result.shap_values).length > 0 && (
                  <div className="card glass">
                    <h3 style={{ fontSize: '1.125rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <AlertTriangle size={18} color="var(--warning)" /> Feature Importance (SHAP)
                    </h3>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
                      Top features influencing the prediction (→ Fraud | ← Legitimate).
                    </p>
                    <ShapChart shapData={
                      Object.entries(result.shap_values)
                        .map(([feature, importance]) => ({ feature, importance }))
                        .sort((a, b) => Math.abs(b.importance) - Math.abs(a.importance))
                        .slice(0, 15)
                    } />
                  </div>
                )}

                {/* Email Alert (fraud only) */}
                {result.email_alert && (
                  <div className="card" style={{ backgroundColor: '#1a1a2e', color: '#00ff41', fontFamily: 'monospace', borderLeft: '4px solid var(--danger)', padding: '1.5rem' }}>
                    <h3 style={{ fontSize: '1rem', color: '#fff', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <FileText size={18} /> 📧 Email Alert Simulation
                    </h3>
                    <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.85rem', lineHeight: 1.6, margin: 0 }}>
                      {result.email_alert}
                    </pre>
                  </div>
                )}

              </motion.div>
            ) : (
              <motion.div 
                key="empty"
                className="card glass"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', minHeight: '500px' }}
              >
                <Activity size={64} style={{ marginBottom: '1.5rem', opacity: 0.5 }} />
                <h3>Awaiting Analysis</h3>
                <p style={{ textAlign: 'center', maxWidth: '300px', marginTop: '0.5rem' }}>
                  Fill in the transaction details and click "Analyze Transaction" to check for fraud.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </PageTransition>
  );
};

export default Analyze;
