import sys
import os
import time
import random
import requests
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.dataset import load_cicids2017

print("Loading dataset for simulation...")
X_train, X_test, y_train, y_test, feature_names, label_names = load_cicids2017()

API_URL = "http://localhost:8000/predict"
NODES = ["Hospital-Node-1", "Bank-Node-2", "Uni-Node-3"]

# Pre-index samples by class so we can pick from any class equally
class_indices = {}
for cls_id in range(len(label_names)):
    indices = np.where(y_test == cls_id)[0]
    if len(indices) > 0:
        class_indices[cls_id] = indices
        print(f"  Class {cls_id} ({label_names[cls_id]}): {len(indices)} test samples")

attack_class_ids = [c for c in class_indices if c != 0]
print(f"\nAvailable attack classes: {[label_names[c] for c in attack_class_ids]}")

def simulate():
    print(f"\nStarted live traffic simulation. Sending 1 packet/sec to {API_URL}")
    print("Press Ctrl+C to stop.\n")
    while True:
        try:
            # 35% chance of attack, and when attack, pick UNIFORMLY from all attack classes
            if random.random() < 0.35 and attack_class_ids:
                chosen_class = random.choice(attack_class_ids)
                idx = random.choice(class_indices[chosen_class])
            else:
                idx = random.choice(class_indices[0])

            features = X_test[idx].tolist()
            true_label = label_names[int(y_test[idx])]
            source_ip = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
            node = random.choice(NODES)

            payload = {
                "features": features,
                "source_ip": source_ip,
                "node": node
            }

            resp = requests.post(API_URL, json=payload)
            if resp.status_code == 200:
                result = resp.json()
                pred = result.get("prediction", "?")
                conf = result.get("confidence", 0)
                if result.get("is_alert"):
                    print(f"  [ALERT] {pred} detected on {node} from {source_ip} (conf: {conf}%, true: {true_label})")
                else:
                    print(f"  [OK]    BENIGN on {node} (true: {true_label})")
            else:
                print(f"  API Error: {resp.status_code}")

        except requests.ConnectionError:
            print("  Waiting for API to start...")
        except Exception as e:
            print(f"  Error: {e}")

        time.sleep(0.8)

if __name__ == "__main__":
    time.sleep(3)
    simulate()
