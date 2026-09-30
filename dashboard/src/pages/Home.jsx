import React, { useState, useEffect } from 'react';
import { Activity, Users, Target, ShieldAlert, Shield, Brain, AlertTriangle, CheckCircle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

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

  // Build per-class detection data for chart
  const classChartData = analytics ? analytics.per_class_metrics.map(c => ({
    name: c.name,
    precision: (c.precision * 100).toFixed(1),
    recall: (c.recall * 100).toFixed(1),
    f1: (c.f1 * 100).toFixed(1),
    support: c.support
  })) : [];

  // Count attacks by type from live alerts
  const attackCounts = {};
  alerts.forEach(a => {
    attackCounts[a.type] = (attackCounts[a.type] || 0) + 1;
  });

  const COLORS = {
    'DDoS': '#ff4757', 'PortScan': '#ffa502', 'Brute Force': '#ff6348',
    'Web Attack': '#e84393', 'Infiltration': '#a29bfe', 'Bot': '#fd79a8',
    'Heartbleed': '#d63031'
  };

  return (
    <div className="animate-fade-in">
      {/* Hero section */}
      <div className="card" style={{ marginBottom: '24px', padding: '24px', borderLeft: '4px solid var(--accent-cyan)' }}>
        <h1 style={{ margin: '0 0 8px 0', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Brain size={28} color="var(--accent-cyan)" />
          ByzAgent — Federated Intrusion Detection
        </h1>
        <p style={{ color: 'var(--text-secondary)', margin: 0, lineHeight: '1.6' }}>
          Multiple organizations train a shared IDS model without exchanging private network data.
          An LLM-powered trust arbiter monitors each client's behavior and quarantines poisoned updates in real-time.
        </p>
      </div>

      {/* Key metrics */}
      <div className="stats-grid" style={{ marginBottom: '24px' }}>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <Target size={22} color="var(--accent-cyan)" />
            <div className="stat-label">Model Accuracy</div>
          </div>
          <div className="stat-value">{stats.globalAccuracy}%</div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            8-class classification on CICIDS-2017
          </div>
        </div>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <ShieldAlert size={22} color="var(--status-critical)" />
            <div className="stat-label">Threats Detected</div>
          </div>
          <div className="stat-value">{alerts.length > 0 ? alerts.length : '—'}</div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Live stream from {stats.activeNodes} federated nodes
          </div>
        </div>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <Users size={22} color="var(--accent-blue)" />
            <div className="stat-label">Federated Nodes</div>
          </div>
          <div className="stat-value">{stats.activeNodes}</div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Hospital · Bank · University
          </div>
        </div>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
            <Shield size={22} color="#00c864" />
            <div className="stat-label">Attack Types</div>
          </div>
          <div className="stat-value">8</div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            DDoS, PortScan, Brute Force, Bot...
          </div>
        </div>
      </div>

      {/* Per-class detection rates */}
      {classChartData.length > 0 && (
        <div className="card" style={{ marginBottom: '24px', padding: '20px' }}>
          <h3 style={{ marginTop: 0 }}>Detection Performance by Attack Type</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px', margin: '0 0 16px 0' }}>
            F1 Score (%) for each of the 8 traffic classes. The model detects DDoS, PortScan, Brute Force, Web Attacks, Infiltration, Bot, and Heartbleed.
          </p>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={classChartData} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis type="number" domain={[0, 100]} stroke="var(--text-secondary)" />
              <YAxis type="category" dataKey="name" stroke="var(--text-secondary)" width={90} tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{ background: '#1a1a2e', border: '1px solid var(--border-color)' }}
                formatter={(val, name) => [`${val}%`, name]}
              />
              <Legend />
              <Bar dataKey="f1" name="F1 Score" fill="var(--accent-cyan)" radius={[0, 4, 4, 0]} />
              <Bar dataKey="precision" name="Precision" fill="var(--accent-blue)" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Live alerts feed */}
      <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
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
              <tr><td colSpan="6" style={{textAlign: 'center', padding: '20px', color: 'var(--text-secondary)'}}>
                Waiting for live traffic... Start the simulator with: <code>python backend/simulate_traffic.py</code>
              </td></tr>
            ) : alerts.map((alert) => (
              <tr key={alert.id} className="animate-fade-in">
                <td style={{ color: 'var(--accent-cyan)', fontWeight: 500, fontFamily: 'monospace' }}>{alert.id}</td>
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
                    <div style={{ width: '50px', height: '5px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ width: `${alert.confidence}%`, height: '100%', background: alert.confidence > 90 ? 'var(--status-critical)' : 'var(--status-warning)', borderRadius: '3px' }} />
                    </div>
                    <span style={{ fontSize: '13px' }}>{alert.confidence}%</span>
                  </div>
                </td>
                <td style={{ fontFamily: 'monospace', fontSize: '13px' }}>{alert.sourceIp}</td>
                <td>{alert.node}</td>
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
