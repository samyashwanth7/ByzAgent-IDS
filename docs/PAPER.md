# XFed-IDS: Explainable Federated Learning for Privacy-Preserving Network Intrusion Detection

**Shaashwat Agrawal and Team**
Department of Computer Science, VIT-AP University, 2026

---

## Abstract

Traditional Intrusion Detection Systems (IDS) rely on centralized data collection, creating significant privacy risks when applied across multiple organizations. We propose **XFed-IDS**, an Explainable Federated Learning framework for network intrusion detection that enables collaborative model training without exchanging raw network traffic data. XFed-IDS combines Federated Averaging (FedAvg) and FedProx aggregation strategies with SHAP-based post-hoc explainability. We evaluate our approach on the CICIDS-2017 dataset under both IID and non-IID data distributions, simulating realistic multi-organization deployments. Our experiments demonstrate that XFed-IDS achieves **99.79% accuracy** — only 0.08% below the centralized upper bound — while preserving complete data privacy. Critically, we show that data-poor organizations (with as few as 97 attack samples) gain a **+2.5% accuracy boost** by joining the federation compared to training in isolation. Furthermore, SHAP analysis reveals that Packet Length Variance, Fwd Seg Size Min, and SYN Flag Count are the top predictive features for attack detection, providing actionable transparency for Security Operations Center (SOC) analysts.

**Keywords:** Federated Learning, Intrusion Detection System, Explainable AI, SHAP, Privacy-Preserving Machine Learning, CICIDS-2017

---

## 1. Introduction

### 1.1 Background and Motivation

The global cost of cybercrime is projected to reach $10.5 trillion annually by 2025 (Cybersecurity Ventures, 2023). Organizations across sectors — healthcare, finance, education — face an escalating volume of sophisticated network attacks including Distributed Denial-of-Service (DDoS), port scanning, brute-force intrusions, and infiltration campaigns. Network Intrusion Detection Systems (NIDS) serve as a critical line of defense, analyzing network traffic in real-time to identify and flag malicious activity.

Machine Learning (ML) and Deep Learning (DL) have significantly advanced IDS capabilities, enabling models to detect complex, previously unseen attack patterns from raw network features. However, training highly accurate ML models requires large, diverse datasets that capture a wide range of attack behaviors. For a single organization, the volume and variety of attacks it encounters may be limited, leading to models that overfit to local traffic patterns and generalize poorly.

The intuitive solution — pooling data from multiple organizations — is fundamentally incompatible with modern privacy regulations. Regulations such as the General Data Protection Regulation (GDPR) in Europe, the Health Insurance Portability and Accountability Act (HIPAA) in the United States, and India's Digital Personal Data Protection Act (DPDPA, 2023) impose strict constraints on the sharing of sensitive network telemetry data. Raw network traffic can contain personally identifiable information (PII), internal IP address schemas, proprietary system architectures, and business-critical communication patterns. Sharing this data creates unacceptable legal, competitive, and security risks.

### 1.2 Problem Statement

How can multiple organizations collaboratively train a high-accuracy intrusion detection model without sharing their raw, private network traffic data, while simultaneously ensuring that the model's predictions are interpretable and trustworthy?

### 1.3 Proposed Solution: XFed-IDS

We propose XFed-IDS, a framework that addresses this problem through three integrated components:

1. **Federated Learning (FL):** Instead of centralizing data, XFed-IDS distributes a global neural network model to each participating organization. Each organization trains the model locally on its private data and sends back only the updated model weights (mathematical parameters). The central server aggregates these weights to produce an improved global model.

2. **Non-IID Robustness via FedProx:** In practice, different organizations encounter vastly different distributions of attack types — a hospital may face ransomware while a bank sees credential stuffing. This "Non-IID" (Non-Independent and Identically Distributed) data heterogeneity is a known challenge for federated systems. We evaluate FedProx, which adds a proximal regularization term to handle this statistical heterogeneity.

3. **SHAP-Based Explainability:** Deep learning models are often criticized as "black boxes." In cybersecurity, a SOC analyst cannot afford to blindly trust an automated alert. XFed-IDS employs SHAP (SHapley Additive exPlanations) to decompose every prediction into per-feature contributions, answering the question: "Which specific network characteristics caused this traffic to be flagged as malicious?"

### 1.4 Contributions

Our key contributions are:
- **End-to-end FL + IDS + XAI framework** — filling the gap identified by Yenduri et al. (2022).
- **Empirical proof of minimal privacy cost** — only 0.08% accuracy degradation vs. centralized training.
- **Quantified benefit for small organizations** — +2.5% accuracy boost for data-poor clients joining the federation.
- **Live deployment architecture** — a FastAPI backend + React dashboard demonstrating real-time federated inference with on-the-fly SHAP explanations.
- **Feature importance ranking** — identifying Packet Length Variance, Fwd Seg Size Min, and SYN Flag Count as top attack indicators.

