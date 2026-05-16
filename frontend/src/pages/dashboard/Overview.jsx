import React, { useState, useEffect } from 'react';
import { ShieldAlert, Activity, CheckCircle, Clock } from 'lucide-react';
import PageTransition from '../../components/layout/PageTransition';
import MetricCard from '../../components/ui/MetricCard';
import api from '../../services/api';

const Overview = () => {
  const [stats, setStats] = useState({
    users: 0,
    analyses: 0,
    model_ready: false
  });

  useEffect(() => {
    // Fetch stats
    api.get('/stats').then(res => {
      setStats(res.data);
    }).catch(err => console.error("Failed to load stats", err));
  }, []);

  return (
    <PageTransition>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.875rem', fontWeight: 700, marginBottom: '0.5rem' }}>Dashboard Overview</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Welcome to your SecurBank control center.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
        <MetricCard 
          title="Total Analyses" 
          value={stats.analyses.toLocaleString()} 
          icon={Activity} 
          trend={12} 
        />
        <MetricCard 
          title="Fraud Detected" 
          value="24" 
          icon={ShieldAlert} 
          color="var(--danger)" 
          trend={-5} 
        />
        <MetricCard 
          title="Avg Risk Score" 
          value="18%" 
          icon={Activity} 
          color="var(--warning)" 
        />
        <MetricCard 
          title="System Status" 
          value={stats.model_ready ? "Online" : "Offline"} 
          icon={stats.model_ready ? CheckCircle : Clock} 
          color={stats.model_ready ? "var(--success)" : "var(--text-muted)"} 
        />
      </div>

      <div className="card glass" style={{ padding: '0' }}>
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Recent Activity</h2>
          <button className="btn btn-outline" style={{ padding: '0.25rem 0.75rem', fontSize: '0.875rem' }}>View All</button>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ backgroundColor: 'var(--bg-secondary)', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Transaction ID</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Date & Time</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Amount</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Risk Score</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {/* Dummy data for now */}
              {[1, 2, 3, 4, 5].map((_, i) => (
                <tr key={i} style={{ borderBottom: '1px solid var(--border-color)', fontSize: '0.9375rem' }}>
                  <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>TXN-{1000 + i}</td>
                  <td style={{ padding: '1rem 1.5rem' }}>Today, 10:{24 + i} AM</td>
                  <td style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Rs {(Math.random() * 5000).toFixed(2)}</td>
                  <td style={{ padding: '1rem 1.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div style={{ width: '60px', height: '6px', backgroundColor: 'var(--bg-secondary)', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{ width: `${Math.random() * 100}%`, height: '100%', backgroundColor: i === 1 ? 'var(--danger)' : 'var(--success)' }}></div>
                      </div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                        {i === 1 ? '89%' : '12%'}
                      </span>
                    </div>
                  </td>
                  <td style={{ padding: '1rem 1.5rem' }}>
                    <span style={{ 
                      padding: '0.25rem 0.5rem', 
                      borderRadius: '9999px', 
                      fontSize: '0.75rem', 
                      fontWeight: 500,
                      backgroundColor: i === 1 ? 'var(--danger-bg)' : 'var(--success-bg)',
                      color: i === 1 ? 'var(--danger)' : 'var(--success)'
                    }}>
                      {i === 1 ? 'Fraud' : 'Legit'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </PageTransition>
  );
};

export default Overview;
