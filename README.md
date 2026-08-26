# ByzAgent-IDS: Agentic Byzantine Trust Diagnosis for Federated Intrusion Detection

ByzAgent-IDS (formerly XFed-IDS) is an advanced Federated Learning framework for network intrusion detection. It introduces an **Agentic AI Trust Arbiter** to detect and neutralize Byzantine poisoning attacks (such as label-flipping) from malicious clients.

Instead of relying on rigid, single-round mathematical thresholds (like Krum or Trimmed-Mean) which are highly vulnerable to Sybil attacks and slow-drip adaptive poisoning, **ByzAgent** extracts behavioral statistics over a rolling history and feeds them to a Large Language Model (LLM). The agent reasons over these temporal trends to dynamically **trust, downweight, or quarantine** malicious clients, providing natural language explanations for its actions to SOC analysts.

## Key Contributions & Features
1. **Agentic Aggregation (Phase 3):** An LLM-powered (LangChain + Groq API) aggregator that analyzes 4 key behavioral metrics (Update Norm, Peer Cosine Similarity, Local Loss, Validation Drop) to quarantine poisoned updates.
2. **Robust Baseline Analysis (Phase 2):** Includes Krum and Trimmed-Mean aggregators, successfully proving that traditional mathematical defenses fail when attackers form a majority (Sybil attack).
3. **Poisoning Simulator (Phase 0-1):** Simulates both Sudden and Gradual label-flipping attacks across distributed organizations.
4. **Deep Explainability:** SHAP-based feature importance mapping to understand the PyTorch MLP's underlying network packet classifications.
5. **Real-time Dashboard:** A React + FastAPI frontend to visualize agent decisions, confusion matrices, and model accuracy across rounds.

## Architecture

```
[ CICIDS-2017 Data ] --> [ PyTorch Clients (Local Training) ]
                                      |
                               (Model Updates)
                                      v
[ ByzAgent Arbiter ] <-- [ Behavioral Stats Extractor ]
(LLM JSON Decision)                   |
        |                             v
        +-------------------> [ Aggregation ] --> [ Global Model ]
```

## How to Run the Federated Experiment

1. **Setup Environment**
```bash
pip install -r requirements.txt
```

2. **Configure the Strategy**
Edit `config.py` to set the attack scenarios and defenses:
```python
POISON_ENABLED = True
ATTACKER_CLIENTS = [1, 2] # Test a Sybil Attack
AGG_STRATEGY = "byzagent" # Choose: 'fedavg', 'krum', 'trimmed_mean', or 'byzagent'
```

3. **Run the Simulation**
```bash
python experiments/run_federated.py
```
*Note: If using `byzagent`, ensure you have a `.env` file with a valid `GROQ_API_KEY`.*

## Results: The Krum Failure vs. ByzAgent Success
During testing with 3 clients (2 Attackers, 1 Clean):
- **Krum** mistakenly trusted the attackers (because they formed a mathematical majority cluster) and rejected the clean client, crashing the model accuracy to `84.9%`.
- **ByzAgent** recognized the massive spike in the attackers' `local_loss` and drop in `val_accuracy`, successfully quarantining both attackers and maintaining a `98.6%` global accuracy. 

### The Solution: Federated Learning (FL)
XFed-IDS solves this using **Federated Learning**. Instead of bringing the data to the model, we bring the model to the data:
1. A central server initializes a global neural network model.
2. The server sends this model to all participating organizations (clients).
3. Each organization trains the model locally on their own private, isolated network traffic data.
4. Instead of sending data back, each organization only sends the **updated mathematical weights** of their model back to the central server.
5. The server averages these weights (using algorithms like FedAvg or FedProx) to create a smarter global model, and sends it back to the clients.

**Result:** A highly accurate intrusion detection system trained collaboratively across multiple institutions, with **zero raw data exchanged**, preserving 100% privacy.

### The Innovation: Explainable AI (XAI)
A major critique of Deep Learning in cybersecurity is that models act as "black boxes." When the system flags an alert, Security Operations Center (SOC) analysts don't know *why*.
XFed-IDS integrates **SHAP (SHapley Additive exPlanations)**. For every detected attack, the system mathematically calculates exactly which network features (e.g., Packet Length, SYN Flag Count) triggered the alert, providing analysts with actionable intelligence rather than just a binary "Attack/Benign" output.

---

## 🏗️ System Architecture & Implementation Details

The project is structured into three main engineering pillars:

