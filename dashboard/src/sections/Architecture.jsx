import React from 'react';
import { Database, ShieldAlert, Server, Cpu, Network } from 'lucide-react';

export default function Architecture() {
  return (
    <section className="section-full dot-grid" id="architecture" style={{ position: 'relative' }}>
      <div className="glow-purple" style={{ top: '100px', left: '-150px' }} />
      <div className="glow-cyan" style={{ bottom: '-100px', right: '-100px' }} />

      <div style={{ maxWidth: '1200px', margin: '0 auto', position: 'relative', zIndex: 1 }}>
        <div className="section-label">
          <span>02</span> System Architecture
        </div>

        <h2 className="heading-lg" style={{ marginBottom: '16px' }}>
          An LLM replaces <span className="serif">rigid math</span><br />
          with <span className="text-purple">adaptive reasoning.</span>
        </h2>

        <p className="subtitle" style={{ marginBottom: '60px' }}>
          Instead of relying on Euclidean distance (which attackers can game),
          ByzAgent feeds behavioral statistics to an LLM that reasons about trust
          across temporal context.
        </p>

        {/* Architecture Flowchart */}
        <div className="arch-flow">
          {/* Row 1: Clients */}
          <div className="arch-row">
            <div className="arch-node clean">
              <Database size={24} color="var(--green)" style={{ marginBottom: '10px' }} />
              <h4 style={{ color: 'var(--green)' }}>Clean Client</h4>
              <p>Hospital Node — trains on real network traffic with correct labels</p>
            </div>
            <div className="arch-node attacker">
              <ShieldAlert size={24} color="var(--red)" style={{ marginBottom: '10px' }} />
              <h4 style={{ color: 'var(--red)' }}>Attacker A</h4>
              <p>Sybil Node — flips "Attack" labels to "BENIGN" to hide intrusions</p>
            </div>
            <div className="arch-node attacker">
              <ShieldAlert size={24} color="var(--red)" style={{ marginBottom: '10px' }} />
              <h4 style={{ color: 'var(--red)' }}>Attacker B</h4>
              <p>Sybil Node — coordinates with Node A to form a majority cluster</p>
            </div>
          </div>

          <div className="arch-arrow" />

          {/* Row 2: Central Server */}
          <div className="arch-row">
            <div className="arch-node server">
              <Server size={28} color="var(--accent)" style={{ marginBottom: '12px' }} />
              <h4 style={{ color: 'var(--accent)' }}>Central Aggregation Server</h4>
              <p style={{ marginBottom: '16px' }}>Receives model updates and extracts behavioral statistics per client</p>
              <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', flexWrap: 'wrap' }}>
                <span className="badge badge-cyan">Update Norm</span>
                <span className="badge badge-cyan">Cosine Similarity</span>
                <span className="badge badge-cyan">Local Loss</span>
                <span className="badge badge-cyan">Val Accuracy</span>
              </div>
            </div>
          </div>

          <div className="arch-arrow" style={{ background: 'linear-gradient(to bottom, rgba(0,240,255,0.3), rgba(167,139,250,0.4))' }} />

          {/* Row 3: ByzAgent LLM */}
          <div className="arch-row">
            <div className="arch-node agent">
              <Cpu size={36} color="var(--purple)" style={{ marginBottom: '14px' }} />
              <h4 style={{ color: 'var(--purple)', fontSize: '20px' }}>ByzAgent Trust Arbiter</h4>
              <p style={{ marginBottom: '16px' }}>LangChain + Groq LLM receives JSON stats and outputs structured trust decisions with natural language reasoning</p>
              <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', flexWrap: 'wrap' }}>
                <span className="badge badge-green">TRUST</span>
                <span className="badge badge-orange">DOWNWEIGHT</span>
                <span className="badge badge-red">QUARANTINE</span>
              </div>
            </div>
          </div>

          <div className="arch-arrow" style={{ background: 'linear-gradient(to bottom, rgba(167,139,250,0.4), rgba(34,197,94,0.4))' }} />

          {/* Row 4: Output */}
          <div className="arch-row">
            <div className="arch-node output">
              <Network size={28} color="var(--green)" style={{ marginBottom: '10px' }} />
              <h4 style={{ color: 'var(--green)' }}>Robust Global Model</h4>
              <p>Only trusted updates aggregated — achieves 99.31% accuracy under attack</p>
            </div>
          </div>
        </div>

        {/* Tech Stack */}
        <div style={{ textAlign: 'center', marginTop: '80px' }}>
          <div className="section-label" style={{ justifyContent: 'center' }}>
            <span>◆</span> Technology Stack
          </div>
          <div className="tech-grid" style={{ marginTop: '20px' }}>
            <span className="tech-pill">PyTorch</span>
            <span className="tech-pill">LangChain</span>
            <span className="tech-pill">Groq API</span>
            <span className="tech-pill">SHAP</span>
            <span className="tech-pill">Scikit-Learn</span>
            <span className="tech-pill">React</span>
            <span className="tech-pill">Vite</span>
            <span className="tech-pill">Recharts</span>
            <span className="tech-pill">FastAPI</span>
            <span className="tech-pill">CICIDS-2017</span>
          </div>
        </div>
      </div>
    </section>
  );
}
