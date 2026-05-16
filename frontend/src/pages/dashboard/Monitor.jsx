import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Square, Settings, ShieldAlert, ShieldCheck } from 'lucide-react';
import PageTransition from '../../components/layout/PageTransition';

const Monitor = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [speedMs, setSpeedMs] = useState(2000);
  const [transactions, setTransactions] = useState([]);
  const [stats, setStats] = useState({ total: 0, fraud: 0 });
  const intervalRef = useRef(null);

  const generateRandomTransaction = () => {
    const isFraud = Math.random() > 0.85; // 15% fraud rate for demo
    return {
      id: `TXN-${Math.floor(Math.random() * 100000)}`,
      amount: (Math.random() * 5000).toFixed(2),
      type: Math.random() > 0.5 ? 'Debit' : 'Credit',
      risk_score: isFraud ? (Math.random() * 30 + 70).toFixed(1) : (Math.random() * 40).toFixed(1),
      label: isFraud ? 'fraud' : 'legit',
      timestamp: new Date().toLocaleTimeString()
    };
  };

  useEffect(() => {
    if (isRunning) {
      intervalRef.current = setInterval(() => {
        const newTxn = generateRandomTransaction();
        setTransactions(prev => [newTxn, ...prev].slice(0, 10)); // keep last 10
        setStats(prev => ({
          total: prev.total + 1,
          fraud: prev.fraud + (newTxn.label === 'fraud' ? 1 : 0)
        }));
      }, speedMs);
    } else {
      clearInterval(intervalRef.current);
    }
    return () => clearInterval(intervalRef.current);
  }, [isRunning, speedMs]);

  const toggleRun = () => setIsRunning(!isRunning);

  const fraudRate = stats.total > 0 ? ((stats.fraud / stats.total) * 100).toFixed(1) : 0;

  return (
    <PageTransition>
      <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h1 style={{ fontSize: '1.875rem', fontWeight: 700, marginBottom: '0.5rem' }}>Real-Time Monitor</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Live simulation of incoming transaction stream analysis.</p>
        </div>
        
        <div className="card glass" style={{ display: 'flex', gap: '1rem', padding: '1rem', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <label style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Speed:</label>
            <select className="input-field" value={speedMs} onChange={(e) => setSpeedMs(Number(e.target.value))} style={{ width: '120px', padding: '0.5rem' }} disabled={isRunning}>
              <option value={5000}>Slow (5s)</option>
              <option value={2000}>Normal (2s)</option>
              <option value={500}>Fast (0.5s)</option>
            </select>
          </div>
          <button 
            onClick={toggleRun} 
            className={`btn ${isRunning ? 'btn-outline' : 'btn-primary'}`}
            style={{ minWidth: '100px' }}
          >
            {isRunning ? <><Square size={16} fill="currentColor" /> Stop</> : <><Play size={16} fill="currentColor" /> Start</>}
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="card glass">
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Transactions Scanned</p>
          <h3 style={{ fontSize: '2rem', fontWeight: 800 }}>{stats.total}</h3>
        </div>
        <div className="card glass" style={{ borderBottom: stats.fraud > 0 ? '3px solid var(--danger)' : '' }}>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Fraud Flags</p>
          <h3 style={{ fontSize: '2rem', fontWeight: 800, color: stats.fraud > 0 ? 'var(--danger)' : 'var(--text-primary)' }}>{stats.fraud}</h3>
        </div>
        <div className="card glass">
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Current Fraud Rate</p>
          <h3 style={{ fontSize: '2rem', fontWeight: 800 }}>{fraudRate}%</h3>
        </div>
      </div>

      <div className="card glass" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', backgroundColor: 'var(--bg-secondary)', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: isRunning ? 'var(--success)' : 'var(--text-muted)', boxShadow: isRunning ? '0 0 10px var(--success)' : 'none' }}></div>
          <span style={{ fontWeight: 600 }}>Live Feed {isRunning ? '(Active)' : '(Paused)'}</span>
        </div>
        
        <div style={{ minHeight: '400px', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', backgroundColor: '#0f172a' }}>
          <AnimatePresence>
            {transactions.map((txn) => (
              <motion.div
                key={txn.id}
                initial={{ opacity: 0, y: -20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.3 }}
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1.5fr 1fr 1fr 1fr',
                  padding: '1rem 1.5rem',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: txn.label === 'fraud' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(30, 41, 59, 0.8)',
                  borderLeft: `4px solid ${txn.label === 'fraud' ? '#ef4444' : '#10b981'}`,
                  color: '#f8fafc',
                  alignItems: 'center'
                }}
              >
                <div style={{ fontFamily: 'monospace' }}>{txn.id}</div>
                <div>{txn.timestamp}</div>
                <div style={{ fontWeight: 600 }}>Rs {txn.amount}</div>
                <div>Risk: {txn.risk_score}%</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: txn.label === 'fraud' ? '#ef4444' : '#10b981', fontWeight: 700, textTransform: 'uppercase' }}>
                  {txn.label === 'fraud' ? <ShieldAlert size={18} /> : <ShieldCheck size={18} />}
                  {txn.label}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          
          {transactions.length === 0 && (
            <div style={{ textAlign: 'center', color: '#64748b', marginTop: '4rem' }}>
              <Settings size={48} style={{ opacity: 0.5, marginBottom: '1rem' }} />
              <p>Feed is empty. Click Start to begin simulation.</p>
            </div>
          )}
        </div>
      </div>
    </PageTransition>
  );
};

export default Monitor;
