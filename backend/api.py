import sys
import os
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel
import numpy as np
import torch
import shap

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# Ensure imports work from the root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import MODEL_DIR
from src.model import IDSModel
from src.dataset import load_cicids2017

app = FastAPI(title="XFed-IDS Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globals
model = None
feature_names = []
explainer = None
alerts_db = []
alert_id_counter = 1050

def _extract_attack_class(shap_values):
    if isinstance(shap_values, list):
        return shap_values[1]
    sv = np.array(shap_values)
    if sv.ndim == 3:
        return sv[:, :, 1]
    return sv

@app.on_event("startup")
def load_resources():
    global model, feature_names, explainer
    print("Loading dataset metadata...")
    X_train, X_test, y_train, y_test, f_names, label_names = load_cicids2017()
    feature_names = f_names
    
    print("Loading global federated model...")
    model = IDSModel(input_dim=len(feature_names), num_classes=2)
    model.load_state_dict(torch.load(MODEL_DIR / 'federated_iid_fedavg.pt', map_location='cpu', weights_only=True))
    model.eval()
    
    print("Initializing SHAP KernelExplainer...")
    def predict_fn(X):
        with torch.no_grad():
            out = model(torch.FloatTensor(X))
            return torch.softmax(out, dim=1).numpy()
            
    # Use 50 benign background samples for SHAP
    bg = X_test[np.where(y_test==0)[0][:50]]
    explainer = shap.KernelExplainer(predict_fn, bg)
    print("API is ready.")

class PredictRequest(BaseModel):
    features: list[float]
    source_ip: str
    node: str

@app.post("/predict")
def predict(req: PredictRequest):
    global alert_id_counter
    
    # 1. Predict
    X = np.array(req.features).reshape(1, -1)
    with torch.no_grad():
        out = model(torch.FloatTensor(X))
        probs = torch.softmax(out, dim=1).numpy()[0]
        
    pred_class = int(np.argmax(probs))
    confidence = float(probs[pred_class] * 100)
    
    result = {
        "prediction": "ATTACK" if pred_class == 1 else "BENIGN",
        "confidence": round(confidence, 2),
        "source_ip": req.source_ip,
        "node": req.node,
        "is_alert": False
    }
    
    # 2. If attack, generate SHAP explanation and save alert
    if pred_class == 1:
        sv = explainer.shap_values(X)
        sv_attack = _extract_attack_class(sv)[0] # get the 1D array for this sample
        
        # Sort by absolute SHAP value
        top_idx = np.argsort(np.abs(sv_attack))[-5:][::-1]
        shap_data = [{"feature": feature_names[i], "value": float(sv_attack[i])} for i in top_idx]
        
        alert = {
            "id": f"AL-{alert_id_counter}",
            "type": "Network Intrusion", # We treat all class 1 as general intrusion here
            "confidence": round(confidence, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sourceIp": req.source_ip,
            "status": "critical" if confidence > 90 else "warning",
            "node": req.node,
            "shap": shap_data
        }
        alerts_db.insert(0, alert) # Put newest first
        if len(alerts_db) > 50:
            alerts_db.pop() # Keep last 50
            
        alert_id_counter += 1
        result["is_alert"] = True
        result["alert_id"] = alert["id"]
        
    return result

@app.get("/alerts")
def get_alerts():
    return alerts_db

@app.get("/stats")
def get_stats():
    return {
        "totalAlerts": 1432 + len(alerts_db),
        "activeNodes": 3,
        "globalAccuracy": 99.79,
        "centralizedAccuracy": 99.87,
        "uptime": "Live Simulation",
        "lastUpdate": datetime.now().strftime("%H:%M:%S")
    }
