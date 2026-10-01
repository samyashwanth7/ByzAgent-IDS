import React from 'react';
import { Shield } from 'lucide-react';

export default function Hero() {
  return (
    <section className="section" style={{ paddingTop: '180px', paddingBottom: '140px', position: 'relative' }}>
      <div className="glow-cyan" style={{ top: '-200px', right: '-200px' }} />

      <div className="reveal visible">
        <div className="section-label">
          <span>◆</span> Capstone Research Project
        </div>
      </div>

      <h1 className="heading-xl reveal visible" style={{ marginBottom: '24px' }}>
        <span className="text-accent">ByzAgent</span>-IDS
      </h1>

      <h2 className="heading-lg reveal visible" style={{ color: 'var(--text-secondary)', marginBottom: '32px', maxWidth: '800px' }}>
        Agentic Byzantine Trust Diagnosis for{' '}
        <span className="serif">Federated Intrusion Detection</span>
      </h2>

      <p className="subtitle reveal visible" style={{ marginBottom: '48px' }}>
        Multiple organizations collaboratively train a shared intrusion detection model
        without exposing private network data. When attackers poison the system, an
        LLM-powered trust arbiter reasons about client behavior and quarantines malicious nodes — achieving <strong style={{ color: 'var(--accent)' }}>99.31% accuracy</strong> where
        traditional math defenses collapse to 84%.
      </p>

      <div className="reveal visible" style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
        <a href="#architecture" className="btn btn-primary">
          <Shield size={16} />
          View Architecture
        </a>
        <a href="#results" className="btn btn-ghost">
          See Results ↓
        </a>
      </div>

      <div style={{ marginTop: '80px', display: 'flex', gap: '60px', flexWrap: 'wrap' }}>
        <div className="reveal visible">
          <div className="stat-huge text-accent">99.31%</div>
          <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>Accuracy under Sybil Attack</div>
        </div>
        <div className="reveal visible reveal-delay-1">
          <div className="stat-huge text-red">84.9%</div>
          <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>Krum Baseline (Failed)</div>
        </div>
        <div className="reveal visible reveal-delay-2">
          <div className="stat-huge" style={{ color: 'var(--text)' }}>8</div>
          <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>Attack Classes Detected</div>
        </div>
        <div className="reveal visible reveal-delay-3">
          <div className="stat-huge text-purple">LLM</div>
          <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>Autonomous Trust Arbiter</div>
        </div>
      </div>
    </section>
  );
}
