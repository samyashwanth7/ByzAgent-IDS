import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Alerts() {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await fetch('http://localhost:8000/alerts');
        if (res.ok) setAlerts(await res.json());
      } catch (e) {
        console.error("API not running");
      }
    };
    
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 1000); // Live poll
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h1>Network Alerts (Live stream)</h1>
        <button className="btn btn-primary">Export CSV</button>
      </div>
      
      <div className="card table-container">
        <table>
          <thead>
            <tr>
              <th>Alert ID</th>
              <th>Type</th>
              <th>Confidence</th>
              <th>Source IP</th>
              <th>Reporting Node</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {alerts.length === 0 ? (
              <tr><td colSpan="7" style={{textAlign: 'center', padding: '20px'}}>Monitoring network... no alerts currently.</td></tr>
            ) : alerts.map((alert) => (
              <tr key={alert.id} className="animate-fade-in">
                <td style={{ color: 'var(--accent-cyan)', fontWeight: 500 }}>{alert.id}</td>
                <td>{alert.type}</td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '60px', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ width: `${alert.confidence}%`, height: '100%', background: alert.confidence > 90 ? 'var(--status-critical)' : 'var(--status-warning)' }} />
                    </div>
                    <span>{alert.confidence}%</span>
                  </div>
                </td>
                <td style={{ fontFamily: 'monospace' }}>{alert.sourceIp}</td>
                <td>{alert.node}</td>
                <td>
                  <span className={`badge ${alert.status}`}>
                    {alert.status}
                  </span>
                </td>
                <td>
                  <button 
                    className="btn" 
                    style={{ padding: '4px 8px', fontSize: '12px' }}
                    onClick={() => navigate(`/explain?alertId=${alert.id}`)}
                  >
                    Explain
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
