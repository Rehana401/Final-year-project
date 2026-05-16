import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useTheme } from '../../context/ThemeContext';
import { Sun, Moon, LogOut, Bell } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const [showNotifs, setShowNotifs] = React.useState(false);
  const [notifs, setNotifs] = React.useState([
    { id: 1, title: 'System Online', time: 'Just now', read: false },
    { id: 2, title: 'New Fraud Model Deployed', time: '2 hours ago', read: false },
    { id: 3, title: 'Weekly Report Generated', time: '1 day ago', read: false },
  ]);
  const notifRef = React.useRef(null);

  React.useEffect(() => {
    const handleClickOutside = (event) => {
      if (notifRef.current && !notifRef.current.contains(event.target)) {
        setShowNotifs(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const unreadCount = notifs.filter(n => !n.read).length;

  const handleNotifClick = () => {
    setShowNotifs(!showNotifs);
    if (!showNotifs) {
      setNotifs(notifs.map(n => ({ ...n, read: true })));
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="navbar glass">
      <div className="navbar-left">
        {/* Can put a search bar or breadcrumbs here */}
      </div>
      
      <div className="navbar-right">
        <button className="icon-btn" onClick={toggleTheme} aria-label="Toggle theme">
          {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
        </button>
        
        <div className="notif-wrapper" ref={notifRef} style={{ position: 'relative' }}>
          <button className="icon-btn" onClick={handleNotifClick} aria-label="Notifications">
            <Bell size={20} />
            {unreadCount > 0 && <span className="badge">{unreadCount}</span>}
          </button>
          
          {showNotifs && (
            <div className="notif-dropdown card glass">
              <div className="notif-header">
                <h3 style={{ fontSize: '0.875rem', fontWeight: 600, margin: 0 }}>Notifications</h3>
              </div>
              <div className="notif-body">
                {notifs.map(n => (
                  <div key={n.id} className="notif-item">
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: n.read ? 'transparent' : 'var(--accent)', marginTop: '4px', flexShrink: 0 }} />
                    <div>
                      <p style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-primary)', marginBottom: '0.2rem' }}>{n.title}</p>
                      <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{n.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        
        <div className="user-profile">
          <div className="avatar">
            {user?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div className="user-info">
            <span className="user-name">{user?.username || 'User'}</span>
            <span className="user-role">{user?.is_admin ? 'Admin' : 'Member'}</span>
          </div>
        </div>

        <button className="icon-btn logout-btn" onClick={handleLogout} aria-label="Logout">
          <LogOut size={20} />
        </button>
      </div>
    </header>
  );
};

export default Navbar;
