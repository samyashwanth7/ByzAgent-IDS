import React from 'react';
import { Shield } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Shield size={20} color="var(--accent)" />
          <span style={{ fontWeight: 700, color: 'var(--accent)', fontSize: '16px' }}>ByzAgent-IDS</span>
        </div>

        <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
          Agentic Byzantine Trust Diagnosis for Federated Intrusion Detection
        </p>

        <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
          <a 
            href="https://github.com/samyashwanth7/ByzAgent-IDS" 
            target="_blank" 
            rel="noreferrer"
            style={{ color: 'var(--text-secondary)', fontSize: '13px', textDecoration: 'none', transition: 'color 0.2s' }}
            onMouseEnter={e => e.target.style.color = 'var(--text)'}
            onMouseLeave={e => e.target.style.color = 'var(--text-secondary)'}
          >
            GitHub ↗
          </a>
          <span style={{ color: 'var(--text-muted)', fontSize: '12px', fontFamily: 'monospace' }}>
            © {new Date().getFullYear()} Capstone Project
          </span>
        </div>
      </div>
    </footer>
  );
}
