import React, { useState, useEffect } from 'react';
import { accuracyComparison } from '../mockData';
import { Activity, Users, Target, ShieldAlert } from 'lucide-react';

export default function Home() {
  const [stats, setStats] = useState({
    totalAlerts: 0,
    activeNodes: 0,
    globalAccuracy: 0,
    centralizedAccuracy: 0,
    uptime: "Loading...",
    lastUpdate: "-"
  });
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const statsRes = await fetch('http://localhost:8000/stats');
        if (statsRes.ok) setStats(await statsRes.json());
        
        const alertsRes = await fetch('http://localhost:8000/alerts');
        if (alertsRes.ok) {
          const data = await alertsRes.json();
          setAlerts(data.slice(0, 5)); // Show top 5 on home
        }
      } catch (e) {
        console.error("API not running");
      }
    };
    
    fetchData();
    const interval = setInterval(fetchData, 1000); // Poll every second for live simulation
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="animate-fade-in">
      <h1>Dashboard Overview (Live)</h1>
      
      <div className="stats-grid">
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
            <Target size={24} color="var(--accent-cyan)" />
            <div className="stat-label">Federated Accuracy</div>
          </div>
          <div className="stat-value">{stats.globalAccuracy}%</div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Centralized bound: {stats.centralizedAccuracy}%
          </div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
            <ShieldAlert size={24} color="var(--status-critical)" />
            <div className="stat-label">Total Threats Blocked</div>
          </div>
          <div className="stat-value">{stats.totalAlerts.toLocaleString()}</div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Last Update: {stats.lastUpdate}
          </div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
            <Users size={24} color="var(--accent-blue)" />
            <div className="stat-label">Active Federated Nodes</div>
          </div>
          <div className="stat-value">{stats.activeNodes}</div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Hospital, Bank, University
          </div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
            <Activity size={24} color="var(--status-good)" />
            <div className="stat-label">System Uptime</div>
          </div>
          <div className="stat-value">{stats.uptime}</div>
        </div>
      </div>

      <h2>Recent Intrusions</h2>
      <div className="card table-container">
        <table>
          <thead>
            <tr>
              <th>Alert ID</th>
              <th>Type</th>
              <th>Confidence</th>
              <th>Source IP</th>
              <th>Node</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {alerts.length === 0 ? (
              <tr><td colSpan="6" style={{textAlign: 'center', padding: '20px'}}>No alerts yet... Waiting for live traffic.</td></tr>
            ) : alerts.map((alert) => (
              <tr key={alert.id} className="animate-fade-in">
                <td style={{ color: 'var(--accent-cyan)', fontWeight: 500 }}>{alert.id}</td>
                <td>{alert.type}</td>
                <td>{alert.confidence}%</td>
                <td>{alert.sourceIp}</td>
                <td>{alert.node}</td>
                <td>
                  <span className={`badge ${alert.status}`}>
                    {alert.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

