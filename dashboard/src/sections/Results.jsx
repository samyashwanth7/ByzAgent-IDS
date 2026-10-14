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

export default function Results() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    fetch('/data/comparison.json')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then((json) => {
        if (isMounted && json && Object.keys(json).length > 0) {
          setData(json);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.warn('Failed to fetch /data/comparison.json:', err);
        setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const byz = data?.byzagent_gradual;
  const rule = data?.rule_gradual;
  const krum = data?.krum_gradual;
  const trim = data?.trimmed_mean_gradual;
  const fedavg = data?.fedavg_gradual;
  const clean = data?.fedavg_clean;

  const formatPercent = (val) => {
    if (val === undefined || val === null) return '--';
    const num = val <= 1 ? val * 100 : val;
    return `${parseFloat(num.toFixed(2))}%`;
  };

  const chartData = Array.from({ length: 10 }, (_, i) => {
    const toPct = (hist) => {
      if (!hist || hist[i] === undefined || hist[i] === null) return null;
      const v = hist[i];
      return +(v <= 1 ? (v * 100).toFixed(2) : v.toFixed(2));
    };

    return {
      round: i + 1,
      ByzAgent: toPct(byz?.acc_history),
      'Rule Baseline': toPct(rule?.acc_history),
      Krum: toPct(krum?.acc_history),
      'Trimmed-Mean': toPct(trim?.acc_history),
      'FedAvg (Poisoned)': toPct(fedavg?.acc_history),
      'Clean Reference': toPct(clean?.acc_history),
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
        Evaluated under a coordinated Sybil Label-Flipping attack where 2 of 3 clients maliciously flip traffic labels across 10 federated rounds.
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
            <span className="badge badge-cyan">Real Evaluation Data</span>
          </div>

          <ResponsiveContainer width="100%" height={380}>
            <LineChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 20 }}>
              <CartesianGrid stroke="rgba(255, 255, 255, 0.05)" strokeDasharray="3 3" />
              <XAxis
                dataKey="round"
                stroke="var(--text-muted)"
                tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
                label={{ value: 'Round', position: 'insideBottom', offset: -12, fill: 'var(--text-secondary)', fontSize: 12 }}
              />
              <YAxis
                domain={[70, 100]}
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
                wrapperStyle={{ paddingBottom: '10px', fontSize: '12px' }}
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
                dataKey="Rule Baseline"
                stroke="#00F0FF"
                strokeWidth={2}
                dot={{ fill: '#00F0FF', r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="Krum"
                stroke="#f59e0b"
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={{ fill: '#f59e0b', r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="Trimmed-Mean"
                stroke="#a78bfa"
                strokeWidth={2}
                strokeDasharray="4 4"
                dot={{ fill: '#a78bfa', r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="FedAvg (Poisoned)"
                stroke="#ef4444"
                strokeWidth={2}
                dot={{ fill: '#ef4444', r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="Clean Reference"
                stroke="#9ca3af"
                strokeWidth={1.5}
                strokeDasharray="3 3"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Right: Stacked Result Cards (flex: 1) */}
        <div style={{ flex: '1 1 300px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* ByzAgent */}
          <div className="result-card winner">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontWeight: 600, fontSize: '15px' }}>ByzAgent</span>
              <span className="badge badge-green">
                <ShieldCheck size={14} /> Winner
              </span>
            </div>
            <div className="stat-huge text-green">{formatPercent(byz?.final_acc)}</div>
            <p className="subtitle" style={{ fontSize: '13px', marginTop: '6px' }}>
              LLM dynamically quarantined Sybil attackers
            </p>
          </div>

          {/* Rule Baseline */}
          <div className="result-card" style={{ borderColor: 'rgba(0, 240, 255, 0.3)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontWeight: 600, fontSize: '15px' }}>Rule Baseline</span>
              <span className="badge badge-cyan">Heuristic</span>
            </div>
            <div className="stat-huge text-accent">{formatPercent(rule?.final_acc)}</div>
            <p className="subtitle" style={{ fontSize: '13px', marginTop: '6px' }}>
              Static threshold defense
            </p>
          </div>

          {/* Krum */}
          <div className="result-card failed">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontWeight: 600, fontSize: '15px' }}>Krum</span>
              <span className="badge badge-orange">Failed</span>
            </div>
            <div className="stat-huge text-orange">{formatPercent(krum?.final_acc)}</div>
            <p className="subtitle" style={{ fontSize: '13px', marginTop: '6px' }}>
              Fooled by Sybil majority cluster
            </p>
          </div>

          {/* FedAvg */}
          <div className="result-card compromised" style={{ marginBottom: 0 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontWeight: 600, fontSize: '15px' }}>FedAvg</span>
              <span className="badge badge-red">Compromised</span>
            </div>
            <div className="stat-huge text-red">{formatPercent(fedavg?.final_acc)}</div>
            <p className="subtitle" style={{ fontSize: '13px', marginTop: '6px' }}>
              No Byzantine defense
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
          <h3 style={{ fontSize: '18px', fontWeight: 600 }}>Why Traditional Math Defenses Collapse</h3>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '15px', lineHeight: '1.7' }}>
          Classical Byzantine robust aggregators like Krum require an honest majority (<code style={{ color: 'var(--accent)' }}>n &gt; 2f + 2</code>). When malicious clients coordinate a <strong style={{ color: 'var(--text)' }}>Sybil attack</strong> (controlling 2 of 3 nodes), their poisoned updates form an artificial geometric cluster in weight space. Pure distance-based metrics mistake this dense Sybil cluster for consensus, selecting poisoned updates and discarding genuine honest contributions. In contrast, ByzAgent tracks temporal behavioral trajectories across rounds and reasons contextually to isolate stealthy poisoning.
        </p>
      </div>
    </section>
  );
}
