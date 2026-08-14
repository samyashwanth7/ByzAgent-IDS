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
BATCH_SIZE = 256
LEARNING_RATE = 0.001
NUM_EPOCHS = 20
RANDOM_SEED = 42

# Federated Learning
NUM_CLIENTS = 3
NUM_ROUNDS = 10
LOCAL_EPOCHS = 1
NON_IID_ALPHA = 0.5
FEDPROX_MU = 0.01

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
DP_ENABLED = True
DP_EPSILON = 8.0
DP_DELTA = 1e-5
DP_CLIP_NORM = 10.0
