# ByzAgent: Agentic Byzantine Trust Diagnosis for Federated Intrusion Detection

**Shaashwat Agrawal and Team**
Department of Computer Science, VIT-AP University, 2026

---

## Abstract

Federated Learning (FL) enables multiple organizations to collaboratively train Network Intrusion Detection Systems (NIDS) without sharing sensitive network telemetry, preserving strict data privacy. However, decentralized training introduces a critical vulnerability: Byzantine poisoning attacks, where malicious clients submit sabotaged model updates to degrade global performance. Traditional robust aggregation algorithms, such as Krum and Trimmed-Mean, rely on geometric distance metrics. We demonstrate empirically that these mathematical defenses fail catastrophically under Sybil conditions (when attackers outnumber honest clients), as malicious updates form a tighter geometric majority. 

To solve this, we propose **ByzAgent**, an Agentic AI trust arbiter that replaces rigid distance formulas with a Large Language Model (LLM) reasoning engine. ByzAgent extracts client behavioral statistics—update norm, peer cosine similarity, local loss, and validation accuracy—and uses an LLM to logically deduce client intent, dynamically outputting "trust", "downweight", or "quarantine" decisions. Evaluated on the CICIDS-2017 dataset, ByzAgent successfully quarantines coordinated attackers where Krum fails, recovering global model accuracy from 84.90% to **98.97%**.

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
The foundational model is a Deep Neural Network (Multi-Layer Perceptron) trained on the CICIDS-2017 dataset to classify network flows into 8 categories (BENIGN, DDoS, PortScan, etc.). Training is distributed across $ simulated organizational clients.

### 2.2 ByzAgent: The LLM Trust Arbiter
At the end of each local training round, the central server extracts four behavioral statistics for every client:
1. **Update Norm:** The Euclidean magnitude of the client's weight update.
2. **Peer Cosine Similarity:** The angular divergence of the client's update compared to the network average.
3. **Local Loss:** The client's final training loss (malicious label-flipping inherently increases local loss).
4. **Validation Accuracy:** The client model's performance on a clean, held-out server dataset.

These metrics are structured into a JSON payload and passed to an LLM via the Groq API using LangChain. The LLM is prompted to evaluate the statistics and return a structured decision for each client:
*   TRUST: Integrate the update normally.
*   DOWNWEIGHT: Integrate the update with a reduced learning rate.
*   QUARANTINE: Reject the update entirely.

### 2.3 Post-hoc Explainability (SHAP)
To ensure the underlying MLP remains interpretable to human analysts, we apply SHapley Additive exPlanations (SHAP) to the final global model. This allows security teams to verify exactly which network flow features (e.g., Packet Length Variance, SYN Flag Count) triggered an intrusion alert.

---

## 3. Experimental Setup & Results

### 3.1 Experiment Design
We simulate a highly adversarial environment using the CICIDS-2017 dataset (2.8 million rows). The federation consists of 3 clients. To test the limits of Byzantine defenses, we introduce a **Sybil Attack**: 2 out of the 3 clients are adversarial, executing a sudden label-flipping attack (flipping 60% of their labels to arbitrary incorrect classes). 

### 3.2 Results

| Aggregation Strategy | Defense Mechanism | Final Accuracy | Final F1 Score |
| :--- | :--- | :--- | :--- |
| **FedAvg** | None | 96.16% | 0.9567 |
| **Krum** | Distance Clustering | 84.90% | 0.8402 |
| **ByzAgent (Ours)** | LLM Semantic Reasoning | **98.97%** | **0.9889** |

**Analysis of the Krum Failure:** Because the two attackers submitted identical poisoned updates, they were geometrically identical (Distance = 0). Krum identified them as the most "central" updates and selected them as the global model, completely rejecting the single honest client. The global accuracy plummeted to 84.90%.

**Analysis of the ByzAgent Success:** The LLM arbiter ignored the geometric clustering. It observed that the two attackers had massive local loss spikes ($>1.60$) and crashed validation accuracy (.9\%$). The LLM logically deduced that despite their similarity to each other, they were compromised. It quarantined both attackers and exclusively aggregated the honest client, preserving the model's integrity at 98.97%.

---

## 4. Conclusion
ByzAgent demonstrates that Large Language Models can successfully serve as real-time, logical arbiters in Federated Learning pipelines. By transitioning from strict geometric distance formulas to semantic behavioral reasoning, ByzAgent successfully neutralized a majority-attacker Sybil scenario that fundamentally breaks traditional Byzantine defenses.
