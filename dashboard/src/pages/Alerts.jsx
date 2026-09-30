import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { RefreshCw, Shield } from 'lucide-react';

export default function Alerts() {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({});
  const [feedbackMsg, setFeedbackMsg] = useState(null);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await fetch('http://localhost:8000/alerts');
        if (res.ok) setAlerts(await res.json());
        const statsRes = await fetch('http://localhost:8000/stats');
        if (statsRes.ok) setStats(await statsRes.json());
      } catch (e) {
        console.error("API not running");
      }
    };
    
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 1000);
    return () => clearInterval(interval);
  }, []);

  const sendFeedback = async (alertId, verdict) => {
    try {
      const res = await fetch('http://localhost:8000/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ alert_id: alertId, verdict })
      });
      const data = await res.json();
      setFeedbackMsg(`${data.message} (${data.total_feedback_samples} total samples)`);
      setTimeout(() => setFeedbackMsg(null), 3000);
    } catch (e) {
      setFeedbackMsg("Error sending feedback");
    }
  };

  const triggerRetrain = async () => {
    try {
      const res = await fetch('http://localhost:8000/retrain', { method: 'POST' });
      const data = await res.json();
      setFeedbackMsg(data.message);
      setTimeout(() => setFeedbackMsg(null), 5000);
    } catch (e) {
      setFeedbackMsg("Error triggering retrain");
    }
  };

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Shield size={28} color="var(--accent-cyan)" /> 
          Live Intrusion Feed
        </h1>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {stats.feedbackCount > 0 && (
            <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              {stats.feedbackCount} feedback samples
            </span>
          )}
          <button 
            className="btn btn-primary" 
            onClick={triggerRetrain}
            disabled={stats.isRetraining}
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <RefreshCw size={14} className={stats.isRetraining ? 'spin' : ''} />
            {stats.isRetraining ? 'Retraining...' : 'Retrain Model'}
          </button>
        </div>
      </div>

      <div style={{ background: 'rgba(0, 240, 255, 0.02)', border: '1px solid rgba(0, 240, 255, 0.15)', padding: '16px', borderRadius: '8px', color: 'var(--text-secondary)', marginBottom: '24px' }}>
        This feed shows real network packets being classified by the robust ByzAgent model in real-time. 
        To see traffic flowing, run <code style={{ color: 'var(--accent-cyan)' }}>python backend/simulate_traffic.py</code> in your terminal.
      </div>

      {feedbackMsg && (
        <div className="card" style={{ marginBottom: '16px', padding: '12px 16px', borderLeft: '3px solid var(--accent-cyan)', fontSize: '14px' }}>
          {feedbackMsg}
        </div>
      )}

      {stats.modelVersion && (
        <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
          Model: {stats.modelVersion} | Accuracy: {stats.globalAccuracy}%
        </div>
      )}
      
      <div className="card table-container">
        <table>
          <thead>
            <tr>
              <th>Alert ID</th>
              <th>Type</th>
              <th>Confidence</th>
              <th>Source IP</th>
              <th>Node</th>
              <th>Verdict</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {alerts.length === 0 ? (
              <tr><td colSpan="7" style={{textAlign: 'center', padding: '20px'}}>Monitoring network... no alerts currently.</td></tr>
            ) : alerts.map((alert) => (
              <tr key={alert.id} className="animate-fade-in">
                <td style={{ color: 'var(--accent-cyan)', fontWeight: 500 }}>{alert.id}</td>
                <td style={{ color: alert.type === 'BENIGN' ? '#00c864' : 'var(--status-critical)', fontWeight: 600 }}>{alert.type}</td>
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
                  {alert.analyst_verdict === 'confirmed' && (
                    <span className="badge critical">Confirmed</span>
                  )}
                  {alert.analyst_verdict === 'false_positive' && (
                    <span className="badge" style={{ background: 'rgba(0, 200, 100, 0.15)', color: '#00c864' }}>FP</span>
                  )}
                  {!alert.analyst_verdict && (
                    <span style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>Pending</span>
                  )}
                </td>
                <td>
                  <div style={{ display: 'flex', gap: '6px' }}>
                    <button 
                      className="btn" 
                      style={{ padding: '4px 8px', fontSize: '11px' }}
                      onClick={() => navigate(`/explain?alertId=${alert.id}`)}
                    >
                      Explain
                    </button>
                    {!alert.analyst_verdict && (
                      <>
                        <button 
                          className="btn" 
                          style={{ padding: '4px 8px', fontSize: '11px', borderColor: 'var(--status-critical)', color: 'var(--status-critical)' }}
                          onClick={() => sendFeedback(alert.id, 'confirm_attack')}
                        >
                          Confirm
                        </button>
                        <button 
                          className="btn" 
                          style={{ padding: '4px 8px', fontSize: '11px', borderColor: '#00c864', color: '#00c864' }}
                          onClick={() => sendFeedback(alert.id, 'false_positive')}
                        >
                          FP
                        </button>
                      </>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

