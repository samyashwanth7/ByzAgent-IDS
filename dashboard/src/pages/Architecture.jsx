import React from 'react';
import { Layers, Database, ShieldAlert, Cpu, Network, Server, ShieldCheck, Activity } from 'lucide-react';

export default function Architecture() {
  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Layers size={28} color="var(--accent-cyan)" />
          ByzAgent Architecture
        </h1>
        <p style={{ color: 'var(--text-secondary)', maxWidth: '800px', fontSize: '15px' }}>
          ByzAgent introduces an LLM-based Arbiter into the Federated Learning aggregation process. 
          Unlike traditional statistical defenses (like Krum), the LLM can reason about client behavioral 
          trajectories over time, allowing it to detect and quarantine adaptive poisoning attacks.
        </p>
      </div>

      <div className="card" style={{ padding: '40px 20px', marginBottom: '32px', overflowX: 'auto' }}>
        <div className="arch-container">
          
          {/* Row 1: Local Data & Training */}
          <div className="arch-row">
            <div className="arch-box defender">
              <Database size={24} color="#00c864" style={{ marginBottom: '8px' }} />
              <h4>Clean Client</h4>
              <p>Hospital Node<br/>Trains on normal traffic and genuine attacks.</p>
            </div>
            
            <div className="arch-box attacker">
              <ShieldAlert size={24} color="var(--status-critical)" style={{ marginBottom: '8px' }} />
              <h4>Compromised Client</h4>
              <p>Attacker Node A<br/>Poisoning labels (e.g., Attack → Benign).</p>
            </div>

            <div className="arch-box attacker">
              <ShieldAlert size={24} color="var(--status-critical)" style={{ marginBottom: '8px' }} />
              <h4>Compromised Client</h4>
              <p>Attacker Node B<br/>Sybil attacker reinforcing Node A.</p>
            </div>
          </div>

          <div className="arch-arrow-vertical"></div>

          {/* Row 2: Central Server Aggregation */}
          <div className="arch-row">
            <div className="arch-box" style={{ width: '600px', border: '2px solid var(--accent-cyan)', background: 'rgba(0, 240, 255, 0.02)' }}>
              <Server size={24} color="var(--accent-cyan)" style={{ marginBottom: '8px' }} />
              <h4 style={{ color: 'var(--accent-cyan)' }}>Central Aggregation Server</h4>
              <p style={{ marginBottom: '16px' }}>Receives model weight updates. Calculates behavioral statistics.</p>
              
              <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                <span className="badge" style={{ background: 'rgba(255,255,255,0.05)' }}>Update Norms</span>
                <span className="badge" style={{ background: 'rgba(255,255,255,0.05)' }}>Peer Cosine Sim</span>
                <span className="badge" style={{ background: 'rgba(255,255,255,0.05)' }}>Local Loss</span>
              </div>
            </div>
          </div>

          <div className="arch-arrow-vertical"></div>

          {/* Row 3: The LLM Agent */}
          <div className="arch-row">
            <div className="arch-box" style={{ width: '400px', background: 'linear-gradient(180deg, rgba(30,35,45,1) 0%, rgba(20,25,35,1) 100%)', boxShadow: '0 10px 30px rgba(0,0,0,0.5)' }}>
              <Cpu size={32} color="#b48eed" style={{ marginBottom: '12px' }} />
              <h4 style={{ fontSize: '18px', color: '#b48eed' }}>ByzAgent Trust Arbiter (LLM)</h4>
              <p>Analyzes JSON trajectory data. Outputs reasoning and action (Trust, Downweight, Quarantine) via LangChain JSON parser.</p>
            </div>
          </div>

          <div className="arch-arrow-vertical"></div>

          {/* Row 4: Final Global Model */}
          <div className="arch-row">
            <div className="arch-box defender" style={{ width: '300px' }}>
              <Network size={28} color="#00c864" style={{ marginBottom: '8px' }} />
              <h4>Robust Global Model</h4>
              <p>Only aggregates trusted updates. Successfully maintains 99.3%+ accuracy.</p>
            </div>
          </div>

        </div>
      </div>

      <h2 style={{ marginBottom: '16px' }}>Technology Stack</h2>
      <div className="stats-grid">
        <div className="card">
          <h4 style={{ color: 'var(--text-primary)', marginBottom: '4px' }}>AI / ML Core</h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px', margin: 0 }}>PyTorch, Scikit-Learn</p>
        </div>
        <div className="card">
          <h4 style={{ color: 'var(--text-primary)', marginBottom: '4px' }}>Agent Framework</h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px', margin: 0 }}>LangChain, Groq API (gpt-oss-120b)</p>
        </div>
        <div className="card">
          <h4 style={{ color: 'var(--text-primary)', marginBottom: '4px' }}>Explainability</h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px', margin: 0 }}>SHAP (KernelExplainer)</p>
        </div>
        <div className="card">
          <h4 style={{ color: 'var(--text-primary)', marginBottom: '4px' }}>Dashboard Web Stack</h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px', margin: 0 }}>React, Vite, Recharts, FastAPI</p>
        </div>
      </div>
    </div>
  );
}
