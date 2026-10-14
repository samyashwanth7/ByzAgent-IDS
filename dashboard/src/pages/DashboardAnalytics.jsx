import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function DashboardAnalytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/data/analytics.json')
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch((err) => {
        console.warn('Failed to load /data/analytics.json:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
        Loading real evaluation analytics...
      </div>
    );
  }

  if (!data || !data.confusion_matrix) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
        No analytics data available yet. Please complete model training and data export.
      </div>
    );
  }

  const renderConfusionMatrix = () => {
    const { confusion_matrix, class_names } = data;
    const maxVal = Math.max(...confusion_matrix.flat(), 1);

    return (
      <div className="card" style={{ marginBottom: '24px' }}>
        <h3 className="heading-md" style={{ marginBottom: '20px' }}>Confusion Matrix (8-Class Evaluation)</h3>
        
        <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '10px' }}>
          {/* Row Labels */}
          <div style={{ display: 'flex', flexDirection: 'column', marginTop: '24px', gap: '2px' }}>
            {class_names.map(name => (
              <div key={`row-${name}`} className="cm-row-label" style={{ height: '48px', width: '90px' }}>
                {name}
              </div>
            ))}
          </div>

          {/* Grid */}
          <div>
            <div className="cm-grid" style={{ gridTemplateColumns: `repeat(${class_names.length}, 1fr)`, marginBottom: '8px' }}>
              {class_names.map(name => (
                <div key={`col-${name}`} className="cm-header" style={{ width: '48px', writingMode: 'vertical-rl', transform: 'rotate(180deg)' }}>
                  {name}
                </div>
              ))}
            </div>

            <div className="cm-grid" style={{ gridTemplateColumns: `repeat(${class_names.length}, 1fr)` }}>
              {confusion_matrix.map((row, i) => (
                row.map((val, j) => {
                  const isDiagonal = i === j;
                  const intensity = val > 0 ? Math.max(0.12, Math.log10(val) / Math.log10(maxVal)) : 0;
                  const bg = isDiagonal 
                    ? `rgba(0, 240, 255, ${intensity})` 
                    : `rgba(239, 68, 68, ${intensity})`;

                  return (
                    <div 
                      key={`${i}-${j}`} 
                      className="cm-cell"
                      title={`True: ${class_names[i]}\nPredicted: ${class_names[j]}\nCount: ${val}`}
                      style={{ 
                        background: bg,
                        border: '1px solid rgba(255,255,255,0.05)',
                        color: intensity > 0.55 ? '#000' : 'var(--text)'
                      }}
                    >
                      {val > 0 ? val : ''}
                    </div>
                  );
                })
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div>
      <div className="dashboard-header">
        <h1>Deep Analytics</h1>
        <p>Class-wise performance breakdown and confusion matrix for ByzAgent aggregated model.</p>
      </div>

      {renderConfusionMatrix()}

      <div className="card">
        <h3 className="heading-md" style={{ marginBottom: '20px' }}>Per-Class Metrics</h3>
        <div style={{ width: '100%', height: '400px' }}>
          <ResponsiveContainer>
            <BarChart data={data.per_class_metrics} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis type="number" domain={[0, 1]} stroke="var(--text-secondary)" tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
              <YAxis dataKey="name" type="category" stroke="var(--text-secondary)" width={90} />
              <Tooltip 
                contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)' }}
                itemStyle={{ color: 'var(--text)' }}
                formatter={(val) => [(val * 100).toFixed(2) + '%']}
              />
              <Legend />
              <Bar dataKey="precision" fill="var(--accent)" name="Precision" />
              <Bar dataKey="recall" fill="var(--purple)" name="Recall" />
              <Bar dataKey="f1" fill="var(--green)" name="F1 Score" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
