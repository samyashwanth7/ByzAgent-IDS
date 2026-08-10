import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, CartesianGrid } from 'recharts';
import { accuracyComparison } from '../mockData';

export default function Compare() {
  return (
    <div className="animate-fade-in">
      <h1>Federated Architecture Comparison</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '32px', maxWidth: '800px' }}>
        This page demonstrates the core value proposition of XFed-IDS. Federated Learning achieves 
        near-centralized performance while preserving complete data privacy across organizations.
      </p>

      <div className="stats-grid">
        <div className="card">
          <div className="stat-label">Privacy Loss (Centralized)</div>
          <div className="stat-value" style={{ color: 'var(--status-critical)' }}>100%</div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Raw data exposed
          </div>
        </div>
        <div className="card">
          <div className="stat-label">Privacy Loss (Federated)</div>
          <div className="stat-value" style={{ color: 'var(--status-good)' }}>0%</div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Only weights shared
          </div>
        </div>
        <div className="card">
          <div className="stat-label">Accuracy Drop (IID)</div>
          <div className="stat-value" style={{ color: 'var(--accent-teal)' }}>-0.08%</div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            From baseline
          </div>
        </div>
      </div>

      <div className="card" style={{ height: '400px' }}>
        <h3 style={{ marginBottom: '24px' }}>Model Accuracy by Approach</h3>
        <ResponsiveContainer width="100%" height="85%">
          <BarChart data={accuracyComparison} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
            <XAxis dataKey="name" stroke="var(--text-secondary)" />
            <YAxis domain={[90, 100]} stroke="var(--text-secondary)" />
            <Tooltip />
            <Bar dataKey="accuracy" radius={[6, 6, 0, 0]}>
              {accuracyComparison.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={index === 0 ? 'var(--accent-blue)' : index === 3 ? 'var(--text-secondary)' : 'var(--accent-cyan)'} 
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
