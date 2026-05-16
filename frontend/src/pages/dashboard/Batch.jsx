import React, { useState, useRef } from 'react';
import { Upload, File, AlertCircle, CheckCircle, Download } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import PageTransition from '../../components/layout/PageTransition';
import api from '../../services/api';

const Batch = () => {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [status, setStatus] = useState('idle'); // idle, uploading, processing, complete, error
  const [errorMsg, setErrorMsg] = useState('');
  const [results, setResults] = useState(null);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const handleFileSelection = (selectedFile) => {
    if (selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile);
      setErrorMsg('');
      setStatus('idle');
      setResults(null);
    } else {
      setErrorMsg('Please select a valid CSV file.');
      setFile(null);
    }
  };

  const processFile = async () => {
    if (!file) return;
    
    setStatus('processing');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await api.post('/predict/batch', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setResults(response.data.results);
      setStatus('complete');
    } catch (err) {
      setStatus('error');
      setErrorMsg(err.response?.data?.msg || 'Failed to process file.');
    }
  };

  const totalProcessed = results ? results.length : 0;
  const fraudCount = results ? results.filter(r => r.label === 'fraud').length : 0;
  const errorCount = results ? results.filter(r => r.error).length : 0;

  return (
    <PageTransition>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.875rem', fontWeight: 700, marginBottom: '0.5rem' }}>Batch Analysis</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Upload a CSV file containing multiple transactions to process them at once.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '2rem' }}>
        
        {/* Upload Zone */}
        <div className="card glass">
          <div 
            style={{ 
              border: `2px dashed ${isDragging ? 'var(--accent)' : 'var(--border-color)'}`,
              borderRadius: 'var(--radius-lg)',
              padding: '4rem 2rem',
              textAlign: 'center',
              backgroundColor: isDragging ? 'var(--accent-light)' : 'transparent',
              transition: 'all 0.2s ease',
              cursor: 'pointer'
            }}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              style={{ display: 'none' }} 
              accept=".csv"
              onChange={handleFileChange}
            />
            <Upload size={48} color={isDragging ? 'var(--accent)' : 'var(--text-muted)'} style={{ margin: '0 auto 1rem' }} />
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>Drop CSV file here</h3>
            <p style={{ color: 'var(--text-secondary)' }}>or click to browse your computer</p>
          </div>

          {errorMsg && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '1rem', backgroundColor: 'var(--danger-bg)', color: 'var(--danger)', borderRadius: 'var(--radius-md)', marginTop: '1rem' }}>
              <AlertCircle size={18} />
              <span>{errorMsg}</span>
            </div>
          )}

          {file && status !== 'complete' && (
            <div style={{ marginTop: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', backgroundColor: 'var(--bg-secondary)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <File size={24} color="var(--accent)" />
                <div>
                  <p style={{ fontWeight: 600 }}>{file.name}</p>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{(file.size / 1024).toFixed(1)} KB</p>
                </div>
              </div>
              
              <button 
                className="btn btn-primary" 
                onClick={(e) => { e.stopPropagation(); processFile(); }}
                disabled={status === 'processing'}
              >
                {status === 'processing' ? 'Processing...' : 'Run Batch Analysis'}
              </button>
            </div>
          )}
        </div>

        {/* Results */}
        <AnimatePresence>
          {status === 'complete' && results && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="card glass"
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <CheckCircle size={32} color="var(--success)" />
                  <div>
                    <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Analysis Complete</h2>
                    <p style={{ color: 'var(--text-secondary)' }}>Processed {totalProcessed} rows successfully.</p>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <button className="btn btn-outline"><Download size={18} /> Download CSV</button>
                  <button className="btn btn-outline"><Download size={18} /> Export PDF</button>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
                <div style={{ padding: '1.5rem', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                  <p style={{ color: 'var(--text-secondary)' }}>Total Processed</p>
                  <h3 style={{ fontSize: '2rem', fontWeight: 800 }}>{totalProcessed}</h3>
                </div>
                <div style={{ padding: '1.5rem', backgroundColor: 'var(--danger-bg)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                  <p style={{ color: 'var(--danger)' }}>Fraud Detected</p>
                  <h3 style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--danger)' }}>{fraudCount}</h3>
                </div>
                <div style={{ padding: '1.5rem', backgroundColor: 'var(--warning-bg)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                  <p style={{ color: 'var(--warning)' }}>Errors</p>
                  <h3 style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--warning)' }}>{errorCount}</h3>
                </div>
              </div>

              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ backgroundColor: 'var(--bg-secondary)', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                      <th style={{ padding: '1rem' }}>Row</th>
                      <th style={{ padding: '1rem' }}>Amount</th>
                      <th style={{ padding: '1rem' }}>Type</th>
                      <th style={{ padding: '1rem' }}>Risk Score</th>
                      <th style={{ padding: '1rem' }}>Result</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((res, idx) => (
                      <tr key={idx} style={{ borderBottom: '1px solid var(--border-color)', fontSize: '0.9375rem' }}>
                        <td style={{ padding: '1rem' }}>{idx + 1}</td>
                        {res.error ? (
                          <td colSpan="4" style={{ padding: '1rem', color: 'var(--danger)' }}>Error: {res.error}</td>
                        ) : (
                          <>
                            <td style={{ padding: '1rem', fontWeight: 500 }}>Rs {res.amount}</td>
                            <td style={{ padding: '1rem' }}>{res.transaction_type}</td>
                            <td style={{ padding: '1rem' }}>{res.risk_score}%</td>
                            <td style={{ padding: '1rem' }}>
                              <span style={{ 
                                padding: '0.25rem 0.5rem', 
                                borderRadius: '4px', 
                                fontSize: '0.75rem', 
                                fontWeight: 600,
                                backgroundColor: res.label === 'fraud' ? 'var(--danger-bg)' : 'var(--success-bg)',
                                color: res.label === 'fraud' ? 'var(--danger)' : 'var(--success)',
                                textTransform: 'uppercase'
                              }}>
                                {res.label}
                              </span>
                            </td>
                          </>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </PageTransition>
  );
};

export default Batch;
