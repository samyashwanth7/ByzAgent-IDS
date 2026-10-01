import React, { useState, useEffect } from 'react';
import { Activity } from 'lucide-react';

const MOCK = [
  { id: 'AL-1050', type: 'DDoS', confidence: 99.1, sourceIp: '192.168.1.50', node: 'Hospital-Node-1', status: 'critical' },
  { id: 'AL-1051', type: 'PortScan', confidence: 97.2, sourceIp: '10.0.0.12', node: 'Bank-Node-2', status: 'critical' },
  { id: 'AL-1052', type: 'Brute Force', confidence: 94.3, sourceIp: '172.16.0.100', node: 'Uni-Node-3', status: 'warning' },
  { id: 'AL-1053', type: 'Bot', confidence: 88.5, sourceIp: '192.168.2.33', node: 'Hospital-Node-1', status: 'warning' },
  { id: 'AL-1054', type: 'Web Attack', confidence: 91.8, sourceIp: '10.0.1.55', node: 'Bank-Node-2', status: 'critical' },
  { id: 'AL-1055', type: 'Infiltration', confidence: 86.1, sourceIp: '172.16.1.20', node: 'Uni-Node-3', status: 'warning' },
];

export default function LiveDemo() {
  const [alerts, setAlerts] = useState(MOCK);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await fetch('http://localhost:8000/alerts');
        if (!res.ok) {
          throw new Error('API request failed');
        }
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          setAlerts(data);
        } else {
          setAlerts(MOCK);
        }
      } catch {
        setAlerts(MOCK);
      }
    };

    fetchAlerts();
    const interval = setInterval(fetchAlerts, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="section" id="demo">
      <div className="divider" style={{ marginBottom: '120px' }} />

      <div className="glow-cyan" style={{ top: '80px', right: '-150px' }} />

      <div className="section-label">
        <span>04</span> Live Demo
      </div>

      <h2 className="heading-lg" style={{ marginBottom: '16px' }}>
        Real-time <span className="serif">intrusion detection.</span>
      </h2>

      <p className="subtitle" style={{ marginBottom: '40px' }}>
        Live network packet classification streaming against the ByzAgent-defended global model. Start the background traffic simulator to stream real-time attack flows across federated nodes.
      </p>

      <div className="card" style={{ padding: '28px', overflowX: 'auto', position: 'relative', zIndex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Activity size={20} color="var(--accent)" className="pulse" />
            <span style={{ fontWeight: 600, fontSize: '16px' }}>Live Alert Feed</span>
          </div>
          <span className="badge badge-cyan" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--green)', display: 'inline-block' }} />
            Live Stream
          </span>
        </div>

        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th>Alert ID</th>
              <th>Attack Type</th>
              <th>Confidence</th>
              <th>Source IP</th>
              <th>Node</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {alerts.slice(0, 8).map((alert) => (
              <tr key={alert.id}>
                <td style={{ fontFamily: 'monospace', color: 'var(--accent)' }}>
                  {alert.id}
                </td>
                <td style={{ fontWeight: 600, color: 'var(--red)' }}>
                  {alert.type}
                </td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div
                      style={{
                        width: '60px',
                        height: '5px',
                        borderRadius: '3px',
                        background: 'rgba(255, 255, 255, 0.1)',
                        overflow: 'hidden'
                      }}
                    >
                      <div
                        style={{
                          width: `${Math.min(alert.confidence, 100)}%`,
                          height: '100%',
                          background: alert.confidence > 90 ? 'var(--red)' : 'var(--orange)',
                          borderRadius: '3px'
                        }}
                      />
                    </div>
                    <span style={{ fontSize: '13px' }}>
                      {typeof alert.confidence === 'number' ? alert.confidence.toFixed(1) : alert.confidence}%
                    </span>
                  </div>
                </td>
                <td style={{ fontFamily: 'monospace', color: 'var(--text-secondary)' }}>
                  {alert.sourceIp}
                </td>
                <td style={{ color: 'var(--text)' }}>
                  {alert.node}
                </td>
                <td>
                  <span className={`badge ${alert.status === 'critical' ? 'badge-red' : 'badge-orange'}`}>
                    {alert.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <p style={{ marginTop: '24px', fontSize: '13px', color: 'var(--text-secondary)' }}>
          Run <code style={{ fontFamily: 'monospace', color: 'var(--accent)' }}>python backend/simulate_traffic.py</code> to see live traffic from all 8 attack classes
        </p>
      </div>
    </section>
  );
}
