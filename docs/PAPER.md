# ByzAgent: Agentic Byzantine Trust Diagnosis for Federated Intrusion Detection

**Sampath Kumar and Team**
Department of Computer Science, VIT-AP University, 2026

---

## Abstract

Federated Learning (FL) enables multiple organizations to collaboratively train Network Intrusion Detection Systems (NIDS) without sharing sensitive network telemetry, preserving strict data privacy. However, decentralized training introduces a critical vulnerability: Byzantine poisoning attacks, where malicious clients submit sabotaged model updates to degrade global performance. Traditional robust aggregation algorithms, such as Krum and Trimmed-Mean, rely on geometric distance metrics. We demonstrate empirically that these mathematical defenses fail catastrophically under Sybil conditions (when attackers outnumber honest clients), as malicious updates form a tighter geometric majority. 

To solve this, we propose **ByzAgent**, an Agentic AI trust arbiter that replaces rigid distance formulas with a Large Language Model (LLM) reasoning engine. ByzAgent extracts client behavioral telemetry—update norm, peer consensus cosine similarity, local loss, held-out server validation accuracy, and multi-round temporal trajectory—and uses an LLM to logically deduce client intent, dynamically outputting "trust", "downweight", or "quarantine" decisions. Evaluated on the CICIDS-2017 benchmark (8 traffic classes), ByzAgent successfully quarantines coordinated Sybil attackers where Krum fails, preserving global model accuracy at **99.04%** (Macro-F1: 0.9897) while classical defenses completely collapse (Krum down to 1.77%, FedAvg to 1.18%).

**Keywords:** Federated Learning, Intrusion Detection, Byzantine Fault Tolerance, Large Language Models, Agentic AI, Cybersecurity

---

## 1. Introduction

### 1.1 The Privacy and Poisoning Dilemma
As cyber threats grow in complexity, Machine Learning (ML) models require massive, diverse datasets to detect zero-day attacks. While Federated Learning (FL) allows organizations to collaboratively train an ML-based IDS by exchanging only model weights rather than private network data, it assumes all participating clients are honest. If a compromised organization or adversarial node joins the federation, they can execute a "label-flipping" poisoning attack, intentionally corrupting the global model.

### 1.2 The Failure of Mathematical Baselines
Current defenses against poisoning rely on robust aggregation algorithms like Krum. Krum selects the client update that is geometrically closest to its neighbors. While effective against isolated attackers, Krum relies on a fundamental assumption: that honest clients form the majority. If attackers coordinate and outnumber the honest clients, they form a mathematical majority cluster. In this scenario, distance-based metrics blindly trust the attackers and reject the honest clients.

### 1.3 Proposed Solution: ByzAgent
We introduce **ByzAgent**, a fundamentally new approach to federated aggregation. Instead of relying solely on the geometric distance between weight vectors, ByzAgent introduces an Agentic LLM (acting as a Security Operations Center analyst) into the aggregation loop. By monitoring the semantic behavior of the model updates (e.g., "Is this client struggling to fit the data?", "Did their validation accuracy suddenly crash?"), the LLM can logically reason about which clients are compromised, regardless of how many attackers are present.

---

## 2. Methodology

### 2.1 The Federated IDS Architecture
The foundational model is a Deep Neural Network (Multi-Layer Perceptron) trained on the CICIDS-2017 dataset to classify network flows into 8 categories (BENIGN, DDoS, PortScan, etc.). Training is distributed across 3 simulated organizational clients.

### 2.2 ByzAgent: The LLM Trust Arbiter
At the end of each local training round, the central server extracts 5 behavioral telemetry dimensions for every client:
1. **Weight Update Norm ($L_2$):** The Euclidean magnitude of the client's weight update vector.
2. **Peer Consensus Cosine Similarity:** The angular alignment of the client's update compared to the fleet consensus / unweighted global direction.
3. **Local Loss:** The client's final training loss (malicious label-flipping increases local loss as the client fits conflicting corrupted labels).
4. **Server Validation Accuracy:** Performance on a clean, isolated 10% server validation slice (preventing test data leakage).
5. **Rolling History Trajectory:** A 3-round sliding window tracking rate of change and temporal slopes across rounds.

These metrics are structured into a JSON payload and passed to an LLM via the Groq API using LangChain. The LLM is prompted to evaluate the statistics and return a structured decision for each client:
*   TRUST: Integrate the update normally.
*   DOWNWEIGHT: Integrate the update with a reduced learning rate.
*   QUARANTINE: Reject the update entirely.

### 2.3 Post-hoc Explainability (SHAP)
To ensure the underlying MLP remains interpretable to human analysts, we apply SHapley Additive exPlanations (SHAP) to the final global model. This allows security teams to verify exactly which network flow features (e.g., Packet Length Variance, SYN Flag Count) triggered an intrusion alert.

---

## 3. Experimental Setup & Results

### 3.1 Experiment Design
We simulate an adversarial environment using the CICIDS-2017 benchmark (1,786,531 training flows, 446,633 held-out flows [401,970 test + 44,663 server validation], 8 balanced traffic classes). The federation consists of 3 clients with a **Sybil Attack**: 2 out of the 3 clients are adversarial, executing a gradual label-flipping attack over 10 federated rounds (+10% poisoned labels per round).

### 3.2 Results

| Defense Strategy | Attack Status | Defense Mechanism | Final Accuracy | Macro-F1 | Attacker Detections (TP) | False Alarms (FP) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **FedAvg (Clean Ref)** | No Attack | None (Baseline) | 98.92% | 0.9882 | — | — |
| **FedAvg (Poisoned)** | Gradual Flip | None | 1.18% | 0.0156 | 0 / 20 | 0 |
| **Krum** | Gradual Flip | Distance Clustering | 1.77% | 0.0296 | 0 / 20 | 0 |
| **Trimmed-Mean** | Gradual Flip | Coordinate Median | 0.64% | 0.0051 | 0 / 20 | 0 |
| **Rule Baseline** | Gradual Flip | Static Thresholds | 99.33% | 0.9926 | 4 / 20 | 1 |
| **ByzAgent (Ours)** | Gradual Flip | Temporal LLM Reasoning | **99.04%** | **0.9897** | **20 / 20** | **2** |

**Analysis of the Krum Failure:** Because the two attackers submitted identical poisoned updates, they were geometrically close to each other ($d_{12} \approx 0$). Krum identified them as the most "central" updates and selected them as the global model, completely rejecting the single honest client. Global accuracy collapsed to 1.77%.

**Analysis of the ByzAgent Success:** ByzAgent discarded geometric distance assumptions. By tracking behavioral telemetry across a 3-round rolling window, it observed that the two attackers exhibited increasing loss, falling validation accuracy, and diverging consensus similarity. ByzAgent quarantined both malicious nodes early (20/20 true positives), isolating the poison and preserving the global model at 99.04% accuracy (Macro-F1: 0.9897).

---

## 4. Conclusion
ByzAgent demonstrates that Large Language Models can successfully serve as real-time, logical arbiters in Federated Learning pipelines. By transitioning from strict geometric distance formulas to semantic behavioral reasoning, ByzAgent successfully neutralized a majority-attacker Sybil scenario that fundamentally breaks traditional Byzantine defenses.
