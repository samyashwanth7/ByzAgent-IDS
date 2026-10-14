import React, { useState, useEffect } from 'react';
import { Activity } from 'lucide-react';

export default function LiveDemo() {
  const [allAlerts, setAllAlerts] = useState([]);
  const [displayAlerts, setDisplayAlerts] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(8);

  useEffect(() => {
    // Attempt local backend first, fallback to static /data/alerts.json
    fetch('http://localhost:8000/alerts')
      .then(res => {
        if (!res.ok) throw new Error('API offline');
        return res.json();
      })
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          setAllAlerts(data);
          setDisplayAlerts(data.slice(0, 8));
        } else {
          throw new Error('Empty API data');
        }
      })
      .catch(() => {
        fetch('/data/alerts.json')
          .then(res => res.json())
          .then(data => {
            if (Array.isArray(data) && data.length > 0) {
              setAllAlerts(data);
              setDisplayAlerts(data.slice(0, 8));
            }
          })
          .catch(err => console.warn('Could not load alerts.json:', err));
      });
  }, []);

  // Cycle one row every 1.5 seconds from real test-set evaluations
  useEffect(() => {
    if (allAlerts.length <= 8) return;

    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => {
        const nextIndex = (prevIndex + 1) % allAlerts.length;
        const start = Math.max(0, nextIndex - 7);
        const window = nextIndex < 8 
          ? allAlerts.slice(0, 8) 
          : allAlerts.slice(start, nextIndex + 1);
        setDisplayAlerts(window);
        return nextIndex;
      });
    }, 1500);

    return () => clearInterval(interval);
  }, [allAlerts]);

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
        Packet classification streaming against the ByzAgent-defended global model across federated nodes.
      </p>

      <div className="card" style={{ padding: '28px', overflowX: 'auto', position: 'relative', zIndex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Activity size={20} color="var(--accent)" className="pulse" />
            <span style={{ fontWeight: 600, fontSize: '16px' }}>
              Replay of real test-set predictions
            </span>
          </div>
          <span className="badge badge-cyan" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--green)', display: 'inline-block' }} />
            Active Stream
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
            {displayAlerts.map((alert) => (
              <tr key={alert.id}>
                <td style={{ fontFamily: 'monospace', color: 'var(--accent)' }}>
                  {alert.id}
                </td>
                <td style={{ fontWeight: 600, color: alert.type === 'BENIGN' ? 'var(--green)' : 'var(--red)' }}>
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
                          background: alert.type === 'BENIGN' ? 'var(--green)' : (alert.confidence > 90 ? 'var(--red)' : 'var(--orange)'),
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
                  <span className={`badge ${alert.status === 'normal' ? 'badge-green' : (alert.status === 'critical' ? 'badge-red' : 'badge-orange')}`}>
                    {alert.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <p style={{ marginTop: '24px', fontSize: '13px', color: 'var(--text-secondary)' }}>
          Real evaluation stream from held-out test data processed by the trained model.
        </p>
      </div>
    </section>
  );
}
