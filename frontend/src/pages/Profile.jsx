import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { User, Mail, Calendar, Activity, Shield, Edit2, CheckCircle } from 'lucide-react';
import PageTransition from '../components/layout/PageTransition';
import { useAuth } from '../hooks/useAuth';
import api from '../services/api';

const Profile = () => {
  const { user, login, token } = useAuth();
  const [profile, setProfile] = useState(null);
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({ username: '', email: '' });
  const [saveStatus, setSaveStatus] = useState('idle');
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/user/profile').then(res => {
      setProfile(res.data.profile);
      setFormData({ username: res.data.profile.username, email: res.data.profile.email });
    });
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaveStatus('saving');
    setError('');
    try {
      await api.put('/user/profile', formData);
      setProfile(prev => ({ ...prev, ...formData }));
      setSaveStatus('saved');
      setEditing(false);
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (err) {
      setError(err.response?.data?.msg || 'Failed to save profile.');
      setSaveStatus('idle');
    }
  };

  const avatarLetter = (profile?.username || 'U').charAt(0).toUpperCase();

  return (
    <PageTransition>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.875rem', fontWeight: 700, marginBottom: '0.5rem' }}>My Profile</h1>
        <p style={{ color: 'var(--text-secondary)' }}>View and update your personal information.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>

        {/* Left: Avatar & Quick Info */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <motion.div className="card glass" style={{ textAlign: 'center', padding: '2.5rem 1.5rem' }} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <div style={{
              width: '96px', height: '96px', borderRadius: '50%', backgroundColor: 'var(--accent)',
              color: 'white', fontSize: '2.5rem', fontWeight: 800, display: 'flex', alignItems: 'center',
              justifyContent: 'center', margin: '0 auto 1.5rem', boxShadow: '0 0 0 4px var(--accent-light)'
            }}>
              {avatarLetter}
            </div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.25rem' }}>{profile?.username || '...'}</h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>{profile?.email || '...'}</p>
            <span style={{
              display: 'inline-flex', alignItems: 'center', gap: '0.25rem',
              padding: '0.3rem 0.75rem', borderRadius: '9999px', fontSize: '0.875rem', fontWeight: 600,
              backgroundColor: profile?.is_admin ? 'rgba(250,204,21,0.15)' : 'var(--accent-light)',
              color: profile?.is_admin ? '#ca8a04' : 'var(--accent)'
            }}>
              <Shield size={14} /> {profile?.is_admin ? 'Administrator' : 'Member'}
            </span>
          </motion.div>

          <div className="card glass">
            <h3 style={{ fontWeight: 600, marginBottom: '1rem', fontSize: '1rem' }}>Account Details</h3>
            {[
              { icon: Calendar, label: 'Member Since', value: profile?.createdAt ? new Date(profile.createdAt).toLocaleDateString() : '—' },
              { icon: Activity,  label: 'Last Login',   value: profile?.lastLogin ? new Date(profile.lastLogin).toLocaleDateString() : '—' },
            ].map(({ icon: Icon, label, value }) => (
              <div key={label} style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', padding: '0.75rem 0', borderBottom: '1px solid var(--border-color)' }}>
                <Icon size={18} color="var(--text-muted)" />
                <div>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{label}</p>
                  <p style={{ fontWeight: 500, fontSize: '0.9375rem' }}>{value}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Edit Form */}
        <div className="card glass">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>Personal Information</h2>
            {!editing && (
              <button className="btn btn-outline" onClick={() => setEditing(true)} style={{ padding: '0.5rem 1rem' }}>
                <Edit2 size={16} /> Edit
              </button>
            )}
            {saveStatus === 'saved' && (
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--success)', fontWeight: 500 }}>
                <CheckCircle size={18} /> Saved!
              </span>
            )}
          </div>

          {error && (
            <div style={{ padding: '1rem', backgroundColor: 'var(--danger-bg)', color: 'var(--danger)', borderRadius: 'var(--radius-md)', marginBottom: '1.5rem' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div>
              <label className="label"><User size={14} style={{ display: 'inline', marginRight: '0.25rem' }} /> Username</label>
              <input
                type="text"
                className="input-field"
                value={formData.username}
                onChange={e => setFormData(p => ({ ...p, username: e.target.value }))}
                disabled={!editing}
                style={{ opacity: editing ? 1 : 0.7, cursor: editing ? 'text' : 'default' }}
              />
            </div>
            <div>
              <label className="label"><Mail size={14} style={{ display: 'inline', marginRight: '0.25rem' }} /> Email Address</label>
              <input
                type="email"
                className="input-field"
                value={formData.email}
                onChange={e => setFormData(p => ({ ...p, email: e.target.value }))}
                disabled={!editing}
                style={{ opacity: editing ? 1 : 0.7, cursor: editing ? 'text' : 'default' }}
              />
            </div>
            <div>
              <label className="label">Role</label>
              <input type="text" className="input-field" value={profile?.is_admin ? 'Administrator' : 'Member'} disabled style={{ opacity: 0.6, cursor: 'default' }} />
            </div>

            {editing && (
              <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                <button type="submit" className="btn btn-primary" disabled={saveStatus === 'saving'}>
                  {saveStatus === 'saving' ? 'Saving...' : 'Save Changes'}
                </button>
                <button type="button" className="btn btn-outline" onClick={() => { setEditing(false); setError(''); setFormData({ username: profile.username, email: profile.email }); }}>
                  Cancel
                </button>
              </div>
            )}
          </form>
        </div>
      </div>
    </PageTransition>
  );
};

export default Profile;