---

## 2. Literature Review

### 2.1 Machine Learning for Intrusion Detection

Traditional signature-based IDS (e.g., Snort, Suricata) rely on pattern-matching against known attack signatures and are inherently blind to zero-day attacks. ML-based IDS leverage statistical learning to detect anomalous patterns in network traffic features such as flow duration, packet sizes, flag counts, and inter-arrival times.

Sharafaldin et al. (2018) introduced the CICIDS-2017 dataset, providing realistic labeled traffic for benchmarking ML-based IDS. Subsequent work by Panigrahi and Borah (2018) achieved over 99% accuracy using Random Forests on this dataset in a centralized setting. Deep learning approaches — including CNNs (Wang et al., 2017), LSTMs (Kim and Ho, 2018), and autoencoders (Shone et al., 2018) — have further improved detection of complex, multi-stage attacks.

However, all these approaches assume centralized data access, which is impractical in multi-organization deployments.

### 2.2 Federated Learning

Federated Learning was formalized by McMahan et al. (2017) with the Federated Averaging (FedAvg) algorithm. FedAvg operates in communication rounds: in each round, the server sends the current global model to selected clients, each client performs local SGD updates, and the server averages the returned model updates weighted by dataset size.

Li et al. (2020) proposed FedProx to address the convergence issues FedAvg faces under heterogeneous (non-IID) data distributions. FedProx adds a proximal term to each client's local loss function, preventing local models from drifting too far from the global consensus.

Kairouz et al. (2021) provided a comprehensive survey of open problems in FL, including communication efficiency, privacy guarantees, and robustness to adversarial clients.

### 2.3 Federated Learning for Intrusion Detection

Yenduri et al. (2022) published a seminal survey identifying FL-IDS as a critical research direction, noting the gap between theoretical FL frameworks and practical IDS deployments. They specifically called for work on non-IID robustness and explainability in FL-IDS systems.

Zhao et al. (2019) demonstrated the accuracy degradation of FedAvg under non-IID settings, showing up to 55% accuracy loss on highly skewed CIFAR-10 partitions. Mothukuri et al. (2021) applied FL to IoT-based IDS but did not address explainability. Rahman et al. (2020) combined FL with differential privacy for network anomaly detection but used only shallow models (logistic regression).

### 2.4 Explainable AI (XAI) for Security

Lundberg and Lee (2017) unified several interpretability methods under the SHAP framework, grounding feature attribution in cooperative game theory (Shapley values). SHAP provides both local explanations (why a specific packet was flagged) and global explanations (which features are most important overall).

Wang et al. (2020) applied LIME and SHAP to explain random forest-based IDS decisions, demonstrating that explainability increases analyst trust and reduces false-positive investigation time. Amarasinghe et al. (2018) used attention mechanisms for interpretable deep learning IDS but did not address the federated setting.

### 2.5 Research Gap

To our knowledge, no prior work has combined all three pillars — (1) Federated Learning for privacy, (2) Non-IID robustness via FedProx, and (3) SHAP-based post-hoc explainability — into a single, deployable IDS framework with a live inference dashboard. XFed-IDS fills this gap.

---

## 3. Methodology

### 3.1 Dataset and Preprocessing

We utilized the **CICIDS-2017** dataset (Sharafaldin et al., 2018), which contains five days of network traffic (Monday-Friday) captured at the Canadian Institute for Cybersecurity. The dataset includes both benign traffic and the following attack types: DDoS, DoS (Hulk, Slowloris, SlowHTTPTest, GoldenEye), PortScan, FTP-Patator, SSH-Patator, Botnet, Web Attack (Brute Force, SQL Injection, XSS), Heartbleed, and Infiltration.

**Preprocessing Pipeline:**
1. **Column Standardization:** Stripped whitespace from all column headers across multiple CSV files.
2. **Identifier Removal:** Dropped Source IP, Destination IP, Source Port, Destination Port, Flow ID, and Timestamp columns to prevent the model from memorizing specific hosts or sessions.
3. **Numeric Conversion:** Converted all feature columns to numeric types; non-convertible entries were replaced with NaN.
4. **Cleaning:** Removed rows containing NaN or Infinity values and dropped exact duplicate rows.
5. **Binary Encoding:** Mapped all labels to binary classification — BENIGN (class 0) vs. ATTACK (class 1), grouping all attack sub-types into a single class.
6. **Feature Scaling:** Applied StandardScaler (zero-mean, unit-variance normalization) fitted on the training set and applied to the test set.
7. **Train-Test Split:** 80/20 stratified split (random seed = 42).

