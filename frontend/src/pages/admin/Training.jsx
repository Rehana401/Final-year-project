import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, AlertCircle, Loader, ChevronRight, Database, Brain, Zap } from 'lucide-react';
import PageTransition from '../../components/layout/PageTransition';
import api from '../../services/api';

const STEPS = [
  { id: 1, label: 'Load & Preprocess', icon: Database, desc: 'Load the CSV dataset, clean it, apply SMOTE balancing, and build feature engineering pipelines.' },
  { id: 2, label: 'Train Models', icon: Brain, desc: 'Train Random Forest, XGBoost, and other classifiers. Evaluate all models with cross-validation.' },
  { id: 3, label: 'Tune & Save Best', icon: Zap, desc: 'Apply RandomizedSearchCV to the best model, compute final metrics, and deploy to the prediction engine.' },
];

const StatusBadge = ({ status }) => {
  const styles = {
    idle:    { color: 'var(--text-muted)',    bg: 'var(--bg-secondary)', label: 'Waiting' },
    loading: { color: 'var(--warning)',        bg: 'var(--warning-bg)',   label: 'Running...' },
    done:    { color: 'var(--success)',        bg: 'var(--success-bg)',   label: 'Complete' },
    error:   { color: 'var(--danger)',         bg: 'var(--danger-bg)',    label: 'Failed' },
  }[status] || {};

  return (
    <span style={{ fontSize: '0.75rem', fontWeight: 600, color: styles.color, backgroundColor: styles.bg, padding: '0.2rem 0.6rem', borderRadius: '9999px' }}>
      {status === 'loading' ? <Loader size={10} style={{ display: 'inline', marginRight: '4px' }} /> : null}
      {styles.label}
    </span>
  );
};

