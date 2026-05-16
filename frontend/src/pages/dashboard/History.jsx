import React, { useState, useEffect } from 'react';
import { Download, Search, Filter, Trash2 } from 'lucide-react';
import PageTransition from '../../components/layout/PageTransition';
import api from '../../services/api';

const History = () => {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const response = await api.get('/history/');
      setRecords(response.data.records);
    } catch (err) {
      console.error('Failed to load history', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      console.log('Deleting record:', id);
      await api.delete(`/history/${id}`);
      console.log('Delete successful');
      setRecords(prevRecords => prevRecords.filter(r => r.historyId !== id));
    } catch (err) {
      console.error('Failed to delete', err);
      alert('Failed to delete the record. Please try again.');
    }
  };

  const exportCSV = async () => {
    try {
      const response = await api.post('/history/export/csv', { records: filteredRecords }, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'analysis_history.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Export failed', err);
    }
  };

  const exportPDF = async () => {
    try {
      const response = await api.post('/history/export/pdf', { records: filteredRecords }, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'analysis_history.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Export failed', err);
    }
  };

  const filteredRecords = records.filter(record => {
    const matchesSearch = JSON.stringify(record).toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'all' || (record.resultLabel && record.resultLabel.toLowerCase() === filterType);
    return matchesSearch && matchesType;
  });

  return (
    <PageTransition>
      <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h1 style={{ fontSize: '1.875rem', fontWeight: 700, marginBottom: '0.5rem' }}>Analysis History</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Review past transaction predictions and export reports.</p>
        </div>
        
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button className="btn btn-outline" onClick={exportCSV} disabled={filteredRecords.length === 0}>
            <Download size={18} /> Export CSV
          </button>
          <button className="btn btn-outline" onClick={exportPDF} disabled={filteredRecords.length === 0}>
            <Download size={18} /> Export PDF
          </button>
        </div>
      </div>

      <div className="card glass" style={{ padding: 0 }}>
        {/* Toolbar */}
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <div style={{ position: 'relative', flex: 1, maxWidth: '400px' }}>
            <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input 
              type="text" 
              className="input-field" 
              placeholder="Search transactions..." 
              style={{ paddingLeft: '2.5rem' }}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Filter size={18} color="var(--text-muted)" />
            <select className="input-field" value={filterType} onChange={(e) => setFilterType(e.target.value)} style={{ width: 'auto' }}>
              <option value="all">All Status</option>
              <option value="fraud">Fraud Only</option>
              <option value="legit">Legit Only</option>
            </select>
          </div>
        </div>

        {/* Table */}
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ backgroundColor: 'var(--bg-secondary)', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Date</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Amount</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Type</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Risk Score</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Status</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 500, textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="6" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>Loading history...</td></tr>
              ) : filteredRecords.length === 0 ? (
                <tr><td colSpan="6" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No records found.</td></tr>
              ) : (
                filteredRecords.map((record) => {
                  const details = JSON.parse(record.transactionDetails || '{}');
                  return (
                    <tr key={record.historyId} style={{ borderBottom: '1px solid var(--border-color)', fontSize: '0.9375rem' }}>
                      <td style={{ padding: '1rem 1.5rem' }}>{record.predictedAt}</td>
                      <td style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Rs {details.Transaction_Amount || 0}</td>
                      <td style={{ padding: '1rem 1.5rem' }}>{details.Transaction_Type || 'N/A'}</td>
                      <td style={{ padding: '1rem 1.5rem' }}>{record.riskScore}%</td>
                      <td style={{ padding: '1rem 1.5rem' }}>
                        <span style={{ 
                          padding: '0.25rem 0.5rem', 
                          borderRadius: '4px', 
                          fontSize: '0.75rem', 
                          fontWeight: 600,
                          backgroundColor: record.resultLabel === 'fraud' ? 'var(--danger-bg)' : 'var(--success-bg)',
                          color: record.resultLabel === 'fraud' ? 'var(--danger)' : 'var(--success)',
                          textTransform: 'uppercase'
                        }}>
                          {record.resultLabel}
                        </span>
                      </td>
                      <td style={{ padding: '1rem 1.5rem', textAlign: 'right' }}>
                        <button 
                          type="button"
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            handleDelete(record.historyId);
                          }}
                          style={{ 
                            background: 'none', 
                            border: '1px solid var(--border-color)', 
                            color: 'var(--danger)', 
                            cursor: 'pointer', 
                            padding: '0.5rem 0.75rem',
                            borderRadius: 'var(--radius-sm)',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.25rem',
                            fontSize: '0.8125rem',
                            transition: 'all 0.2s ease'
                          }}
                          title="Delete Record"
                        >
                          <Trash2 size={14} style={{ pointerEvents: 'none' }} /> Delete
                        </button>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </PageTransition>
  );
};

export default History;