After preprocessing, the dataset contained **78 features** and approximately 2.8 million records.

### 3.2 Model Architecture

We employed a Multi-Layer Perceptron (MLP) implemented in PyTorch:

| Layer | Configuration |
|---|---|
| Input | 78 features |
| Hidden Layer 1 | Linear(78, 128) -> ReLU -> BatchNorm1d(128) -> Dropout(0.3) |
| Hidden Layer 2 | Linear(128, 64) -> ReLU -> BatchNorm1d(64) -> Dropout(0.3) |
| Output Layer | Linear(64, 2) -> Softmax |
| **Total Parameters** | **19,394** |

We used CrossEntropyLoss and the Adam optimizer (learning rate = 0.001). The model was trained for 20 epochs in centralized mode and 10 federated communication rounds with 1 local epoch per round.

### 3.3 Federated Learning Setup

We simulated **3 participating organizations** (clients), representing a hospital network (Client 0), a banking network (Client 1), and a university network (Client 2).

**IID Partitioning:** The training data was shuffled and split into 3 equal partitions, each client receiving a representative sample of both benign and attack traffic.

**Non-IID Partitioning:** We used a **Dirichlet distribution** (alpha = 0.5) to create realistic, heterogeneous data splits. This resulted in highly skewed distributions:
- **Client 0:** 121,077 benign samples, **only 97 attack samples** (severe class imbalance)
- **Client 1:** Received a moderate mix of both classes
- **Client 2:** Received a large portion of attack samples

**Aggregation Strategies:**
- **FedAvg:** Server averages all client model weights, weighted by the number of local training samples.
- **FedProx (mu = 0.01):** Each client's local loss is augmented with a proximal term, penalizing local model drift from the global consensus.

### 3.4 Explainability Module

We employed **SHAP KernelExplainer** (Lundberg & Lee, 2017) for post-hoc model interpretation:
- **Background Dataset:** 50 randomly sampled benign traffic instances from the test set.
- **Target Class:** Attack (class index 1). We extract the attack-class SHAP values from the 3D output array.
- **Output:** For each flagged packet, the top-5 features by absolute SHAP value are reported, along with their direction (positive = pushes toward ATTACK, negative = pushes toward BENIGN).

### 3.5 Live Deployment Architecture

Beyond offline experiments, we engineered a live deployment system:
- **Backend:** FastAPI server that loads the trained global model into memory and serves inference via REST API.
- **Simulator:** A Python script that streams 1 network packet per second from the test set to the API.
- **Frontend:** A React.js + Vite dashboard that polls the API every second, displaying real-time system stats, a live alert stream, and interactive SHAP visualizations for each detected intrusion.

---

## 4. Experimental Results

### 4.1 Detection Performance

| Experimental Setup | Aggregation | Accuracy | F1-Score | Precision | Recall | Training Time |
|---|---|---|---|---|---|---|
| Centralized Baseline | N/A | **99.87%** | 0.9987 | 0.9987 | 0.9987 | 23 min |
| Federated (IID) | FedAvg | **99.79%** | 0.9979 | 0.9979 | 0.9979 | 11 min |
| Federated (Non-IID) | FedAvg | **99.79%** | 0.9979 | 0.9979 | 0.9979 | 11 min |
| Federated (Non-IID) | FedProx (mu=0.01) | **99.44%** | 0.9943 | 0.9944 | 0.9944 | 14 min |
| Local-Only (Average) | N/A | **99.02%** | 0.9898 | -- | -- | 24 min |

**Key Observation 1: Negligible Privacy Cost.** XFed-IDS achieved 99.79% accuracy, only **0.08 percentage points** below the centralized upper bound. This empirically demonstrates that strict data privacy can be maintained with virtually no performance sacrifice.

**Key Observation 2: FedAvg Outperforms FedProx.** Counterintuitively, FedAvg (99.79%) outperformed FedProx (99.44%) in our setting. We attribute this to the relatively low task difficulty (binary classification on well-separated network features), where the proximal regularization constraint in FedProx acts as an unnecessary restriction.

### 4.2 Impact of Federation on Data-Poor Organizations

In the non-IID partitioning, Client 0 received only 97 attack samples out of 121,174 total samples.

| Setting | Client 0 Accuracy | Client 0 F1 |
|---|---|---|
| Local-Only (isolated) | **97.29%** | 0.9719 |
| Federated (Non-IID, FedAvg) | **99.79%** | 0.9979 |
| **Improvement** | **+2.50%** | **+0.026** |

By joining the XFed-IDS federation, Client 0 absorbed the attack detection knowledge from Clients 1 and 2 **without ever seeing their raw traffic**.

### 4.3 Interpretability Analysis (SHAP)

Global SHAP analysis of the federated model revealed the following top-5 features driving attack predictions:

