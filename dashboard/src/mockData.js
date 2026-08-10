export const systemStats = {
  totalAlerts: 1432,
  activeNodes: 3,
  globalAccuracy: 99.79,
  centralizedAccuracy: 99.87,
  uptime: "14d 6h",
  lastUpdate: "Just now"
};

export const alertsData = [
  {
    id: "AL-1049",
    type: "DDoS",
    confidence: 99.1,
    timestamp: "2026-08-01 14:23:01",
    sourceIp: "192.168.1.50",
    status: "critical",
    node: "Hospital-Node-1"
  },
  {
    id: "AL-1048",
    type: "Infiltration",
    confidence: 94.3,
    timestamp: "2026-08-01 14:15:22",
    sourceIp: "10.0.0.12",
    status: "warning",
    node: "Bank-Node-2"
  },
  {
    id: "AL-1047",
    type: "Bot",
    confidence: 88.5,
    timestamp: "2026-08-01 13:58:10",
    sourceIp: "172.16.0.100",
    status: "warning",
    node: "Uni-Node-3"
  },
  {
    id: "AL-1046",
    type: "PortScan",
    confidence: 97.2,
    timestamp: "2026-08-01 13:45:05",
    sourceIp: "192.168.1.150",
    status: "critical",
    node: "Hospital-Node-1"
  }
];

export const shapData = {
  "AL-1049": [
    { feature: "Packet Length Variance", value: 0.12 },
    { feature: "Fwd Seg Size Min", value: 0.10 },
    { feature: "Packet Length Std", value: 0.08 },
    { feature: "Bwd Packet Length Std", value: 0.07 },
    { feature: "Bwd Segment Size Avg", value: 0.06 },
    { feature: "Bwd Packet Length Mean", value: 0.06 },
    { feature: "Fwd RST Flags", value: 0.05 }
  ],
  "AL-1048": [
    { feature: "Bwd Bulk Rate Avg", value: 0.04 },
    { feature: "SYN Flag Count", value: 0.02 },
    { feature: "Protocol", value: 0.01 },
    { feature: "Bwd IAT Total", value: 0.01 },
    { feature: "FIN Flag Count", value: 0.005 }
  ]
};

export const accuracyComparison = [
  { name: 'Centralized', accuracy: 99.87 },
  { name: 'Fed IID', accuracy: 99.79 },
  { name: 'Fed Non-IID (Avg)', accuracy: 99.79 },
  { name: 'Fed Non-IID (Prox)', accuracy: 99.44 },
  { name: 'Local Only', accuracy: 99.02 }
];