### 1. The Machine Learning Engine
- **Dataset:** CICIDS-2017 (78 network features, binary classification: Benign vs. Attack).
- **Model Architecture:** A Multi-Layer Perceptron (MLP) built with PyTorch. It features an input layer of 78 nodes, hidden layers (128 and 64 nodes) with ReLU activations, Batch Normalization, and Dropout (30%) to prevent overfitting, outputting to 2 classes.
- **Federated Strategies:** 
  - **FedAvg:** Averages the weights from all clients equally.
  - **FedProx:** A mathematical regularization technique added to handle "Non-IID" (statistically heterogeneous) data, where one organization might have vastly different types of attacks than another.

### 2. The Live Backend API (FastAPI)
Rather than just running static scripts, the project features a live production-grade Python backend:
- **FastAPI Server:** Hosts the trained global model in memory.
- **Traffic Simulator:** A script that continuously pumps random packets from the CICIDS test dataset into the API at a rate of 1 packet per second, simulating real-world network traffic.
- **Inference Pipeline:** The API receives a packet, runs it through the PyTorch model, and if an attack is detected, instantly triggers the SHAP KernelExplainer to calculate feature importance on the fly.
- **Continuous Learning (The Analyst Loop):** When SOC analysts confirm an attack or flag a false positive in the dashboard, the API captures the raw network packet features. 
- **Hot-Swap Retraining:** A background process can be triggered to inject these newly labeled analyst samples into the training pool, run a fresh federated training round, and hot-swap the new, smarter global model into memory without ever taking the server offline.

### 3. The Premium Frontend Dashboard (React.js)
A modern, dark-themed React web application that serves as the SOC interface:
- **Live Monitoring:** Uses `fetch` polling to pull live stats, system uptime, and federated accuracy from the API.
- **Real-time Alert Stream:** Displays intrusions the moment they are detected by the backend.
- **Visual Explainability:** Renders SHAP arrays dynamically using `recharts` to show analysts exactly which features pushed the model to predict an attack.

---

## 📊 Experimental Setup & Key Findings

We simulated an environment with 3 distinct organizations. We tested Centralized training (sharing all data) vs. Federated training under various data distribution conditions.

| Experimental Setup | Accuracy | F1 Score | Privacy Preserved |
|---|---|---|---|
| **Centralized (Ideal Bound)** | 99.87% | 0.9987 | ❌ No |
| **Federated IID (FedAvg)** | 99.79% | 0.9979 | ✅ Yes |
| **Federated Non-IID (FedAvg)** | 99.79% | 0.9979 | ✅ Yes |
| **Federated Non-IID (FedProx)** | 99.44% | 0.9943 | ✅ Yes |
| **Local Only (Client isolated)** | 99.02% | 0.9898 | ✅ Yes |

### 🏆 The "Killer Finding"
To prove the value of FL, we simulated a "data-poor" organization (Client 0) that had only 97 local attack samples in its historical data.
- When Client 0 trained a model entirely on its own, it achieved **97.29% accuracy**.
- When Client 0 joined the XFed-IDS federation, its accuracy jumped to **99.79%**.
- **Conclusion:** By joining the federation, the small organization gained the knowledge of larger organizations' attacks without ever seeing their private data, resulting in a massive +2.5% accuracy boost. Furthermore, the overall privacy penalty compared to a centralized database was less than 0.1%.

---

## 🚀 How to Run the Project

### 1. Prerequisites
```bash
# Clone the repository
git clone https://github.com/samyashwanth7/XFed-IDS.git
cd XFed-IDS

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Download Data
Download the [Kaggle CICIDS2017 Dataset](https://www.kaggle.com/datasets/ciaboricmendez/cicids2017) and place the CSV files inside `data/raw/`. The system handles all preprocessing automatically.

### 3. Start the Live System
To launch the end-to-end live demonstration:

**Terminal 1 (Backend API):**
```bash
cd backend
uvicorn api:app --reload
```

**Terminal 2 (Traffic Simulator):**
```bash
cd backend
python simulate_traffic.py
```

**Terminal 3 (React Frontend):**
```bash
cd dashboard
npm install
npm run dev
```
Open `http://localhost:5173` in your browser to view the live SOC dashboard.

---

## 📝 Academic References
- Yenduri et al. (2022) — *"Federated Learning for Intrusion Detection System: Concepts, Challenges and Future Directions"* (Computer Communications, Vol. 195)
- Lundberg & Lee (2017) — *"A Unified Approach to Interpreting Model Predictions"* (SHAP)
