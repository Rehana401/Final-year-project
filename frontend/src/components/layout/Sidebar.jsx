import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import {
  LayoutDashboard,
  Activity,
  Upload,
  Clock,
  Settings,
  User,
  Database,
  Brain,
  Users,
  Shield,
  MonitorPlay,
} from 'lucide-react';
import './Sidebar.css';

const Sidebar = () => {
  const { user } = useAuth();

  return (
    <aside className="sidebar">
      <Link to="/" className="sidebar-header" style={{ textDecoration: 'none', color: 'inherit' }}>
        <Shield className="logo-icon" size={30} />
        <h2>SecurBank</h2>
      </Link>

      <nav className="sidebar-nav">
        <div className="nav-group">
          <p className="nav-label">Dashboard</p>
          <NavLink to="/dashboard" end className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}>
            <LayoutDashboard size={19} /> Overview
          </NavLink>
          <NavLink to="/dashboard/analyze" className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}>
            <Activity size={19} /> Analyze
          </NavLink>
          <NavLink to="/dashboard/monitor" className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}>
            <MonitorPlay size={19} /> Live Monitor
          </NavLink>
          <NavLink to="/dashboard/batch" className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}>
            <Upload size={19} /> Batch Analysis
          </NavLink>
          <NavLink to="/dashboard/history" className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}>
            <Clock size={19} /> History
          </NavLink>
        </div>

        {user?.is_admin && (
          <div className="nav-group">
            <p className="nav-label">Admin</p>
            <NavLink to="/admin/insights" className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}>
              <Database size={19} /> Dataset Insights
            </NavLink>
            <NavLink to="/admin/training" className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}>
              <Brain size={19} /> Model Training
            </NavLink>
            <NavLink to="/admin/users" className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}>
              <Users size={19} /> Manage Users
            </NavLink>
          </div>
        )}

        <div className="nav-group">
          <p className="nav-label">Account</p>
          <NavLink to="/profile" className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}>
            <User size={19} /> Profile
          </NavLink>
          <NavLink to="/settings" className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}>
            <Settings size={19} /> Settings
          </NavLink>
        </div>
      </nav>
    </aside>
  );
};

export default Sidebar;

