import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Sun, Moon, Monitor, Lock, Bell, Trash2, CheckCircle, AlertCircle, Eye, EyeOff } from 'lucide-react';
import PageTransition from '../components/layout/PageTransition';
import { useTheme } from '../context/ThemeContext';
import api from '../services/api';

const Section = ({ title, children }) => (
  <div className="card glass" style={{ marginBottom: '1.5rem' }}>
    <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>{title}</h2>
    {children}
  </div>
);

const ThemeOption = ({ value, label, icon: Icon, current, onClick }) => (
  <button
    onClick={() => onClick(value)}
    style={{
      flex: 1, padding: '1rem', borderRadius: 'var(--radius-md)', border: `2px solid ${current === value ? 'var(--accent)' : 'var(--border-color)'}`,
      background: current === value ? 'var(--accent-light)' : 'var(--bg-secondary)',
      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem', cursor: 'pointer',
      color: current === value ? 'var(--accent)' : 'var(--text-secondary)', transition: 'all 0.2s ease'
    }}
  >
    <Icon size={24} />
    <span style={{ fontSize: '0.875rem', fontWeight: 600 }}>{label}</span>
  </button>
);

const Settings = () => {
  const { theme, toggleTheme } = useTheme();

  const [pwForm, setPwForm] = useState({ old_password: '', new_password: '', confirm: '' });
  const [showPw, setShowPw] = useState({ old: false, new: false, confirm: false });
  const [pwStatus, setPwStatus] = useState('idle');
  const [pwMsg, setPwMsg] = useState('');

  const [notifications, setNotifications] = useState({ emailAlerts: true, weeklyReport: false });

  const getStrength = (pw) => {
    let s = 0;
    if (pw.length > 5) s += 25;
    if (pw.length > 8) s += 25;
    if (/[A-Z]/.test(pw)) s += 25;
    if (/[0-9!@#$%]/.test(pw)) s += 25;
    return s;
  };
  const strength = getStrength(pwForm.new_password);
  const strengthColor = strength >= 75 ? 'var(--success)' : strength >= 50 ? 'var(--warning)' : 'var(--danger)';

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    if (pwForm.new_password !== pwForm.confirm) { setPwMsg('Passwords do not match.'); setPwStatus('error'); return; }
    if (pwForm.new_password.length < 6) { setPwMsg('Password must be at least 6 characters.'); setPwStatus('error'); return; }
    setPwStatus('saving');
    try {
      await api.put('/user/password', { old_password: pwForm.old_password, new_password: pwForm.new_password });
      setPwStatus('saved');
      setPwMsg('Password updated successfully.');
      setPwForm({ old_password: '', new_password: '', confirm: '' });
      setTimeout(() => { setPwStatus('idle'); setPwMsg(''); }, 3000);
    } catch (err) {
      setPwStatus('error');
      setPwMsg(err.response?.data?.msg || 'Failed to update password.');
    }
  };

  return (
    <PageTransition>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.875rem', fontWeight: 700, marginBottom: '0.5rem' }}>Settings</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Manage your preferences, security, and account options.</p>
      </div>

      {/* Appearance */}
      <Section title="Appearance">
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9375rem', marginBottom: '1rem' }}>Choose your preferred colour scheme.</p>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <ThemeOption value="light" label="Light" icon={Sun} current={theme} onClick={() => theme !== 'light' && toggleTheme()} />
          <ThemeOption value="dark"  label="Dark"  icon={Moon} current={theme} onClick={() => theme !== 'dark'  && toggleTheme()} />
        </div>
      </Section>

      {/* Security */}
      <Section title="Change Password">
        {pwMsg && (
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', padding: '0.75rem 1rem', borderRadius: 'var(--radius-md)', marginBottom: '1rem', backgroundColor: pwStatus === 'saved' ? 'var(--success-bg)' : 'var(--danger-bg)', color: pwStatus === 'saved' ? 'var(--success)' : 'var(--danger)' }}>
            {pwStatus === 'saved' ? <CheckCircle size={16} /> : <AlertCircle size={16} />} {pwMsg}
          </div>
        )}
        <form onSubmit={handlePasswordChange} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', maxWidth: '480px' }}>
          {[
            { key: 'old_password', label: 'Current Password',  showKey: 'old'     },
            { key: 'new_password', label: 'New Password',       showKey: 'new'     },
            { key: 'confirm',      label: 'Confirm New Password', showKey: 'confirm' },
          ].map(({ key, label, showKey }) => (
            <div key={key}>
              <label className="label">{label}</label>
              <div style={{ position: 'relative' }}>
                <input
                  type={showPw[showKey] ? 'text' : 'password'}
                  className="input-field"
                  value={pwForm[key]}
                  onChange={e => setPwForm(p => ({ ...p, [key]: e.target.value }))}
                  style={{ paddingRight: '3rem' }}
                  required
                />
                <button type="button" onClick={() => setShowPw(p => ({ ...p, [showKey]: !p[showKey] }))}
                  style={{ position: 'absolute', right: '1rem', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                  {showPw[showKey] ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {key === 'new_password' && pwForm.new_password && (
                <div style={{ marginTop: '0.5rem' }}>
                  <div style={{ height: '4px', backgroundColor: 'var(--border-color)', borderRadius: '2px', overflow: 'hidden' }}>
                    <div style={{ width: `${strength}%`, height: '100%', backgroundColor: strengthColor, transition: 'all 0.3s ease' }} />
                  </div>
                  <p style={{ fontSize: '0.75rem', color: strengthColor, marginTop: '0.25rem', textAlign: 'right', fontWeight: 600 }}>
                    {strength < 50 ? 'Weak' : strength < 75 ? 'Fair' : 'Strong'}
                  </p>
                </div>
              )}
            </div>
          ))}
          <button type="submit" className="btn btn-primary" style={{ alignSelf: 'flex-start' }} disabled={pwStatus === 'saving'}>
            <Lock size={16} /> {pwStatus === 'saving' ? 'Updating...' : 'Update Password'}
          </button>
        </form>
      </Section>

      {/* Notifications */}
      <Section title="Notification Preferences">
        {[
          { key: 'emailAlerts',   label: 'Email Fraud Alerts',      desc: 'Receive simulated email alerts when a fraud transaction is detected.' },
          { key: 'weeklyReport',  label: 'Weekly Summary Report',    desc: 'Get a PDF summary of your activity delivered weekly.' },
        ].map(({ key, label, desc }) => (
          <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 0', borderBottom: '1px solid var(--border-color)' }}>
            <div>
              <p style={{ fontWeight: 500 }}>{label}</p>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>{desc}</p>
            </div>
            <label style={{ position: 'relative', display: 'inline-flex', alignItems: 'center', cursor: 'pointer' }}>
              <input type="checkbox" style={{ opacity: 0, width: 0, height: 0 }} checked={notifications[key]} onChange={() => setNotifications(p => ({ ...p, [key]: !p[key] }))} />
              <div style={{
                width: '44px', height: '24px', backgroundColor: notifications[key] ? 'var(--accent)' : 'var(--border-color)',
                borderRadius: '12px', transition: 'background-color 0.2s ease', position: 'relative'
              }}>
                <div style={{
                  position: 'absolute', top: '2px', left: notifications[key] ? '22px' : '2px',
                  width: '20px', height: '20px', backgroundColor: 'white', borderRadius: '50%',
                  transition: 'left 0.2s ease', boxShadow: '0 1px 3px rgba(0,0,0,0.2)'
                }} />
              </div>
            </label>
          </div>
        ))}
      </Section>

      {/* Danger Zone */}
      <Section title="⚠️ Danger Zone">
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9375rem', marginBottom: '1.5rem' }}>
          These actions are irreversible. Please proceed with caution.
        </p>
        <button
          className="btn"
          style={{ backgroundColor: 'var(--danger-bg)', color: 'var(--danger)', border: '1px solid var(--danger)', gap: '0.5rem' }}
          onClick={() => { if (window.confirm('Are you sure? This cannot be undone.')) alert('Account deletion not yet wired to backend.'); }}
        >
          <Trash2 size={16} /> Delete My Account
        </button>
      </Section>
    </PageTransition>
  );
};

export default Settings;
