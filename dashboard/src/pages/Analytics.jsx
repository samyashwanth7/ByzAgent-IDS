import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Loader2 } from 'lucide-react';

const Analytics = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8000/analytics');
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const result = await response.json();
        setData(result);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="animate-fade-in" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <Loader2 className="spin" size={48} color="var(--accent-cyan)" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="animate-fade-in">
        <h2>Analytics</h2>
        <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
          <p style={{ color: 'var(--status-critical)' }}>Failed to load data: {error}</p>
        </div>
      </div>
    );
  }

  if (!data) return null;

  // Render Confusion Matrix
  const renderConfusionMatrix = () => {
    const { confusion_matrix, class_names } = data;
    const numClasses = class_names.length;
    
    // Find maximum count for log scaling
    const maxCount = Math.max(...confusion_matrix.flat());
    const logMax = Math.log(maxCount + 1);
    
    return (
      <div className="card" style={{ marginBottom: '32px' }}>
        <h3 style={{ marginBottom: '24px' }}>Confusion Matrix (8-Class)</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', overflowX: 'auto' }}>
          <div style={{ display: 'flex' }}>
            <div style={{ width: '100px', flexShrink: 0 }}></div>
            <div className="cm-grid" style={{ gridTemplateColumns: `repeat(${numClasses}, 1fr)` }}>
              {class_names.map((name, i) => (
                <div key={`col-${i}`} className="cm-header" title={name}>{name.length > 4 ? name.substring(0, 4) : name}</div>
              ))}
            </div>
          </div>
          
          <div style={{ display: 'flex' }}>
            <div style={{ width: '100px', flexShrink: 0, display: 'flex', flexDirection: 'column', gap: '2px' }}>
              {class_names.map((name, i) => (
                <div key={`row-lbl-${i}`} className="cm-row-label" style={{ minHeight: '48px' }}>
                  {name}
                </div>
              ))}
            </div>
            
            <div className="cm-grid" style={{ gridTemplateColumns: `repeat(${numClasses}, 1fr)` }}>
              {confusion_matrix.map((row, i) => (
                row.map((count, j) => {
                  const isDiagonal = i === j;
                  const intensity = Math.max(0.1, Math.min(1, Math.log(count + 1) / logMax));
                  
                  // Color scheme: cyan/blue for diagonal, red for off-diagonal
                  const backgroundColor = isDiagonal 
                    ? `rgba(0, 240, 255, ${intensity})` 
                    : `rgba(239, 68, 68, ${intensity})`;
                    
                  return (
                    <div key={`cell-${i}-${j}`} className="cm-cell" style={{ backgroundColor }} title={`True: ${class_names[i]}\nPredicted: ${class_names[j]}\nCount: ${count}`}>
                      {count}
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

  const accuracyPercent = (data.overall_accuracy * 100).toFixed(2);

  return (
    <div className="animate-fade-in">
      <h1>Analytics</h1>
      
      <div className="stats-grid">
        <div className="card">
          <div className="stat-label">Overall Accuracy</div>
          <div className="stat-value">{accuracyPercent}%</div>
        </div>
        <div className="card">
          <div className="stat-label">Differential Privacy</div>
          <div className="stat-value" style={{ color: data.dp_enabled ? 'var(--status-warning)' : 'var(--text-secondary)' }}>
            {data.dp_enabled ? `ε = ${data.dp_epsilon}` : 'Disabled'}
          </div>
        </div>
        <div className="card">
          <div className="stat-label">Number of Classes</div>
          <div className="stat-value" style={{ color: 'var(--text-primary)' }}>{data.class_names.length}</div>
        </div>
      </div>

      {renderConfusionMatrix()}

      <div className="card" style={{ height: '600px' }}>
        <h3 style={{ marginBottom: '24px' }}>Per-Class Performance Metrics</h3>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            layout="vertical"
            data={data.per_class_metrics}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" horizontal={false} />
            <XAxis type="number" domain={[0, 1]} tick={{ fill: 'var(--text-secondary)' }} />
            <YAxis dataKey="name" type="category" width={100} tick={{ fill: 'var(--text-secondary)' }} />
            <Tooltip 
              contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border-color)' }}
              itemStyle={{ color: 'var(--text-primary)' }}
            />
            <Legend />
            <Bar dataKey="precision" name="Precision" fill="var(--accent-cyan)" />
            <Bar dataKey="recall" name="Recall" fill="var(--accent-blue)" />
            <Bar dataKey="f1" name="F1 Score" fill="var(--status-good)" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default Analytics;
