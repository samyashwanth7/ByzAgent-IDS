# XFed-IDS: Explainable Federated Intrusion Detection System

> **A multi-organization federated learning framework for network intrusion detection with SHAP-based explainability.**

---

## 👨‍🏫 Project Overview (For Evaluators & Teachers)

### The Problem: Data Silos in Cybersecurity
In modern cybersecurity, Intrusion Detection Systems (IDS) rely on Machine Learning models to detect zero-day attacks. However, a model is only as good as the data it is trained on. Different organizations (e.g., hospitals, banks, universities) experience different types of cyberattacks. 
Ideally, they would pool their network traffic data together to train a massive, highly accurate global model. But due to strict privacy laws (like GDPR, HIPAA) and corporate confidentiality, **organizations cannot legally share their raw network traffic data**.

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