| Rank | Feature | Role in Attack Detection |
|---|---|---|
| 1 | **Packet Length Variance** | High variance indicates automated, irregular payloads typical of DDoS |
| 2 | **Fwd Seg Size Min** | Abnormally small forward segment sizes are characteristic of crafted exploit packets |
| 3 | **SYN Flag Count** | Elevated SYN flags directly correlate with SYN flood DoS and port scanning |
| 4 | **Init Fwd Win Bytes** | Initial TCP window size manipulation used in OS fingerprinting and evasion |
| 5 | **Fwd IAT Min** | Minimum forward inter-arrival time; near-zero values indicate automated scanning |

---

## 5. Discussion

### 5.1 Limitations

1. **Binary Classification Only:** We grouped all attack types into a single ATTACK class.
2. **Simulated Federation:** We simulated 3 clients on a single machine.
3. **No Differential Privacy:** While FL protects raw data, model updates can theoretically leak information via gradient inversion attacks.
4. **Static Dataset:** CICIDS-2017 is a static benchmark. Real-world IDS must handle concept drift.

### 5.2 Future Work

- Multi-class federated classification to distinguish DDoS, PortScan, Botnet, etc.
- Differential Privacy integration using DP-SGD for formal privacy guarantees
- Byzantine-robust aggregation (e.g., Krum, Trimmed Mean) to defend against adversarial clients
- Cross-dataset federation (CICIDS-2017 + UNSW-NB15 + NSL-KDD)

---

## 6. Conclusion

XFed-IDS demonstrates that privacy-preserving, explainable intrusion detection is not only feasible but highly effective. By applying Federated Learning with FedAvg aggregation, we achieved 99.79% detection accuracy across 3 simulated organizations — suffering only a 0.08% penalty compared to the centralized ideal where all data is shared. The most impactful finding is the disproportionate benefit to data-poor organizations: an institution with only 97 local attack samples improved from 97.29% to 99.79% accuracy by joining the federation, without any participant exposing raw network traffic.

---

## References

1. Amarasinghe, K., Kenney, M., & Manic, M. (2018). Toward explainable deep neural network based anomaly detection. IEEE Conference on Human-Machine Systems.
2. Kairouz, P., McMahan, H. B., et al. (2021). Advances and open problems in federated learning. Foundations and Trends in Machine Learning, 14(1-2), 1-210.
3. Kim, J., & Ho, T. Q. (2018). LSTM-based deep learning model for network intrusion detection. IEEE Access, 6, 16694-16706.
4. Li, T., Sahu, A. K., Zaheer, M., Sanjabi, M., Talwalkar, A., & Smith, V. (2020). Federated optimization in heterogeneous networks. MLSys.
5. Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. NeurIPS, 30.
6. McMahan, B., Moore, E., Ramage, D., Hampson, S., & y Arcas, B. A. (2017). Communication-efficient learning of deep networks from decentralized data. AISTATS.
7. Mothukuri, V., Parizi, R. M., et al. (2021). A survey on security and privacy of federated learning. Future Generation Computer Systems, 115, 619-640.
8. Panigrahi, R., & Borah, S. (2018). A detailed analysis of CICIDS-2017 dataset for designing intrusion detection systems. Int. J. Engineering & Technology, 7(3.24), 479-482.
9. Rahman, S. A., Tout, H., Talhi, C., & Mourad, A. (2020). Internet of things intrusion detection: Centralized, on-device, or federated learning? IEEE Network, 34(6), 310-317.
10. Sharafaldin, I., Lashkari, A. H., & Ghorbani, A. A. (2018). Toward generating a new intrusion detection dataset and intrusion traffic characterization. ICISSP.
11. Shone, N., Ngoc, T. N., Phai, V. D., & Shi, Q. (2018). A deep learning approach to network intrusion detection. IEEE Trans. Emerging Topics in Computational Intelligence, 2(1), 41-50.
12. Wang, W., Zhu, M., Zeng, X., Ye, X., & Sheng, Y. (2017). Malware traffic classification using convolutional neural network. IEEE Int. Conf. Information Networking.
13. Wang, M., Zheng, K., Yang, Y., & Wang, X. (2020). An explainable machine learning framework for intrusion detection systems. IEEE Access, 8, 73127-73141.
14. Yenduri, G., Ramalingam, M., et al. (2022). Federated learning for intrusion detection system: Concepts, challenges and future directions. Computer Communications, 195, 346-361.
15. Zhao, Y., Li, M., Lai, L., Suda, N., Civin, D., & Chandra, V. (2019). Federated learning with non-IID data. arXiv:1806.00582.
16. Zhu, L., Liu, Z., & Han, S. (2019). Deep leakage from gradients. NeurIPS, 32.
