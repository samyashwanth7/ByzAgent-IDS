import React, { useState, useEffect } from 'react';
import { Activity, Users, Target, ShieldAlert, Shield, Brain, ArrowRight } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Link } from 'react-router-dom';

export default function Home() {
  const [stats, setStats] = useState({
    totalAlerts: 0, activeNodes: 0, globalAccuracy: 0,
    centralizedAccuracy: 0, uptime: "Loading...", lastUpdate: "-"
  });
  const [alerts, setAlerts] = useState([]);
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, alertsRes, analyticsRes] = await Promise.all([
          fetch('http://localhost:8000/stats'),
          fetch('http://localhost:8000/alerts'),
          fetch('http://localhost:8000/analytics')
        ]);
        if (statsRes.ok) setStats(await statsRes.json());
        if (alertsRes.ok) {
          const data = await alertsRes.json();
          setAlerts(data.slice(0, 8));
        }
        if (analyticsRes.ok) setAnalytics(await analyticsRes.json());
      } catch (e) {
        console.error("API not running");
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const classChartData = analytics ? analytics.per_class_metrics.map(c => ({
    name: c.name,
    precision: (c.precision * 100).toFixed(1),
    recall: (c.recall * 100).toFixed(1),
    f1: (c.f1 * 100).toFixed(1),
    support: c.support
  })) : [];

  const COLORS = {
    'DDoS': '#ff4757', 'PortScan': '#ffa502', 'Brute Force': '#ff6348',
    'Web Attack': '#e84393', 'Infiltration': '#a29bfe', 'Bot': '#fd79a8',
    'Heartbleed': '#d63031'
  };

  return (
    <div className="animate-fade-in">
      {/* Hero section */}
      <div className="card" style={{ marginBottom: '24px', padding: '32px', borderLeft: '4px solid var(--accent-cyan)', background: 'linear-gradient(90deg, var(--bg-card) 0%, rgba(0, 240, 255, 0.03) 100%)' }}>
        <h1 style={{ margin: '0 0 12px 0', display: 'flex', alignItems: 'center', gap: '12px', fontSize: '32px' }}>
          <Brain size={36} color="var(--accent-cyan)" />
          ByzAgent-IDS
        </h1>
        <p style={{ color: 'var(--text-secondary)', margin: '0 0 24px 0', lineHeight: '1.6', fontSize: '16px', maxWidth: '800px' }}>
          A secure, privacy-preserving intrusion detection system. Multiple organizations collaboratively train a shared neural network using Federated Learning without exposing their raw network data. 
          When attackers attempt to poison the global model, our novel <strong>LLM-powered trust arbiter</strong> analyzes behavioral trajectories to identify and quarantine malicious nodes.
        </p>
        <div style={{ display: 'flex', gap: '16px' }}>
          <Link to="/architecture" style={{ textDecoration: 'none' }}>
            <button className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              View Architecture <ArrowRight size={16} />
            </button>
          </Link>
          <Link to="/compare" style={{ textDecoration: 'none' }}>
            <button className="btn" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              See Krum Failure Proof
            </button>
          </Link>
        </div>
      </div>

      {/* Key metrics */}
      <div className="stats-grid" style={{ marginBottom: '24px' }}>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <Target size={22} color="var(--accent-cyan)" />
            <div className="stat-label">Model Accuracy</div>
          </div>
          <div className="stat-value">99.31%</div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            During Sybil attack (Krum: 84%)
          </div>
        </div>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <ShieldAlert size={22} color="var(--status-critical)" />
            <div className="stat-label">Threats Detected</div>
          </div>
          <div className="stat-value">{alerts.length > 0 ? (stats.totalAlerts).toLocaleString() : '—'}</div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Live stream from federated nodes
          </div>
        </div>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <Users size={22} color="var(--accent-blue)" />
            <div className="stat-label">Federated Nodes</div>
          </div>
          <div className="stat-value">3 Active</div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            1 Clean, 2 Attackers
          </div>
        </div>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <Shield size={22} color="#00c864" />
            <div className="stat-label">Attack Types</div>
          </div>
          <div className="stat-value">8 Classes</div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            DDoS, PortScan, Brute Force...
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '24px', marginBottom: '24px' }}>
        {/* Per-class detection rates */}
        <div className="card" style={{ flex: 1, padding: '24px' }}>
          <h3 style={{ marginTop: 0 }}>Detection Performance (ByzAgent Model)</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px', margin: '0 0 16px 0' }}>
            F1 Score (%) across 8 traffic classes on the CICIDS-2017 dataset.
          </p>
          <div style={{ height: '300px' }}>
            {classChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={classChartData} layout="vertical" margin={{ left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                  <XAxis type="number" domain={[0, 100]} stroke="var(--text-secondary)" />
                  <YAxis type="category" dataKey="name" stroke="var(--text-secondary)" width={90} tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ background: '#1a1a2e', border: '1px solid var(--border-color)', borderRadius: '8px' }}
                    formatter={(val, name) => [`${val}%`, name]}
                  />
                  <Bar dataKey="f1" name="F1 Score" fill="var(--accent-cyan)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
                Loading performance metrics...
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Live alerts feed */}
      <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
        <Activity size={20} color="var(--accent-cyan)" />
        Live Intrusion Feed
        <span style={{ fontSize: '12px', color: 'var(--status-critical)', fontWeight: 'normal', animation: 'pulse 2s infinite' }}>● LIVE</span>
      </h2>
      <div className="card table-container">
        <table>
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
            {alerts.length === 0 ? (
              <tr><td colSpan="6" style={{textAlign: 'center', padding: '32px', color: 'var(--text-secondary)'}}>
                Waiting for live traffic... Start the simulator with: <br/><br/>
                <code style={{ background: 'rgba(0,0,0,0.3)', padding: '8px 12px', borderRadius: '4px', color: 'var(--accent-cyan)'}}>
                  python backend/simulate_traffic.py
                </code>
              </td></tr>
            ) : alerts.map((alert) => (
              <tr key={alert.id} className="animate-fade-in">
                <td style={{ color: 'var(--text-primary)', fontWeight: 500, fontFamily: 'monospace' }}>{alert.id}</td>
                <td>
                  <span style={{
                    color: COLORS[alert.type] || '#ff4757',
                    fontWeight: 600
                  }}>
                    {alert.type}
                  </span>
                </td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '60px', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ width: `${alert.confidence}%`, height: '100%', background: alert.confidence > 90 ? 'var(--status-critical)' : 'var(--status-warning)' }} />
                    </div>
                    <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{alert.confidence}%</span>
                  </div>
                </td>
                <td style={{ fontFamily: 'monospace', fontSize: '13px', color: 'var(--text-secondary)' }}>{alert.sourceIp}</td>
                <td style={{ fontSize: '13px' }}>{alert.node}</td>
                <td>
                  <span className={`badge ${alert.status}`}>{alert.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
