import sys
import os
import csv
import subprocess
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
import numpy as np
import torch
import shap

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# Ensure imports work from the root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import MODEL_DIR, BASE_DIR, ATTACK_CLASSES, DP_ENABLED, DP_EPSILON
from src.model import IDSModel
from src.dataset import load_cicids2017
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score

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
label_names = []
explainer = None
alerts_db = []
alert_id_counter = 1050
model_version = "v1.0"
is_retraining = False

# Cached test data for analytics
_X_test = None
_y_test = None

# Feedback storage path
FEEDBACK_DIR = BASE_DIR / 'data' / 'feedback'
FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)
CONFIRMED_ATTACKS_FILE = FEEDBACK_DIR / 'confirmed_attacks.csv'
CONFIRMED_BENIGN_FILE = FEEDBACK_DIR / 'confirmed_benign.csv'

def _extract_shap_for_class(shap_values, class_idx):
    """Extract SHAP values for a specific predicted class."""
    if isinstance(shap_values, list):
        return shap_values[class_idx]
    sv = np.array(shap_values)
    if sv.ndim == 3:
        return sv[:, :, class_idx]
    return sv

def _load_model_and_explainer():
    """Load the global model and reinitialize the SHAP explainer."""
    global model, feature_names, label_names, explainer, _X_test, _y_test
    print("Loading dataset metadata...")
    X_train, X_test, y_train, y_test, f_names, l_names = load_cicids2017()
    feature_names = f_names
    label_names = l_names
    _X_test = X_test
    _y_test = y_test
    
    num_classes = len(label_names)
    print("Loading global federated model ({} classes)...".format(num_classes))
    model = IDSModel(input_dim=len(feature_names), num_classes=num_classes)
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
    print("Model and explainer loaded successfully.")

@app.on_event("startup")
def load_resources():
    _load_model_and_explainer()
    print("API is ready.")

# ========== Prediction ==========

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
        "prediction": label_names[pred_class] if pred_class < len(label_names) else "UNKNOWN",
        "confidence": round(confidence, 2),
        "source_ip": req.source_ip,
        "node": req.node,
        "is_alert": False
    }
    
    # 2. If NOT benign (class 0), generate SHAP explanation and save alert
    if pred_class != 0:
        sv = explainer.shap_values(X)
        sv_class = _extract_shap_for_class(sv, pred_class)[0]
        
        # Sort by absolute SHAP value
        top_idx = np.argsort(np.abs(sv_class))[-5:][::-1]
        shap_data = [{"feature": feature_names[i], "value": float(sv_class[i])} for i in top_idx]
        
        attack_name = label_names[pred_class] if pred_class < len(label_names) else "Unknown Attack"
        alert = {
            "id": f"AL-{alert_id_counter}",
            "type": attack_name,
            "confidence": round(confidence, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sourceIp": req.source_ip,
            "status": "critical" if confidence > 90 else "warning",
            "node": req.node,
            "shap": shap_data,
            "features": req.features,
            "analyst_verdict": None
        }
        alerts_db.insert(0, alert)
        if len(alerts_db) > 100:
            alerts_db.pop()
            
        alert_id_counter += 1
        result["is_alert"] = True
        result["alert_id"] = alert["id"]
        
    return result

# ========== Alerts ==========

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
        "lastUpdate": datetime.now().strftime("%H:%M:%S"),
        "modelVersion": model_version,
        "isRetraining": is_retraining,
        "feedbackCount": _count_feedback(),
        "dpEnabled": DP_ENABLED,
        "dpEpsilon": DP_EPSILON,
        "numClasses": len(label_names)
    }

# ========== Model Analytics ==========

@app.get("/analytics")
def get_analytics():
    """Return confusion matrix and per-class metrics from test set."""
    if _X_test is None or _y_test is None:
        return {"error": "Model not loaded yet"}
    
    with torch.no_grad():
        out = model(torch.FloatTensor(_X_test))
        preds = torch.argmax(out, dim=1).numpy()
    
    # Confusion matrix
    cm = confusion_matrix(_y_test, preds, labels=list(range(len(label_names))))
    
    # Per-class metrics
    per_class = []
    for i, name in enumerate(label_names):
        mask_true = (_y_test == i)
        mask_pred = (preds == i)
        tp = int(np.sum(mask_true & mask_pred))
        support = int(np.sum(mask_true))
        
        if support > 0:
            prec = float(precision_score(_y_test == i, preds == i, zero_division=0))
            rec = float(recall_score(_y_test == i, preds == i, zero_division=0))
            f1 = float(f1_score(_y_test == i, preds == i, zero_division=0))
        else:
            prec = rec = f1 = 0.0
        
        per_class.append({
            "name": name,
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "support": support
        })
    
    overall_acc = float(np.mean(preds == _y_test))
    
    return {
        "confusion_matrix": cm.tolist(),
        "class_names": label_names,
        "per_class_metrics": per_class,
        "overall_accuracy": round(overall_acc, 4),
        "dp_enabled": DP_ENABLED,
        "dp_epsilon": DP_EPSILON
    }

