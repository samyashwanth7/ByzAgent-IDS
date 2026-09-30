import React, { useState, useEffect } from 'react';
import { Shield, ShieldAlert, ShieldCheck, Brain, TrendingDown, Activity } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function ByzAgentView() {
  const [rounds, setRounds] = useState([]);
  const [history, setHistory] = useState({});

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [decRes, histRes] = await Promise.all([
          fetch('http://localhost:8000/byzagent/decisions'),
          fetch('http://localhost:8000/byzagent/history')
        ]);
        if (decRes.ok) {
          const data = await decRes.json();
          setRounds((data.data || []).slice().reverse());
        }
        if (histRes.ok) {
          const data = await histRes.json();
          setHistory(data.data || {});
        }
      } catch (e) {
        console.error("ByzAgent API not running");
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  // Build chart data from history
  const chartData = [];
  if (history.client_0) {
    history.client_0.forEach((stat, i) => {
      const row = { round: stat.round };
      Object.keys(history).forEach(cid => {
        if (history[cid][i]) {
          row[cid + '_acc'] = (history[cid][i].val_accuracy * 100).toFixed(1);
          row[cid + '_loss'] = history[cid][i].local_loss.toFixed(3);
        }
      });
      chartData.push(row);
    });
  }

  const getDecisionBadge = (decision) => {
    switch (decision?.toLowerCase()) {
      case 'quarantine':
        return <span className="badge critical" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><ShieldAlert size={12}/> QUARANTINE</span>;
      case 'trust':
        return <span className="badge" style={{ background: 'rgba(0, 200, 100, 0.15)', color: '#00c864', display: 'flex', alignItems: 'center', gap: '4px' }}><ShieldCheck size={12}/> TRUST</span>;
      case 'downweight':
        return <span className="badge warning" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Shield size={12}/> DOWNWEIGHT</span>;
      default:
        return <span className="badge">{decision}</span>;
    }
  };

  // Count decisions
  let totalQuarantine = 0, totalTrust = 0, totalDownweight = 0;
  rounds.forEach(r => {
    (r.decisions || []).forEach(d => {
      if (d.decision?.toLowerCase() === 'quarantine') totalQuarantine++;
      else if (d.decision?.toLowerCase() === 'trust') totalTrust++;
      else if (d.decision?.toLowerCase() === 'downweight') totalDownweight++;
    });
  });

  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Brain size={28} color="var(--accent-cyan)" />
          ByzAgent Trust Arbiter
        </h1>
        <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
          LLM-powered reasoning engine analyzing client behavior each federated round.
        </p>
      </div>

      {/* Stats cards */}
      <div className="stats-grid" style={{ marginBottom: '24px' }}>
        <div className="card">
          <div className="stat-label">Rounds Analyzed</div>
          <div className="stat-value" style={{ color: 'var(--accent-cyan)' }}>{rounds.length}</div>
        </div>
        <div className="card">
          <div className="stat-label">Clients Quarantined</div>
          <div className="stat-value" style={{ color: 'var(--status-critical)' }}>{totalQuarantine}</div>
        </div>
        <div className="card">
          <div className="stat-label">Clients Trusted</div>
          <div className="stat-value" style={{ color: '#00c864' }}>{totalTrust}</div>
        </div>
        <div className="card">
          <div className="stat-label">Clients Downweighted</div>
          <div className="stat-value" style={{ color: 'var(--status-warning)' }}>{totalDownweight}</div>
        </div>
      </div>

      {/* How it decides visual */}
      <div className="card" style={{ marginBottom: '24px', padding: '24px', background: 'rgba(0, 240, 255, 0.02)', border: '1px solid rgba(0, 240, 255, 0.1)' }}>
        <h3 style={{ marginTop: 0, marginBottom: '16px', color: 'var(--text-primary)' }}>How the LLM Evaluates Trust</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <div style={{ padding: '16px', background: 'var(--bg-card)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <h4 style={{ margin: '0 0 8px 0', color: 'var(--accent-cyan)' }}>1. Update Norm</h4>
            <p style={{ margin: 0, fontSize: '13px', color: 'var(--text-secondary)' }}>Are the model weights changing drastically? (High norm = suspicious)</p>
          </div>
          <div style={{ padding: '16px', background: 'var(--bg-card)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <h4 style={{ margin: '0 0 8px 0', color: 'var(--accent-cyan)' }}>2. Cosine Similarity</h4>
            <p style={{ margin: 0, fontSize: '13px', color: 'var(--text-secondary)' }}>Does this update align with peers, or is it diverging?</p>
          </div>
          <div style={{ padding: '16px', background: 'var(--bg-card)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <h4 style={{ margin: '0 0 8px 0', color: 'var(--accent-cyan)' }}>3. Local Loss</h4>
            <p style={{ margin: 0, fontSize: '13px', color: 'var(--text-secondary)' }}>Is the client struggling to fit the data? (Poisoning increases loss)</p>
          </div>
          <div style={{ padding: '16px', background: 'var(--bg-card)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <h4 style={{ margin: '0 0 8px 0', color: 'var(--accent-cyan)' }}>4. Temporal History</h4>
            <p style={{ margin: 0, fontSize: '13px', color: 'var(--text-secondary)' }}>How has this client behaved over the past 5 rounds?</p>
          </div>
        </div>
      </div>

      {/* Accuracy chart */}
      {chartData.length > 0 && (
        <div className="card" style={{ marginBottom: '24px', padding: '20px' }}>
          <h3 style={{ marginTop: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <TrendingDown size={18} />
            Client Validation Accuracy Over Rounds
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px', margin: '0 0 16px 0' }}>
            Watch how poisoned clients (1 & 2) diverge from the clean client (0) as the attack intensifies.
          </p>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="round" stroke="var(--text-secondary)" label={{ value: 'Round', position: 'insideBottom', offset: -5 }} />
              <YAxis stroke="var(--text-secondary)" domain={[0, 100]} label={{ value: 'Accuracy %', angle: -90, position: 'insideLeft' }} />
              <Tooltip contentStyle={{ background: '#1a1a2e', border: '1px solid var(--border-color)' }} />
              <Legend />
              <Line type="monotone" dataKey="client_0_acc" name="Client 0 (Clean)" stroke="#00c864" strokeWidth={2} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="client_1_acc" name="Client 1 (Attacker)" stroke="#ff4757" strokeWidth={2} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="client_2_acc" name="Client 2 (Attacker)" stroke="#ff6b81" strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Loss chart */}
      {chartData.length > 0 && (
        <div className="card" style={{ marginBottom: '24px', padding: '20px' }}>
          <h3 style={{ marginTop: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity size={18} />
            Client Local Loss Over Rounds
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px', margin: '0 0 16px 0' }}>
            Poisoned clients struggle to fit their corrupted data, causing loss to spike.
          </p>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="round" stroke="var(--text-secondary)" label={{ value: 'Round', position: 'insideBottom', offset: -5 }} />
              <YAxis stroke="var(--text-secondary)" label={{ value: 'Loss', angle: -90, position: 'insideLeft' }} />
              <Tooltip contentStyle={{ background: '#1a1a2e', border: '1px solid var(--border-color)' }} />
              <Legend />
              <Line type="monotone" dataKey="client_0_loss" name="Client 0 (Clean)" stroke="#00c864" strokeWidth={2} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="client_1_loss" name="Client 1 (Attacker)" stroke="#ff4757" strokeWidth={2} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="client_2_loss" name="Client 2 (Attacker)" stroke="#ff6b81" strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Per-round decisions */}
      <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Brain size={20} />
        LLM Reasoning Log
      </h2>

      {rounds.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
          No ByzAgent decisions found. Run the federated experiment first.
        </div>
      ) : rounds.map((r, i) => (
        <div key={i} className="card" style={{ marginBottom: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px', marginBottom: '12px' }}>
            <h3 style={{ margin: 0, color: 'var(--accent-cyan)' }}>Round {r.round}</h3>
          </div>
          <div style={{ display: 'grid', gap: '12px' }}>
            {r.decisions && r.decisions.map((d, j) => (
              <div key={j} style={{
                background: 'rgba(255,255,255,0.02)',
                padding: '14px',
                borderRadius: '6px',
                borderLeft: d.decision?.toLowerCase() === 'quarantine'
                  ? '3px solid var(--status-critical)'
                  : d.decision?.toLowerCase() === 'downweight'
                    ? '3px solid var(--status-warning)'
                    : '3px solid #00c864'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <strong style={{ fontFamily: 'monospace', fontSize: '14px' }}>{d.client_id}</strong>
                  {getDecisionBadge(d.decision)}
                </div>
                <div style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.5', fontStyle: 'italic' }}>
                  "{d.explanation}"
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
