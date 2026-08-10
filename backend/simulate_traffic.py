import sys
import os
import time
import random
import requests
import numpy as np

# Ensure imports work from the root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.dataset import load_cicids2017

print("Loading dataset for simulation...")
X_train, X_test, y_train, y_test, feature_names, label_names = load_cicids2017()

API_URL = "http://localhost:8000/predict"
NODES = ["Hospital-Node-1", "Bank-Node-2", "Uni-Node-3"]

def simulate():
    print(f"Started live traffic simulation. Sending 1 packet per second to {API_URL}")
    while True:
        try:
            # Pick a random sample from the test set
            # We want to artificially inflate attack frequency slightly so we see alerts on the dashboard
            if random.random() < 0.2: # 20% chance of an attack sample
                idx = random.choice(np.where(y_test == 1)[0])
            else:
                idx = random.choice(np.where(y_test == 0)[0])
                
            features = X_test[idx].tolist()
            
            # Generate a fake source IP
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
                if result.get("is_alert"):
                    print(f"[ALERT] Intrustion detected on {node} from {source_ip} (Confidence: {result['confidence']}%)")
                else:
                    print(f"[PASS] Traffic on {node} is BENIGN.")
            else:
                print(f"API Error: {resp.status_code}")
                
        except Exception as e:
            print(f"Simulation error: {e}")
            
        time.sleep(1) # Send 1 packet per second

if __name__ == "__main__":
    # Wait a few seconds for the API to start up if we run them together
    time.sleep(5)
    simulate()
