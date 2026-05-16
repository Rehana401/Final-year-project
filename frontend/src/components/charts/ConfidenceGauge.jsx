import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';

const ConfidenceGauge = ({ score }) => {
  // score is 0-100
  const data = [
    { name: 'Score', value: score },
    { name: 'Remaining', value: 100 - score },
  ];

  let color = 'var(--success)';
  if (score > 40) color = 'var(--warning)';
  if (score > 75) color = 'var(--danger)';

  return (
    <div style={{ position: 'relative', height: '200px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="100%"
            startAngle={180}
            endAngle={0}
            innerRadius={60}
            outerRadius={80}
            paddingAngle={0}
            dataKey="value"
            stroke="none"
          >
            <Cell fill={color} />
            <Cell fill="var(--bg-secondary)" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <motion.div 
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: "spring", stiffness: 200, damping: 15 }}
        style={{ 
          position: 'absolute', 
          bottom: '10px', 
          textAlign: 'center' 
        }}
      >
        <span style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1 }}>{score.toFixed(1)}</span>
        <span style={{ fontSize: '1rem', color: 'var(--text-secondary)', marginLeft: '2px' }}>%</span>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '4px', textTransform: 'uppercase', letterSpacing: '1px' }}>Risk Score</p>
      </motion.div>
    </div>
  );
};

export default ConfidenceGauge;
