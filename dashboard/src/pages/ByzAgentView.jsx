import React, { useState, useEffect } from 'react';
import { Shield, ShieldAlert, ShieldCheck } from 'lucide-react';

export default function ByzAgentView() {
  const [rounds, setRounds] = useState([]);

  useEffect(() => {
    const fetchDecisions = async () => {
      try {
        const res = await fetch('http://localhost:8000/byzagent/decisions');
        if (res.ok) {
          const data = await res.json();
          // Data is an array of objects: { round: X, decisions: [ {client_id, decision, explanation} ] }
          setRounds(data.data.reverse());
        }
      } catch (e) {
        console.error("ByzAgent API not running");
      }
    };
    
    fetchDecisions();
    const interval = setInterval(fetchDecisions, 2000);
    return () => clearInterval(interval);
  }, []);

  const getDecisionBadge = (decision) => {
    switch (decision?.toLowerCase()) {
      case 'quarantine':
        return <span className=\"badge critical\" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><ShieldAlert size={12}/> Quarantine</span>;
      case 'trust':
        return <span className=\"badge\" style={{ background: 'rgba(0, 200, 100, 0.15)', color: '#00c864', display: 'flex', alignItems: 'center', gap: '4px' }}><ShieldCheck size={12}/> Trust</span>;
      case 'downweight':
        return <span className=\"badge warning\" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Shield size={12}/> Downweight</span>;
      default:
        return <span className=\"badge\">{decision}</span>;
    }
  };

  return (
    <div className=\"animate-fade-in\">
      <div style={{ marginBottom: '24px' }}>
        <h1>ByzAgent LLM Trust Arbiter</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Live reasoning from the LangChain Groq LLM analyzing client behavioral stats.</p>
      </div>

      {rounds.length === 0 ? (
        <div className=\"card\" style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
          Waiting for federated training rounds to complete...
        </div>
      ) : rounds.map((r, i) => (
        <div key={i} className=\"card\" style={{ marginBottom: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px', marginBottom: '12px' }}>
            <h3 style={{ margin: 0, color: 'var(--accent-cyan)' }}>Round {r.round}</h3>
          </div>
          <div style={{ display: 'grid', gap: '12px' }}>
            {r.decisions && r.decisions.map((d, j) => (
              <div key={j} style={{ background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '6px', borderLeft: d.decision.toLowerCase() === 'quarantine' ? '3px solid var(--status-critical)' : '3px solid #00c864' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <strong style={{ fontFamily: 'monospace', fontSize: '14px' }}>{d.client_id}</strong>
                  {getDecisionBadge(d.decision)}
                </div>
                <div style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: '1.4' }}>
                  {d.explanation}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
