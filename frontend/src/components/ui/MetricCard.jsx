import React from 'react';
import { motion } from 'framer-motion';

const MetricCard = ({ title, value, icon: Icon, trend, color = 'var(--accent)' }) => {
  return (
    <motion.div 
      className="card glass"
      whileHover={{ y: -4, boxShadow: 'var(--shadow-md)' }}
      transition={{ duration: 0.2 }}
      style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', fontWeight: 500, marginBottom: '0.5rem' }}>{title}</p>
          <h3 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)' }}>{value}</h3>
        </div>
        <div style={{ padding: '0.75rem', backgroundColor: `${color}20`, borderRadius: '0.5rem', color: color }}>
          {Icon && <Icon size={24} />}
        </div>
      </div>
      {trend && (
        <div style={{ fontSize: '0.875rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <span style={{ color: trend > 0 ? 'var(--success)' : trend < 0 ? 'var(--danger)' : 'var(--text-muted)', fontWeight: 600 }}>
            {trend > 0 ? '+' : ''}{trend}%
          </span>
          <span style={{ color: 'var(--text-muted)' }}>from last week</span>
        </div>
      )}
    </motion.div>
  );
};

export default MetricCard;
