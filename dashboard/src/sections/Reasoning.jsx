import React, { useState, useEffect } from 'react';
import { Brain, ShieldCheck, ShieldAlert, Shield, TrendingUp } from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend
} from 'recharts';

export default function Reasoning() {
  const [rounds, setRounds] = useState([]);
  const [historyData, setHistoryData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 1. Fetch real decisions
    fetch('http://localhost:8000/byzagent/decisions')
      .then((res) => {
        if (!res.ok) throw new Error('API offline');
        return res.json();
      })
      .then((data) => {
        const list = Array.isArray(data) ? data : (data?.data || []);
        if (list.length > 0) setRounds([...list].reverse());
      })
      .catch(() => {
        fetch('/data/decisions.json')
          .then(res => res.json())
          .then(data => {
            const list = Array.isArray(data) ? data : (data?.data || []);
            if (list.length > 0) setRounds([...list].reverse());
          })
          .catch(err => console.warn('Could not load decisions.json:', err));
      });

    // 2. Fetch history for Client Behaviour chart (C3)
    fetch('http://localhost:8000/byzagent/history')
      .then(res => res.json())
      .then(data => processHistory(data))
      .catch(() => {
        fetch('/data/history.json')
          .then(res => res.json())
          .then(data => processHistory(data))
          .catch(err => console.warn('Could not load history.json:', err));
      })
      .finally(() => setLoading(false));
  }, []);

  const processHistory = (rawHist) => {
    if (!rawHist || typeof rawHist !== 'object') return;
    const c0 = rawHist.client_0 || [];
    const c1 = rawHist.client_1 || [];
    const c2 = rawHist.client_2 || [];

    const numRounds = Math.max(c0.length, c1.length, c2.length);
    const chart = [];
    for (let i = 0; i < numRounds; i++) {
      chart.push({
        round: i + 1,
        'Client 0 (Honest) Loss': c0[i]?.local_loss != null ? +c0[i].local_loss.toFixed(4) : null,
        'Client 1 (Attacker) Loss': c1[i]?.local_loss != null ? +c1[i].local_loss.toFixed(4) : null,
        'Client 2 (Attacker) Loss': c2[i]?.local_loss != null ? +c2[i].local_loss.toFixed(4) : null,
        'Client 0 (Honest) Val Acc': c0[i]?.val_accuracy != null ? +(c0[i].val_accuracy * 100).toFixed(2) : null,
        'Client 1 (Attacker) Val Acc': c1[i]?.val_accuracy != null ? +(c1[i].val_accuracy * 100).toFixed(2) : null,
        'Client 2 (Attacker) Val Acc': c2[i]?.val_accuracy != null ? +(c2[i].val_accuracy * 100).toFixed(2) : null,
      });
    }
    setHistoryData(chart);
  };

  const getDecisionClass = (decision) => {
    const d = (decision || '').toLowerCase();
    if (d === 'quarantine') return 'quarantine';
    if (d === 'trust') return 'trust';
    if (d === 'downweight') return 'downweight';
    return '';
  };

  const renderBadge = (decision) => {
    const d = (decision || '').toLowerCase();
    const text = (decision || '').toUpperCase();
    if (d === 'trust') {
      return (
        <span className="badge badge-green">
          <ShieldCheck size={14} />
          {text}
        </span>
      );
    }
    if (d === 'downweight') {
      return (
        <span className="badge badge-orange">
          <Shield size={14} />
          {text}
        </span>
      );
    }
    if (d === 'quarantine') {
      return (
        <span className="badge badge-red">
          <ShieldAlert size={14} />
          {text}
        </span>
      );
    }
    return (
      <span className="badge">
        <Shield size={14} />
        {decision}
      </span>
    );
  };

  return (
    <section className="section" id="reasoning">
      <div className="divider" style={{ marginBottom: '120px' }} />

      <div className="section-label">
        <span>05</span> Agent Reasoning Log
      </div>

      <h2 className="heading-lg" style={{ marginBottom: '16px' }}>
        The LLM's <span className="serif">actual thought process.</span>
      </h2>

      <p className="subtitle" style={{ marginBottom: '48px' }}>
        Each round, the server sends client behavioral stats and recent trajectory as JSON to the LLM. Here is what the agent decided — and why.
      </p>

      {/* C3 Requirement: Client Behaviour Card */}
      {historyData.length > 0 && (
        <div className="card" style={{ marginBottom: '40px', padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <TrendingUp size={20} color="var(--accent)" />
              <h3 style={{ fontSize: '18px', fontWeight: 600 }}>Client Behavioral Trajectory (Across Rounds)</h3>
            </div>
            <span className="badge badge-cyan">Temporal Evidence</span>
          </div>

          <div style={{ width: '100%', height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={historyData} margin={{ top: 10, right: 20, left: -10, bottom: 10 }}>
                <CartesianGrid stroke="rgba(255, 255, 255, 0.05)" strokeDasharray="3 3" />
                <XAxis dataKey="round" stroke="var(--text-secondary)" label={{ value: 'Round', position: 'insideBottom', offset: -5 }} />
                <YAxis yAxisId="left" stroke="var(--text-secondary)" tickFormatter={(v) => `${v}%`} domain={[0, 100]} />
                <YAxis yAxisId="right" orientation="right" stroke="var(--text-secondary)" domain={[0, 'auto']} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: '8px' }}
                />
                <Legend verticalAlign="top" wrapperStyle={{ paddingBottom: '10px' }} />
                <Line yAxisId="left" type="monotone" dataKey="Client 0 (Honest) Val Acc" stroke="#22c55e" strokeWidth={2.5} dot={{ r: 3 }} />
                <Line yAxisId="left" type="monotone" dataKey="Client 1 (Attacker) Val Acc" stroke="#ef4444" strokeWidth={2} strokeDasharray="3 3" dot={{ r: 3 }} />
                <Line yAxisId="left" type="monotone" dataKey="Client 2 (Attacker) Val Acc" stroke="#f97316" strokeWidth={2} strokeDasharray="3 3" dot={{ r: 3 }} />
                <Line yAxisId="right" type="monotone" dataKey="Client 0 (Honest) Loss" stroke="#00F0FF" strokeWidth={1.5} dot={false} />
                <Line yAxisId="right" type="monotone" dataKey="Client 1 (Attacker) Loss" stroke="#f43f5e" strokeWidth={1.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <p style={{ marginTop: '14px', fontSize: '13px', color: 'var(--text-secondary)' }}>
            Validation accuracy (solid green: honest, dashed red/orange: attackers) demonstrates the divergence that enables ByzAgent to identify label-poisoning attacks.
          </p>
        </div>
      )}

      {/* Decision Timeline */}
      <div className="reasoning-list">
        {rounds.map((roundItem, rIdx) => (
          <div className="reasoning-card" key={roundItem.round ?? rIdx}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Brain size={18} color="var(--accent)" />
                <span style={{ color: 'var(--accent)', fontWeight: 700, fontSize: '16px' }}>
                  Round {roundItem.round}
                </span>
              </div>
            </div>

            {roundItem.decisions && roundItem.decisions.map((item, dIdx) => {
              const decisionClass = getDecisionClass(item.decision);
              const rowClassName = decisionClass ? `decision-row ${decisionClass}` : 'decision-row';

              return (
                <div className={rowClassName} key={item.client_id || dIdx}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontFamily: 'monospace', fontWeight: 'bold', fontSize: '14px' }}>
                      {item.client_id}
                    </span>
                    {renderBadge(item.decision)}
                  </div>
                  <p
                    className="text-secondary italic"
                    style={{
                      fontStyle: 'italic',
                      color: 'var(--text-secondary)',
                      margin: 0,
                      fontSize: '13px',
                      lineHeight: '1.6'
                    }}
                  >
                    {item.explanation}
                  </p>
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </section>
  );
}
