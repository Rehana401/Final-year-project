import React from 'react';
import { Link } from 'react-router-dom';
import { Shield } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import { useAuth } from '../../hooks/useAuth';
import { Sun, Moon } from 'lucide-react';
import './Navbar.css';

/**
 * PublicNavbar — used on About, Contact and other public-facing pages
 * that are outside the authenticated AppShell.
 */
const PublicNavbar = () => {
  const { theme, toggleTheme } = useTheme();
  const { user } = useAuth();

  return (
    <header className="navbar glass" style={{ position: 'sticky', top: 0, zIndex: 100 }}>
      <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', color: 'var(--text-primary)', textDecoration: 'none', fontWeight: 700, fontSize: '1.125rem' }}>
        <Shield size={24} color="var(--accent)" /> SecurBank
      </Link>

      <div className="navbar-right">
        <Link to="/about" style={{ color: 'var(--text-secondary)', fontWeight: 500, marginRight: '0.5rem' }}>About</Link>
        <Link to="/contact" style={{ color: 'var(--text-secondary)', fontWeight: 500, marginRight: '1rem' }}>Contact</Link>
        <button className="icon-btn" onClick={toggleTheme} aria-label="Toggle theme">
          {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
        </button>
        {user ? (
          <Link to="/dashboard" className="btn btn-primary" style={{ padding: '0.4rem 1rem' }}>Go to Dashboard</Link>
        ) : (
          <Link to="/login" className="btn btn-primary" style={{ padding: '0.4rem 1rem' }}>Login</Link>
        )}
      </div>
    </header>
  );
};

export default PublicNavbar;
