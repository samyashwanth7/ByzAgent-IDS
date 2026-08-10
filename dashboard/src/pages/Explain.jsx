import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { AlertCircle } from 'lucide-react';

export default function Explain() {
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const initialAlertId = queryParams.get('alertId');
  
  const [alerts, setAlerts] = useState([]);
  const [selectedAlert, setSelectedAlert] = useState(initialAlertId);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await fetch('http://localhost:8000/alerts');
        if (res.ok) {
          const data = await res.json();
          setAlerts(data);
          if (!selectedAlert && data.length > 0) {
            setSelectedAlert(data[0].id);
          }
        }
      } catch (e) {
        console.error("API not running");
      }
    };
    
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 1000); // Live poll
    return () => clearInterval(interval);
  }, [selectedAlert]);

  const alertInfo = alerts.find(a => a.id === selectedAlert);
  const currentShap = alertInfo?.shap || [];

  return (
    <div className="animate-fade-in">
      <h1>Model Explainability (SHAP)</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
        Understand exactly which network features triggered the alert. Positive values push the model toward predicting an attack.
      </p>

      <div style={{ display: 'flex', gap: '24px' }}>
        {/* Sidebar for selecting alerts */}
        <div className="card" style={{ width: '300px', height: '600px', overflowY: 'auto' }}>
          <h3>Live Alerts</h3>
          <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {alerts.length === 0 ? <p style={{color: 'var(--text-secondary)'}}>Waiting for alerts...</p> : alerts.map(alert => (
              <div 
                key={alert.id}
                onClick={() => setSelectedAlert(alert.id)}
                style={{
                  padding: '12px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  border: `1px solid ${selectedAlert === alert.id ? 'var(--accent-cyan)' : 'var(--border-color)'}`,
                  background: selectedAlert === alert.id ? 'rgba(0, 240, 255, 0.05)' : 'transparent'
                }}
              >
                <div style={{ fontWeight: 600 }}>{alert.id}</div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{alert.type} • Conf: {alert.confidence}%</div>
              </div>
            ))}
          </div>
        </div>

        {/* Main Chart Area */}
        <div className="card" style={{ flex: 1, height: '600px' }}>
          {alertInfo ? (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px', paddingBottom: '16px', borderBottom: '1px solid var(--border-color)' }}>
                <AlertCircle color="var(--status-critical)" />
                <div>
                  <h2>{alertInfo.id} - {alertInfo.type} Attack</h2>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
                    Source IP: {alertInfo.sourceIp} | Node: {alertInfo.node}
                  </div>
                </div>
              </div>

              <div style={{ height: '400px', width: '100%' }}>
                {currentShap.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={currentShap} layout="vertical" margin={{ top: 5, right: 30, left: 150, bottom: 5 }}>
                      <XAxis type="number" stroke="var(--text-secondary)" />
                      <YAxis dataKey="feature" type="category" stroke="var(--text-secondary)" width={150} />
                      <Tooltip />
                      <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                        {currentShap.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.value > 0 ? 'var(--status-critical)' : 'var(--accent-blue)'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
                    No SHAP data available for this alert.
                  </div>
                )}
              </div>
              
              <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', marginTop: '16px', fontSize: '14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '12px', height: '12px', background: 'var(--status-critical)', borderRadius: '2px' }} />
                  <span>Pushes toward ATTACK</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div style={{ width: '12px', height: '12px', background: 'var(--accent-blue)', borderRadius: '2px' }} />
                  <span>Pushes toward BENIGN</span>
                </div>
              </div>
            </>
          ) : (
             <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
                Select an alert to view its explanation.
             </div>
          )}
        </div>
      </div>
    </div>
  );
}
