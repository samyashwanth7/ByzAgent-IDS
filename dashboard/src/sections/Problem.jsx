import React from 'react';
import { Users, AlertTriangle, XCircle } from 'lucide-react';

export default function Problem() {
  return (
    <section className="section" id="problem">
      <div className="divider" style={{ marginBottom: '120px' }} />

      <div className="section-label">
        <span>01</span> The Problem
      </div>

      <h2 className="heading-lg" style={{ marginBottom: '16px' }}>
        Federated Learning is <span className="serif">private,</span><br />
        but dangerously <span className="text-red">vulnerable.</span>
      </h2>

      <p className="subtitle" style={{ marginBottom: '60px' }}>
        When organizations collaboratively train a model without sharing data,
        any participant can silently corrupt the shared model from the inside.
      </p>

      <div className="card-grid">
        <div className="card">
          <Users size={28} color="var(--accent)" style={{ marginBottom: '16px' }} />
          <h3 className="heading-md" style={{ marginBottom: '12px' }}>Federated Learning</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '15px', lineHeight: '1.7' }}>
            Three organizations — a hospital, bank, and university — each train a local IDS model
            on their own private network traffic. They share only model weight updates with a central
            server. <strong style={{ color: 'var(--text)' }}>No raw data ever leaves any organization.</strong>
          </p>
        </div>

        <div className="card" style={{ borderColor: 'rgba(239, 68, 68, 0.15)' }}>
          <AlertTriangle size={28} color="var(--red)" style={{ marginBottom: '16px' }} />
          <h3 className="heading-md" style={{ marginBottom: '12px' }}>The Byzantine Threat</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '15px', lineHeight: '1.7' }}>
            An adversary compromises 2 of 3 clients and performs a <strong style={{ color: 'var(--text)' }}>Label-Flipping Attack</strong> —
            relabeling "DDoS Attack" traffic as "BENIGN". The poisoned updates gradually corrupt
            the global model, causing it to stop detecting real attacks.
          </p>
        </div>

        <div className="card" style={{ borderColor: 'rgba(245, 158, 11, 0.15)' }}>
          <XCircle size={28} color="var(--orange)" style={{ marginBottom: '16px' }} />
          <h3 className="heading-md" style={{ marginBottom: '12px' }}>Why Math Defenses Fail</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '15px', lineHeight: '1.7' }}>
            The standard defense, <strong style={{ color: 'var(--text)' }}>Krum</strong>, selects the update closest to its neighbors in
            Euclidean space. But when 2 attackers coordinate (Sybil attack), they form a tight cluster.
            Krum picks the attacker as "honest" and discards the real clean client.
          </p>
        </div>
      </div>
    </section>
  );
}
