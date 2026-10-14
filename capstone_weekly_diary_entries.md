# B.Tech Capstone Project Diary - Weekly Progress Entries (12 Weeks)
**Project Title:** ByzAgent-IDS: Agentic Byzantine Trust Diagnosis for Federated Intrusion Detection  

---

### **Week 1**
* **Tasks Completed:**  
  Surveyed literature on Federated Learning for Network Intrusion Detection (NIDS) and analyzed the CICIDS-2017 dataset schema.
* **Tasks Planned Next Week:**  
  Clean network flow features, remove NaN/Inf values, and build a centralized baseline classifier.

---

### **Week 2**
* **Tasks Completed:**  
  Completed data preprocessing, feature normalization, and trained a centralized PyTorch MLP baseline achieving 99.8% accuracy.
* **Tasks Planned Next Week:**  
  Partition dataset across simulated hospital/bank nodes for both IID and Non-IID distributions.

---

### **Week 3**
* **Tasks Completed:**  
  Implemented Federated Learning training loop with FedAvg and FedProx across 3 distributed client nodes.
* **Tasks Planned Next Week:**  
  Incorporate Differential Privacy (DP) noise clipping and assess model convergence under privacy constraints.

---

### **Week 4**
* **Tasks Completed:**  
  Integrated DP-SGD noise addition on weight updates and benchmarked privacy-utility trade-offs across 10 rounds.
* **Tasks Planned Next Week:**  
  Simulate adversarial client behavior and study model vulnerability to data poisoning attacks.

---

### **Week 5**
* **Tasks Completed:**  
  Implemented sudden and gradual Label-Flipping attacks, demonstrating that unmitigated FedAvg model accuracy degrades significantly.
* **Tasks Planned Next Week:**  
  Implement classical Byzantine-robust aggregation algorithms (Krum, Trimmed-Mean) to defend against poisoning.

---

### **Week 6**
* **Tasks Completed:**  
  Benchmarked Krum and Trimmed-Mean; mathematically proved and observed that Krum collapses (drops to 84.9%) under Sybil majority attacks (2 of 3 malicious clients).
* **Tasks Planned Next Week:**  
  Pivot project scope from static FL to ByzAgent: research LLM-in-the-loop agentic trust diagnosis on the central server.

---

### **Week 7**
* **Tasks Completed:**  
  Finalized pivot to ByzAgent-IDS; designed system architecture where an LLM agent acts as an autonomous trust arbiter during aggregation.
* **Tasks Planned Next Week:**  
  Instrument client behavioral telemetry extraction (update norm, peer cosine similarity, loss, validation accuracy).

---

### **Week 8**
* **Tasks Completed:**  
  Created `ByzAgentMonitor` to compute per-client weight norms and cosine similarities against consensus; drafted LangChain + Groq system prompt.
* **Tasks Planned Next Week:**  
  Integrate Groq LPU API and LangChain structured JSON parsing for dynamic client classification.

---

### **Week 9**
* **Tasks Completed:**  
  Implemented `ByzAgentTrustArbiter` to classify nodes as `TRUST`, `DOWNWEIGHT`, or `QUARANTINE`, and wired dynamic weighted aggregation.
* **Tasks Planned Next Week:**  
  Run end-to-end multi-round experiments comparing ByzAgent against FedAvg, Krum, and Trimmed-Mean.

---

### **Week 10**
* **Tasks Completed:**  
  Completed comparative experiments; ByzAgent maintained 99.31% accuracy and successfully quarantined Sybil attackers where Krum failed.
* **Tasks Planned Next Week:**  
  Build full-stack web showcase and dashboard to present system architecture, live packet classification, and agent reasoning.

---

### **Week 11**
* **Tasks Completed:**  
  Developed single-page showcase and multi-tab Dashboard (React, Vite, Recharts, FastAPI) featuring real-time packet feed and agent thought logs.
* **Tasks Planned Next Week:**  
  Harden system against evaluation leakage, add temporal history to agent prompt, and implement rule-based heuristic baseline.

---

### **Week 12**
* **Tasks Completed:**  
  Separated server validation split to prevent test leakage, added rolling history to ByzAgent prompt, implemented rule baseline, and verified Vercel deployment.
* **Tasks Planned Next Week:**  
  Complete final capstone report, review presentation slides, and prepare documentation for project viva.
