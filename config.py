"""XFed-IDS Configuration"""
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
RAW_DIR = DATA_DIR / 'raw'
PROCESSED_DIR = DATA_DIR / 'processed'
RESULTS_DIR = BASE_DIR / 'results'
MODEL_DIR = BASE_DIR / 'models'
LOG_DIR = BASE_DIR / 'logs'

for d in [RAW_DIR, PROCESSED_DIR, RESULTS_DIR, MODEL_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Model Architecture
INPUT_DIM = 78
NUM_CLASSES = 8
HIDDEN_DIM_1 = 128
HIDDEN_DIM_2 = 64
DROPOUT_RATE = 0.3

# Training
BATCH_SIZE = 128
LEARNING_RATE = 0.001
NUM_EPOCHS = 20
RANDOM_SEED = 42

# Federated Learning
NUM_ROUNDS = 10
NUM_CLIENTS = 3
LOCAL_EPOCHS = 3
AGG_STRATEGY = "byzagent" # 'fedavg', 'krum', 'trimmed_mean', or 'byzagent'
NON_IID_ALPHA = 0.5
BATCH_SIZE = 128
LEARNING_RATE = 0.001
FEDPROX_MU = 0.01

# ByzAgent Phase 0: Poisoning Simulation
POISON_ENABLED = True
ATTACKER_CLIENTS = [1, 2] # 2 malicious clients (sybil attack)
POISON_MODE = "sudden" # 'sudden' or 'gradual'
POISON_FRACTION_SUDDEN = 0.60 # Flip 60% of labels (make it strong to guarantee drop)
POISON_FRACTION_GRADUAL_STEP = 0.10 # +10% per round

# Classification
BINARY_CLASSIFICATION = False
ATTACK_CLASSES = [
    'BENIGN',
    'DDoS',
    'PortScan',
    'Brute Force',
    'Web Attack',
    'Infiltration',
    'Bot',
    'Heartbleed'
]

# Differential Privacy
DP_ENABLED = False
DP_EPSILON = 8.0
DP_DELTA = 1e-5
DP_CLIP_NORM = 10.0