# ========== Analyst Feedback Loop ==========

class FeedbackRequest(BaseModel):
    alert_id: str
    verdict: str  # "confirm_attack" or "false_positive"

def _count_feedback():
    """Count total feedback samples saved."""
    count = 0
    for f in [CONFIRMED_ATTACKS_FILE, CONFIRMED_BENIGN_FILE]:
        if f.exists():
            with open(f, 'r') as fh:
                count += sum(1 for _ in fh) - 1  # subtract header
    return max(count, 0)

@app.post("/feedback")
def submit_feedback(req: FeedbackRequest):
    """SOC analyst confirms or rejects an alert. The raw features are saved
    as new labeled training data for the next federated retraining round."""
    
    # Find the alert
    alert = None
    for a in alerts_db:
        if a["id"] == req.alert_id:
            alert = a
            break
    
    if alert is None:
        return {"status": "error", "message": f"Alert {req.alert_id} not found"}
    
    if alert.get("features") is None:
        return {"status": "error", "message": "No raw features stored for this alert"}
    
    # Determine label based on verdict
    if req.verdict == "confirm_attack":
        label = 1
        target_file = CONFIRMED_ATTACKS_FILE
        alert["analyst_verdict"] = "confirmed"
    elif req.verdict == "false_positive":
        label = 0
        target_file = CONFIRMED_BENIGN_FILE
        alert["analyst_verdict"] = "false_positive"
    else:
        return {"status": "error", "message": "verdict must be 'confirm_attack' or 'false_positive'"}
    
    # Write features + label to CSV
    write_header = not target_file.exists()
    with open(target_file, 'a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(feature_names + ['label'])
        writer.writerow(alert["features"] + [label])
    
    return {
        "status": "ok",
        "message": f"Feedback saved for {req.alert_id} as {'ATTACK' if label == 1 else 'BENIGN'}",
        "total_feedback_samples": _count_feedback()
    }

# ========== Model Retraining ==========

@app.post("/retrain")
def trigger_retrain(background_tasks: BackgroundTasks):
    """Trigger a new round of federated retraining using original data + analyst feedback."""
    global is_retraining
    
    if is_retraining:
        return {"status": "busy", "message": "Retraining is already in progress"}
    
    is_retraining = True
    background_tasks.add_task(_run_retrain)
    return {"status": "started", "message": "Federated retraining started in background. The global model will be updated automatically."}

def _run_retrain():
    """Background task that runs the retraining script and reloads the model."""
    global is_retraining, model_version
    try:
        retrain_script = Path(__file__).parent / 'retrain_federated.py'
        print(f"[RETRAIN] Starting federated retraining via {retrain_script}")
        result = subprocess.run(
            [sys.executable, str(retrain_script)],
            capture_output=True, text=True, timeout=3600
        )
        print(f"[RETRAIN] stdout: {result.stdout[-500:]}")
        if result.returncode != 0:
            print(f"[RETRAIN] FAILED: {result.stderr[-500:]}")
        else:
            # Reload the updated model
            _load_model_and_explainer()
            model_version = f"v{datetime.now().strftime('%Y%m%d_%H%M')}"
            print(f"[RETRAIN] SUCCESS. Model updated to {model_version}")
    except Exception as e:
        print(f"[RETRAIN] ERROR: {e}")
    finally:
        is_retraining = False

# ========== Model Hot-Swap ==========

@app.post("/model/reload")
def reload_model():
    """Manually reload the model from disk without restarting the server."""
    global model_version
    try:
        _load_model_and_explainer()
        model_version = f"v{datetime.now().strftime('%Y%m%d_%H%M')}"
        return {"status": "ok", "message": f"Model reloaded. Version: {model_version}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