const Training = () => {
  const [stepStatus, setStepStatus] = useState({ 1: 'idle', 2: 'idle', 3: 'idle' });
  const [stepResult, setStepResult] = useState({ 1: null, 2: null, 3: null });
  const [activeStep, setActiveStep] = useState(1);

  const runStep = async (stepId) => {
    setStepStatus(prev => ({ ...prev, [stepId]: 'loading' }));
    const endpoints = { 1: '/admin/train/preprocess', 2: '/admin/train/train_all', 3: '/admin/train/tune' };

    try {
      const res = await api.post(endpoints[stepId]);
      setStepResult(prev => ({ ...prev, [stepId]: res.data }));
      setStepStatus(prev => ({ ...prev, [stepId]: 'done' }));
      if (stepId < 3) setActiveStep(stepId + 1);
    } catch (err) {
      setStepResult(prev => ({ ...prev, [stepId]: { msg: err.response?.data?.msg || 'Step failed.' } }));
      setStepStatus(prev => ({ ...prev, [stepId]: 'error' }));
    }
  };

  const canRunStep = (stepId) => {
    if (stepId === 1) return stepStatus[1] !== 'loading';
    return stepStatus[stepId - 1] === 'done' && stepStatus[stepId] !== 'loading';
  };

  return (
    <PageTransition>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.875rem', fontWeight: 700, marginBottom: '0.5rem' }}>Model Training</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Run the full 3-step ML training pipeline to retrain and deploy the fraud detection model.</p>
      </div>

      {/* Step Wizard */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2.5rem' }}>
        {STEPS.map((step, i) => (
          <React.Fragment key={step.id}>
            <div
              onClick={() => setActiveStep(step.id)}
              style={{
                display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem 1.25rem',
                borderRadius: 'var(--radius-lg)', cursor: 'pointer', flex: 1,
                backgroundColor: activeStep === step.id ? 'var(--accent-light)' : 'var(--bg-card)',
                border: `1px solid ${activeStep === step.id ? 'var(--accent)' : 'var(--border-color)'}`,
                transition: 'all 0.2s ease'
              }}
            >
              <div style={{
                width: '36px', height: '36px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                backgroundColor: stepStatus[step.id] === 'done' ? 'var(--success)' : stepStatus[step.id] === 'error' ? 'var(--danger)' : activeStep === step.id ? 'var(--accent)' : 'var(--bg-secondary)',
                color: (stepStatus[step.id] === 'done' || stepStatus[step.id] === 'error' || activeStep === step.id) ? 'white' : 'var(--text-muted)'
              }}>
                {stepStatus[step.id] === 'done' ? <CheckCircle size={18} /> : stepStatus[step.id] === 'error' ? <AlertCircle size={18} /> : <step.icon size={18} />}
              </div>
              <div>
                <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginBottom: '0.15rem' }}>Step {step.id}</p>
                <p style={{ fontSize: '0.9375rem', fontWeight: 600, color: 'var(--text-primary)' }}>{step.label}</p>
              </div>
              <StatusBadge status={stepStatus[step.id]} />
            </div>
            {i < STEPS.length - 1 && <ChevronRight size={20} color="var(--text-muted)" style={{ flexShrink: 0 }} />}
          </React.Fragment>
        ))}
      </div>

      {/* Active Step Detail */}
      {STEPS.map(step => (
        <AnimatePresence key={step.id}>
          {activeStep === step.id && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="card glass"
              style={{ marginBottom: '2rem' }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
                <div>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>Step {step.id}: {step.label}</h2>
                  <p style={{ color: 'var(--text-secondary)', maxWidth: '600px' }}>{step.desc}</p>
                </div>
                <button
                  className="btn btn-primary"
                  onClick={() => runStep(step.id)}
                  disabled={!canRunStep(step.id)}
                  style={{ flexShrink: 0, marginLeft: '2rem' }}
                >
                  {stepStatus[step.id] === 'loading' ? 'Running...' : stepStatus[step.id] === 'done' ? 'Re-run Step' : `Run Step ${step.id}`}
                </button>
              </div>

              {/* Results */}
              <AnimatePresence>
                {stepResult[step.id] && (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className={stepStatus[step.id] === 'error' ? '' : ''}>
                    {stepStatus[step.id] === 'error' ? (
                      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', color: 'var(--danger)', backgroundColor: 'var(--danger-bg)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                        <AlertCircle size={18} /> {stepResult[step.id].msg}
                      </div>
                    ) : (
                      <div style={{ backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)', padding: '1.5rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', color: 'var(--success)' }}>
                          <CheckCircle size={18} /> <strong>Step completed successfully</strong>
                        </div>

                        {/* Step 1 result */}
                        {step.id === 1 && stepResult[1] && (
                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                            {[['Train Samples', stepResult[1].train_samples?.toLocaleString()], ['Test Samples', stepResult[1].test_samples?.toLocaleString()], ['Features', stepResult[1].features]].map(([label, val]) => (
                              <div key={label} style={{ textAlign: 'center' }}>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>{label}</p>
                                <p style={{ fontWeight: 700, fontSize: '1.5rem' }}>{val}</p>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Step 2 result */}
                        {step.id === 2 && stepResult[2]?.metrics && (
                          <div style={{ overflowX: 'auto' }}>
                            <p style={{ marginBottom: '0.75rem', fontWeight: 600 }}>Best Model: <span style={{ color: 'var(--accent)' }}>{stepResult[2].best_model}</span></p>
                            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                              <thead>
                                <tr style={{ color: 'var(--text-muted)' }}>
                                  {Object.keys(stepResult[2].metrics[0] || {}).map(k => <th key={k} style={{ padding: '0.5rem 1rem', textAlign: 'left' }}>{k}</th>)}
                                </tr>
                              </thead>
                              <tbody>
                                {stepResult[2].metrics.map((row, i) => (
                                  <tr key={i} style={{ borderTop: '1px solid var(--border-color)' }}>
                                    {Object.values(row).map((v, j) => (
                                      <td key={j} style={{ padding: '0.5rem 1rem', color: typeof v === 'number' ? 'var(--accent)' : 'var(--text-primary)', fontWeight: typeof v === 'number' ? 600 : 400 }}>
                                        {typeof v === 'number' ? v.toFixed(4) : v}
                                      </td>
                                    ))}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )}

                        {/* Step 3 result */}
                        {step.id === 3 && stepResult[3]?.tuned_metrics && (
                          <>
                            <p style={{ marginBottom: '1rem', fontWeight: 600 }}>
                              Deployed Model: <span style={{ color: 'var(--accent)' }}>{stepResult[3].best_model || 'Best Model'}</span>
                            </p>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '1rem' }}>
                              {Object.entries(stepResult[3].tuned_metrics).map(([key, val]) => (
                                <div key={key} style={{ textAlign: 'center', backgroundColor: 'var(--bg-card)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.8125rem', marginBottom: '0.25rem' }}>{key}</p>
                                  <p style={{ fontWeight: 800, fontSize: '1.25rem', color: 'var(--accent)' }}>{(val * 100).toFixed(2)}%</p>
                                </div>
                              ))}
                            </div>
                          </>
                        )}
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          )}
        </AnimatePresence>
      ))}
    </PageTransition>
  );
};

export default Training;
