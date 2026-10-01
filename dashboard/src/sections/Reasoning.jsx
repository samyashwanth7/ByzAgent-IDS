import React, { useState, useEffect } from 'react';
import { Brain, ShieldCheck, ShieldAlert, Shield } from 'lucide-react';

const FALLBACK = [
  { round: 10, decisions: [
    { client_id: 'client_0', decision: 'TRUST', explanation: 'Low loss (0.026) and high validation accuracy (0.99) indicate a clean, well-performing client.' },
    { client_id: 'client_1', decision: 'QUARANTINE', explanation: 'Very high loss (1.69) and near-zero validation accuracy (0.005) indicate this client is poisoning the model.' },
    { client_id: 'client_2', decision: 'QUARANTINE', explanation: 'Very high loss (1.69) and near-zero validation accuracy (0.006) confirm coordinated poisoning attack.' }
  ]},
  { round: 5, decisions: [
    { client_id: 'client_0', decision: 'TRUST', explanation: 'Consistent low loss and high accuracy across all rounds.' },
    { client_id: 'client_1', decision: 'DOWNWEIGHT', explanation: 'Loss is rising and accuracy dropping — early signs of label corruption.' },
    { client_id: 'client_2', decision: 'DOWNWEIGHT', explanation: 'Similar pattern to client_1, suggesting coordinated behavior.' }
  ]},
  { round: 1, decisions: [
    { client_id: 'client_0', decision: 'TRUST', explanation: 'Normal training metrics for a first round.' },
    { client_id: 'client_1', decision: 'TRUST', explanation: 'Metrics are within expected range for initial training.' },
    { client_id: 'client_2', decision: 'TRUST', explanation: 'No anomalies detected yet.' }
  ]}
];

export default function Reasoning() {
  const [rounds, setRounds] = useState(FALLBACK);

  useEffect(() => {
    fetch('http://localhost:8000/byzagent/decisions')
      .then((res) => {
        if (!res.ok) {
          throw new Error('Network response was not ok');
        }
        return res.json();
      })
      .then((data) => {
        if (data && Array.isArray(data.data) && data.data.length > 0) {
          setRounds([...data.data].reverse());
        } else {
          setRounds(FALLBACK);
        }
      })
      .catch(() => {
        setRounds(FALLBACK);
      });
  }, []);

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
        Each round, the server sends client behavioral stats as JSON to the LLM. Here is what the agent decided — and why.
      </p>

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
