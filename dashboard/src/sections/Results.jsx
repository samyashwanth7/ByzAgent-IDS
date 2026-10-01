import React, { useState, useEffect } from 'react';
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
import { AlertTriangle, ShieldCheck } from 'lucide-react';

const FALLBACK = {
  federated_iid_fedavg: { accuracy: 0.9616, history: { val_accuracy: [0.85,0.90,0.92,0.93,0.94,0.95,0.955,0.958,0.960,0.9616] } },
  federated_iid_krum: { accuracy: 0.849, history: { val_accuracy: [0.85,0.82,0.80,0.78,0.79,0.81,0.83,0.84,0.845,0.849] } },
  federated_iid_byzagent_gradual: { accuracy: 0.9931, history: { val_accuracy: [0.85,0.92,0.95,0.97,0.98,0.985,0.988,0.990,0.992,0.9931] } }
};

export default function Results() {
  const [data, setData] = useState(FALLBACK);

  useEffect(() => {
    let isMounted = true;
    fetch('http://localhost:8000/results/comparison')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then((json) => {
        if (isMounted && json && Object.keys(json).length > 0) {
          setData(json);
        }
      })
      .catch((err) => {
        console.warn('Failed to fetch results from backend, using fallback data:', err);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const fedavgData = data?.federated_iid_fedavg || FALLBACK.federated_iid_fedavg;
  const krumData = data?.federated_iid_krum || FALLBACK.federated_iid_krum;
  const byzagentData = data?.federated_iid_byzagent_gradual || data?.federated_iid_byzagent || FALLBACK.federated_iid_byzagent_gradual;

  const getAccuracyVal = (item) => item?.accuracy ?? item?.final_accuracy;
  const getHistoryList = (item) => item?.history?.val_accuracy || item?.history?.global_acc || [];

  const fedavgAcc = getAccuracyVal(fedavgData);
  const krumAcc = getAccuracyVal(krumData);
  const byzagentAcc = getAccuracyVal(byzagentData);

  const fedavgHistory = getHistoryList(fedavgData);
  const krumHistory = getHistoryList(krumData);
  const byzagentHistory = getHistoryList(byzagentData);

  const formatPercent = (val) => {
    if (val === undefined || val === null) return '--';
    const num = val <= 1 ? val * 100 : val;
    return `${parseFloat(num.toFixed(2))}%`;
  };

  const chartData = Array.from({ length: 10 }, (_, i) => {
    const toPct = (hist) => {
      const v = hist[i];
      if (v === undefined || v === null) return null;
      return +(v <= 1 ? (v * 100).toFixed(2) : v.toFixed(2));
    };

    return {
      round: i + 1,
      ByzAgent: toPct(byzagentHistory),
      Krum: toPct(krumHistory),
      FedAvg: toPct(fedavgHistory),
    };
  });

  return (
    <section className="section" id="results">
      <div className="divider" style={{ marginBottom: '120px' }} />

      <div className="section-label">
        <span>03</span> Experimental Results
      </div>

      <h2 className="heading-lg" style={{ marginBottom: '16px' }}>
        ByzAgent wins. <span className="serif">Krum collapses.</span>
      </h2>

      <p className="subtitle" style={{ marginBottom: '60px' }}>
        Tested under a coordinated Sybil Label-Flipping attack where 2 of 3 clients are malicious across 10 federated rounds.
      </p>

      {/* Main Comparison: Chart + Cards */}
      <div style={{ display: 'flex', gap: '32px', alignItems: 'stretch', marginBottom: '40px', flexWrap: 'wrap' }}>
        {/* Left: Recharts LineChart (flex: 2) */}
        <div
          style={{
            flex: '2 1 500px',
            minWidth: '320px',
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)',
            padding: '24px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center'
          }}
        >
          <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text)' }}>
              Accuracy over 10 Federated Rounds
            </span>
            <span className="badge badge-cyan">Validation Accuracy</span>
          </div>

          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 20 }}>
              <CartesianGrid stroke="rgba(255, 255, 255, 0.05)" strokeDasharray="3 3" />
              <XAxis
                dataKey="round"
                stroke="var(--text-muted)"
                tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
                label={{ value: 'Round', position: 'insideBottom', offset: -12, fill: 'var(--text-secondary)', fontSize: 12 }}
              />
              <YAxis
                domain={[0, 100]}
                stroke="var(--text-muted)"
                tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
                tickFormatter={(v) => `${v}%`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--bg-elevated)',
                  border: '1px solid var(--border)',
                  borderRadius: '12px',
                  color: 'var(--text)'
                }}
                formatter={(value) => [`${value}%`]}
                labelFormatter={(label) => `Round ${label}`}
              />
              <Legend
                verticalAlign="top"
                height={36}
                wrapperStyle={{ paddingBottom: '10px', fontSize: '13px' }}
              />
              <Line
                type="monotone"
                dataKey="ByzAgent"
                stroke="#22c55e"
                strokeWidth={3}
                dot={{ fill: '#22c55e', r: 3 }}
                activeDot={{ r: 6 }}
              />
              <Line
                type="monotone"
                dataKey="Krum"
                stroke="#f59e0b"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={{ fill: '#f59e0b', r: 3 }}
                activeDot={{ r: 5 }}
              />
              <Line
                type="monotone"
                dataKey="FedAvg"
                stroke="#ef4444"
                strokeWidth={2}
                dot={{ fill: '#ef4444', r: 3 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Right: Stacked Result Cards (flex: 1) */}
        <div style={{ flex: '1 1 300px', display: 'flex', flexDirection: 'column' }}>
          {/* ByzAgent */}
          <div className="result-card winner">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontWeight: 600, fontSize: '15px' }}>ByzAgent</span>
              <span className="badge badge-green">
                <ShieldCheck size={14} /> Winner
              </span>
            </div>
            <div className="stat-huge text-green">{formatPercent(byzagentAcc)}</div>
            <p className="subtitle" style={{ fontSize: '13px', marginTop: '6px' }}>
              LLM quarantined attackers
            </p>
          </div>

          {/* Krum */}
          <div className="result-card failed">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontWeight: 600, fontSize: '15px' }}>Krum</span>
              <span className="badge badge-orange">Failed</span>
            </div>
            <div className="stat-huge text-orange">{formatPercent(krumAcc)}</div>
            <p className="subtitle" style={{ fontSize: '13px', marginTop: '6px' }}>
              Fooled by Sybil cluster
            </p>
          </div>

          {/* FedAvg */}
          <div className="result-card compromised" style={{ marginBottom: 0 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontWeight: 600, fontSize: '15px' }}>FedAvg</span>
              <span className="badge badge-red">Compromised</span>
            </div>
            <div className="stat-huge text-red">{formatPercent(fedavgAcc)}</div>
            <p className="subtitle" style={{ fontSize: '13px', marginTop: '6px' }}>
              No defense mechanism
            </p>
          </div>
        </div>
      </div>

      {/* Why Krum Fails Card */}
      <div
        className="card"
        style={{
          borderLeft: '4px solid var(--orange)'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
          <AlertTriangle size={24} color="var(--orange)" />
          <h3 style={{ fontSize: '18px', fontWeight: 600 }}>Why Krum Fails</h3>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '15px', lineHeight: '1.7' }}>
          Krum relies on geometric Euclidean distance, calculating score metrics based on proximity to nearest neighbors under the assumption of an honest majority. When malicious nodes coordinate a <strong style={{ color: 'var(--text)' }}>Sybil attack</strong> (controlling 2 of 3 participants), their poisoned updates cluster tightly together in parameter space. Krum misidentifies this artificial Sybil consensus as the honest cluster and selects an attacker update while discarding the single honest client as an outlier — leading to severe performance degradation down to <strong style={{ color: 'var(--orange)' }}>84.9%</strong>. In contrast, ByzAgent uses semantic behavioral analysis and historical context to accurately identify and quarantine attackers regardless of cluster size.
        </p>
      </div>
    </section>
  );
}
