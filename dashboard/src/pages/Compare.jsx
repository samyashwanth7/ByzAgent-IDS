import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import { ShieldAlert, Info, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function Compare() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('http://localhost:8000/results/comparison');
        if (res.ok) {
          setData(await res.json());
        }
      } catch (e) {
        console.error("Failed to fetch comparison data");
      }
    };
    fetchData();
  }, []);

  // Format data for the line chart (Accuracy across 10 rounds)
  const chartData = [];
  if (data && data.federated_iid_fedavg) {
    const rounds = data.federated_iid_fedavg.history.val_accuracy.length;
    for (let i = 0; i < rounds; i++) {
      chartData.push({
        round: i + 1,
        fedavg: (data.federated_iid_fedavg.history.val_accuracy[i] * 100).toFixed(2),
        krum: data.federated_iid_krum ? (data.federated_iid_krum.history.val_accuracy[i] * 100).toFixed(2) : null,
        byzagent: data.federated_iid_byzagent_gradual ? (data.federated_iid_byzagent_gradual.history.val_accuracy[i] * 100).toFixed(2) : null
      });
    }
  }

  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <ShieldAlert size={28} color="var(--accent-cyan)" />
          Defense Comparison (Sybil Attack)
        </h1>
        <p style={{ color: 'var(--text-secondary)', maxWidth: '900px', fontSize: '15px', lineHeight: '1.6' }}>
          We evaluated the system under a <strong>Sybil Label-Flipping Attack</strong>, where 2 out of 3 clients (66%) 
          are malicious and flip attack labels to "BENIGN". Standard FedAvg is completely compromised. The widely-used 
          mathematical defense, Krum, also fails because the attackers form a majority cluster. ByzAgent successfully 
          defends the system.
        </p>
      </div>

      {/* Why Krum Fails Explainer */}
      <div className="card" style={{ marginBottom: '32px', borderLeft: '4px solid var(--status-warning)', background: 'rgba(245, 158, 11, 0.03)' }}>
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--status-warning)', marginTop: 0 }}>
          <AlertTriangle size={20} />
          Why does Krum fail?
        </h3>
        <p style={{ fontSize: '14px', lineHeight: '1.6', margin: 0, color: 'var(--text-secondary)' }}>
          Krum assumes attackers are outliers in high-dimensional weight space. It selects the single client update with the 
          smallest Euclidean distance to its nearest neighbors. However, in a Sybil attack, the two malicious clients send 
          very similar poisoned updates. Krum calculates that they are close to each other, forming a tight cluster, and 
          mistakenly selects one of the attackers as the "trusted" update, discarding the lone clean client as the "outlier".
        </p>
      </div>

      <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
        
        {/* Line Chart */}
        <div className="card" style={{ flex: '2 1 600px', padding: '24px' }}>
          <h3 style={{ marginTop: 0, marginBottom: '20px' }}>Global Validation Accuracy Over 10 Rounds</h3>
          <div style={{ height: '350px' }}>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="round" stroke="var(--text-secondary)" label={{ value: 'Federated Round', position: 'bottom', offset: 0 }} />
                  <YAxis domain={[0, 100]} stroke="var(--text-secondary)" label={{ value: 'Accuracy (%)', angle: -90, position: 'insideLeft', offset: -10 }} />
                  <Tooltip contentStyle={{ background: '#1a1a2e', border: '1px solid var(--border-color)', borderRadius: '8px' }} />
                  <Legend verticalAlign="top" height={36} />
                  <Line type="monotone" dataKey="byzagent" name="ByzAgent (LLM)" stroke="#00c864" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                  <Line type="monotone" dataKey="krum" name="Krum (Math Baseline)" stroke="#f59e0b" strokeWidth={2} strokeDasharray="5 5" />
                  <Line type="monotone" dataKey="fedavg" name="FedAvg (No Defense)" stroke="#ef4444" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
                Loading experiment results...
              </div>
            )}
          </div>
        </div>

        {/* Results Table */}
        <div className="card" style={{ flex: '1 1 300px', padding: '24px' }}>
          <h3 style={{ marginTop: 0, marginBottom: '20px' }}>Final Results (Round 10)</h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            
            <div style={{ padding: '16px', background: 'rgba(0, 200, 100, 0.05)', borderRadius: '8px', border: '1px solid rgba(0, 200, 100, 0.2)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontWeight: 600, color: '#00c864', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <ShieldCheck size={16} /> ByzAgent
                </span>
                <span className="badge good">Winner</span>
              </div>
              <div style={{ fontSize: '28px', fontWeight: 700, color: 'var(--text-primary)' }}>
                {data?.federated_iid_byzagent_gradual ? (data.federated_iid_byzagent_gradual.accuracy * 100).toFixed(2) : '--'}%
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>LLM successfully quarantined attackers</div>
            </div>

            <div style={{ padding: '16px', background: 'rgba(245, 158, 11, 0.05)', borderRadius: '8px', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontWeight: 600, color: '#f59e0b' }}>Krum Baseline</span>
                <span className="badge warning">Failed</span>
              </div>
              <div style={{ fontSize: '28px', fontWeight: 700, color: 'var(--text-primary)' }}>
                {data?.federated_iid_krum ? (data.federated_iid_krum.accuracy * 100).toFixed(2) : '--'}%
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Fooled by Sybil cluster</div>
            </div>

            <div style={{ padding: '16px', background: 'rgba(239, 68, 68, 0.05)', borderRadius: '8px', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontWeight: 600, color: '#ef4444' }}>FedAvg</span>
                <span className="badge critical">Compromised</span>
              </div>
              <div style={{ fontSize: '28px', fontWeight: 700, color: 'var(--text-primary)' }}>
                {data?.federated_iid_fedavg ? (data.federated_iid_fedavg.accuracy * 100).toFixed(2) : '--'}%
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>No defense mechanism</div>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
}
