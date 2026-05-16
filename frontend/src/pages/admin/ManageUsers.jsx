import React, { useState, useEffect } from 'react';
import { Users, Shield, ShieldOff, Trash2 } from 'lucide-react';
import PageTransition from '../../components/layout/PageTransition';
import api from '../../services/api';

const ManageUsers = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/admin/users')
      .then(res => setUsers(res.data.users))
      .catch(err => setError(err.response?.data?.msg || 'Failed to load users.'))
      .finally(() => setLoading(false));
  }, []);

  const formatDate = (dateStr) => {
    if (!dateStr) return '—';
    try { return new Date(dateStr).toLocaleDateString(); } catch { return dateStr; }
  };

  const handleDeleteUser = async (userId, username) => {
    if (!window.confirm(`Are you sure you want to permanently delete the user "${username}"?`)) return;

    try {
      await api.delete(`/admin/users/${userId}`);
      setUsers(users.filter(u => u.userId !== userId));
    } catch (err) {
      setError(err.response?.data?.msg || 'Failed to delete user.');
    }
  };

  return (
    <PageTransition>
      <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h1 style={{ fontSize: '1.875rem', fontWeight: 700, marginBottom: '0.5rem' }}>User Management</h1>
          <p style={{ color: 'var(--text-secondary)' }}>View and manage all registered users and their roles.</p>
        </div>
        <div className="card glass" style={{ padding: '1rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <Users size={24} color="var(--accent)" />
          <div>
            <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>Total Users</p>
            <p style={{ fontSize: '1.5rem', fontWeight: 800 }}>{users.length}</p>
          </div>
        </div>
      </div>

      {error && (
        <div style={{ padding: '1rem', backgroundColor: 'var(--danger-bg)', color: 'var(--danger)', borderRadius: 'var(--radius-md)', marginBottom: '1.5rem' }}>
          {error}
        </div>
      )}

      <div className="card glass" style={{ padding: 0 }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ backgroundColor: 'var(--bg-secondary)', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Username</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Email</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Role</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Joined</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 500 }}>Last Login</th>
                <th style={{ padding: '1rem 1.5rem', fontWeight: 500, textAlign: 'center' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="6" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>Loading users...</td></tr>
              ) : users.length === 0 ? (
                <tr><td colSpan="6" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>No users found.</td></tr>
              ) : (
                users.map((user) => (
                  <tr key={user.userId} style={{ borderBottom: '1px solid var(--border-color)', fontSize: '0.9375rem' }}>
                    <td style={{ padding: '1rem 1.5rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <div style={{
                          width: '36px', height: '36px', borderRadius: '50%',
                          backgroundColor: 'var(--accent)', color: 'white',
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontWeight: 700, fontSize: '1rem', flexShrink: 0
                        }}>
                          {user.username?.charAt(0).toUpperCase()}
                        </div>
                        <span style={{ fontWeight: 500 }}>{user.username}</span>
                      </div>
                    </td>
                    <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>{user.email}</td>
                    <td style={{ padding: '1rem 1.5rem' }}>
                      <span style={{
                        display: 'inline-flex', alignItems: 'center', gap: '0.25rem',
                        padding: '0.2rem 0.6rem', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 600,
                        backgroundColor: user.is_admin ? 'rgba(250,204,21,0.15)' : 'var(--accent-light)',
                        color: user.is_admin ? '#ca8a04' : 'var(--accent)'
                      }}>
                        {user.is_admin ? <Shield size={12} /> : <ShieldOff size={12} />}
                        {user.is_admin ? 'Admin' : 'Member'}
                      </span>
                    </td>
                    <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>{formatDate(user.createdAt)}</td>
                    <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>{formatDate(user.lastLogin)}</td>
                    <td style={{ padding: '1rem 1.5rem', textAlign: 'center' }}>
                      <button
                        onClick={() => handleDeleteUser(user.userId, user.username)}
                        style={{
                          background: 'none', border: 'none', color: 'var(--danger)', cursor: 'pointer',
                          padding: '0.5rem', borderRadius: 'var(--radius-md)', transition: 'background-color 0.2s ease',
                          display: 'inline-flex', alignItems: 'center', justifyContent: 'center'
                        }}
                        onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'var(--danger-bg)'}
                        onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                        title={`Delete ${user.username}`}
                        disabled={user.is_admin}
                      >
                        <Trash2 size={18} style={{ opacity: user.is_admin ? 0.3 : 1 }} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </PageTransition>
  );
};

export default ManageUsers;
