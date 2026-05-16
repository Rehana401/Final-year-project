import React, { useState, useEffect } from 'react';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Database, AlertTriangle, CheckCircle, TrendingUp } from 'lucide-react';
import PageTransition from '../../components/layout/PageTransition';
import MetricCard from '../../components/ui/MetricCard';
import api from '../../services/api';

const COLORS = ['var(--success)', 'var(--danger)', 'var(--warning)', 'var(--accent)'];

const Insights = () => {
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/admin/dataset/info')
      .then(res => setInfo(res.data.info))
      .catch(err => setError(err.response?.data?.msg || 'Failed to load dataset info.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <PageTransition><div style={{ color: 'var(--text-secondary)', padding: '2rem' }}>Loading dataset insights...</div></PageTransition>;
  if (error) return <PageTransition><div style={{ color: 'var(--danger)', padding: '2rem' }}>{error}</div></PageTransition>;

  // Build chart data from info
  const labelDist = info?.label_distribution || {};
  const fraudPieData = Object.entries(labelDist).map(([key, val]) => ({
    name: key === '0' ? 'Legit' : 'Fraud',
    value: val
  }));

  const categoricalData = Object.entries(info?.categorical_unique || {}).map(([key, val]) => ({
    feature: key,
    unique: val
  })).slice(0, 10);

  return (
    <PageTransition>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.875rem', fontWeight: 700, marginBottom: '0.5rem' }}>Dataset Insights</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Comprehensive statistics and distribution analysis of the training dataset.</p>
      </div>

      {/* Overview Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2.5rem' }}>
        <MetricCard title="Total Records" value={(info?.rows || 0).toLocaleString()} icon={Database} />
        <MetricCard title="Features" value={info?.columns || 0} icon={TrendingUp} color="var(--warning)" />
        <MetricCard title="Missing Values" value={info?.total_missing || 0} icon={AlertTriangle} color="var(--warning)" />
        <MetricCard
          title="Fraud Rate"
          value={`${((labelDist[1] || 0) / (info?.rows || 1) * 100).toFixed(2)}%`}
          icon={AlertTriangle}
          color="var(--danger)"
        />
      </div>

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>

        {/* Label Distribution Pie */}
        <div className="card glass">
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1.5rem' }}>Class Distribution</h2>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={fraudPieData} cx="50%" cy="50%" outerRadius={90} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}>
                {fraudPieData.map((_, i) => <Cell key={i} fill={i === 0 ? 'var(--success)' : 'var(--danger)'} />)}
              </Pie>
              <Tooltip formatter={(val) => val.toLocaleString()} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Categorical Feature Unique Counts */}
        <div className="card glass">
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1.5rem' }}>Categorical Feature Diversity</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={categoricalData} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" horizontal={false} />
              <XAxis type="number" stroke="var(--text-muted)" tick={{ fontSize: 11 }} />
              <YAxis dataKey="feature" type="category" width={110} stroke="var(--text-secondary)" tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="unique" fill="var(--accent)" radius={[0, 4, 4, 0]} name="Unique Values" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Column Info Table */}
      <div className="card glass" style={{ padding: 0 }}>
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)' }}>
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600 }}>Column Summary</h2>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ backgroundColor: 'var(--bg-secondary)', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                <th style={{ padding: '1rem 1.5rem' }}>Column</th>
                <th style={{ padding: '1rem 1.5rem' }}>Type</th>
                <th style={{ padding: '1rem 1.5rem' }}>Missing</th>
                <th style={{ padding: '1rem 1.5rem' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {(info?.column_names || []).map((col) => {
                const dtype = info?.dtypes?.[col] || 'unknown';
                const missing = info?.missing_values?.[col] || 0;
                return (
                  <tr key={col} style={{ borderBottom: '1px solid var(--border-color)', fontSize: '0.9375rem' }}>
                    <td style={{ padding: '0.875rem 1.5rem', fontWeight: 500 }}>{col}</td>
                    <td style={{ padding: '0.875rem 1.5rem', color: 'var(--text-secondary)' }}>
                      <code style={{ fontSize: '0.8125rem', backgroundColor: 'var(--bg-secondary)', padding: '0.15rem 0.4rem', borderRadius: '4px' }}>{dtype}</code>
                    </td>
                    <td style={{ padding: '0.875rem 1.5rem', color: missing > 0 ? 'var(--warning)' : 'var(--text-muted)' }}>{missing}</td>
                    <td style={{ padding: '0.875rem 1.5rem' }}>
                      <span style={{
                        display: 'inline-flex', alignItems: 'center', gap: '0.25rem',
                        fontSize: '0.75rem', fontWeight: 600,
                        color: missing === 0 ? 'var(--success)' : 'var(--warning)',
                        backgroundColor: missing === 0 ? 'var(--success-bg)' : 'var(--warning-bg)',
                        padding: '0.2rem 0.5rem', borderRadius: '9999px'
                      }}>
                        {missing === 0 ? <CheckCircle size={12} /> : <AlertTriangle size={12} />}
                        {missing === 0 ? 'Clean' : 'Has Missing'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </PageTransition>
  );
};

export default Insights;
