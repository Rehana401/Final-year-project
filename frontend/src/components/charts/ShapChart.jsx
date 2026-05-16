import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const ShapChart = ({ shapData }) => {
  // shapData is expected to be an array of { feature: string, importance: number }
  if (!shapData || shapData.length === 0) return null;

  // Sort by absolute importance
  const sortedData = [...shapData]
    .sort((a, b) => Math.abs(b.importance) - Math.abs(a.importance))
    .slice(0, 10); // top 10

  const maxVal = Math.max(...sortedData.map(d => Math.abs(d.importance)));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const isPositive = data.importance > 0;
      return (
        <div className="card glass" style={{ padding: '0.75rem', fontSize: '0.875rem' }}>
          <p style={{ fontWeight: 600, marginBottom: '0.25rem' }}>{data.feature}</p>
          <p style={{ color: isPositive ? 'var(--danger)' : 'var(--success)' }}>
            {isPositive ? 'Pushes towards FRAUD' : 'Pushes towards LEGIT'}
          </p>
          <p style={{ color: 'var(--text-secondary)' }}>Impact: {data.importance.toFixed(4)}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ width: '100%', height: 300 }}>
      <ResponsiveContainer>
        <BarChart
          data={sortedData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" horizontal={false} />
          <XAxis type="number" domain={[-maxVal * 1.1, maxVal * 1.1]} stroke="var(--text-muted)" tick={{ fontSize: 12 }} />
          <YAxis dataKey="feature" type="category" width={120} stroke="var(--text-secondary)" tick={{ fontSize: 12 }} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
            {sortedData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.importance > 0 ? 'var(--danger)' : 'var(--success)'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ShapChart;
