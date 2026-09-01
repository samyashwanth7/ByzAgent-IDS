# ByzAgent

**Catching poisoned clients in federated learning by letting an LLM read their stats instead of trusting a formula.**

---

## What this is

ByzAgent is a federated intrusion detection system built on PyTorch + CICIDS-2017. Multiple organizations (simulated as 3 clients) train a shared MLP on their local network traffic without exchanging raw data. The catch: some of those clients are adversarial. They flip labels to sabotage the global model.

The standard defense against this kind of Byzantine attack is an algorithm called [Krum](https://proceedings.neurips.cc/paper/2017/hash/f4b9ec30ad9f68f89b29639786cb62ef-Abstract.html), which picks the client update closest to its neighbors. The problem we found (and proved empirically) is that when attackers outnumber honest clients, Krum selects the *wrong* side. Two poisoned clients form a tighter cluster than one clean one. Krum trusts the majority. Accuracy crashes to 84.9%.

**ByzAgent replaces that formula with an LLM.** Each round, we extract four behavioral signals from every client (update norm, cosine similarity to peers, local training loss, validation accuracy on a held-out set) and pass them as structured JSON to a language model via LangChain + Groq. The model returns a decision per client: 	rust, downweight, or quarantine, along with a one-sentence explanation. No retraining of the LLM. No fine-tuning. Just a well-crafted prompt and structured output parsing.

It works. 98.97% accuracy under the same 2-attacker scenario where Krum fails.

## Why this matters

Most Byzantine-resilient aggregation schemes assume the number of attackers is strictly less than half the pool. In practice that assumption breaks all the time (compromised IoT devices, Sybil nodes, colluding insiders). We needed something that doesn't depend on a static threshold. An LLM can look at *what the numbers mean* instead of just computing distances between weight vectors.

There's a growing body of work on using LLMs as reasoning engines inside ML pipelines, but as far as we could find, nobody had plugged one into federated aggregation as a trust arbiter. That's the gap.

## Results

| Strategy | Accuracy | F1 | What happens |
|---|---|---|---|
| FedAvg (no defense) | 96.16% | 0.9567 | Poisoned weights drag it down |
| Krum | 84.90% | 0.8402 | Trusts the attackers, rejects the clean client |
| **ByzAgent** | **98.97%** | **0.9889** | Quarantines both attackers every round |

10 rounds, 3 local epochs each, CICIDS-2017 (2.8M rows), 2 out of 3 clients performing sudden label-flip attacks with 60% flip rate.

## Project layout

`
src/
  model.py             # 3-layer MLP (78 -> 128 -> 64 -> 8)
  dataset.py           # CICIDS-2017 loader + IID/non-IID partitioning
  utils.py             # training loops, evaluation, DP clipping
  attacks/
    label_flip.py      # sudden + gradual label-flipping simulator
  monitoring/
    client_stats.py    # per-round stat extraction (norm, cosine, loss, val_acc)
  aggregation/
    robust_baselines.py  # Krum + Trimmed-Mean implementations
  agents/
    byz_agent.py       # the LLM trust arbiter (LangChain + Groq)
experiments/
  run_federated.py     # main training loop with poisoning + ByzAgent
  run_centralized.py   # single-model baseline
  run_explainability.py  # SHAP analysis
backend/
  api.py               # FastAPI server for the dashboard
dashboard/             # React + Recharts frontend
`

## Running it

`ash
# install
pip install -r requirements.txt

# preprocess the dataset (expects CICIDS-2017 CSVs in data/raw/)
python src/dataset.py

# run the federated experiment with ByzAgent
# edit config.py to set AGG_STRATEGY, ATTACKER_CLIENTS, POISON_MODE
python experiments/run_federated.py

# start the dashboard
cd backend && uvicorn api:app --reload &
cd dashboard && npm run dev
`

You need a .env file with GROQ_API_KEY=your_key for the LLM calls. Free tier works fine.

## The interesting file

If you only read one file, read [src/agents/byz_agent.py](src/agents/byz_agent.py). It's ~80 lines. The prompt engineering is where the actual research contribution lives: telling the LLM what each metric means, what combinations signal poisoning, and forcing structured JSON output so we can parse the decisions programmatically.

## Built with

- PyTorch (model + federated training loop, no Flower/PySyft dependency)
- LangChain + Groq (LLM integration)
- SHAP (prediction explainability)
- FastAPI + React + Recharts (monitoring dashboard)
- CICIDS-2017 dataset

## Authors

Shaashwat Agrawal and team, VIT-AP University, 2026.

---

*This started as a plain federated IDS project. The ByzAgent layer came from asking: what if the server could actually understand why a client looks wrong, instead of just measuring how far away it is?*
