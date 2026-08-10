# Analyst Feedback Data

This directory stores analyst-confirmed samples used for federated retraining.

## Expected Files

| File | Description |
|------|-------------|
| `confirmed_attacks.csv` | Analyst-verified attack samples (78 feature columns + `label` column with value `1`) |
| `confirmed_benign.csv` | Analyst-verified benign samples (78 feature columns + `label` column with value `0`) |

## Schema

Each CSV must contain:
- **78 numeric feature columns** matching the CICIDS-2017 feature set (StandardScaler-transformed).
- A **`label`** column: `0` = BENIGN, `1` = ATTACK.

These files are consumed by `backend/retrain_federated.py` during continual
federated retraining. They are merged into the base CICIDS-2017 training data
before re-partitioning across clients.
