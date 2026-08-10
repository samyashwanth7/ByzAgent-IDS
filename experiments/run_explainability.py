"""XFed-IDS: Experiment 4 -- SHAP Explainability"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import torch
import numpy as np
from config import MODEL_DIR, RESULTS_DIR, RANDOM_SEED
from src.model import IDSModel
from src.dataset import load_cicids2017
from src.explainer import IDSExplainer
from src.utils import set_seed

def run_explainability():
    set_seed(RANDOM_SEED)
    print('=' * 60)
    print('  XFed-IDS: SHAP Explainability Analysis')
    print('=' * 60)
    print('\nLoading data...')
    X_train, X_test, y_train, y_test, feature_names, label_names = load_cicids2017()
    input_dim = X_train.shape[1]
    num_classes = len(label_names)
    model = IDSModel(input_dim=input_dim, num_classes=num_classes)
    model_path = MODEL_DIR / 'federated_iid_fedavg.pt'
    if not model_path.exists():
        model_path = MODEL_DIR / 'centralized_baseline.pt'
    if not model_path.exists():
        print('No trained model found! Run centralized or federated experiment first.')
        return
    print('Loading model from {}...'.format(model_path))
    model.load_state_dict(torch.load(model_path, map_location='cpu', weights_only=True))
    explainer = IDSExplainer(model, feature_names)
    attack_indices = np.where(y_test == 1)[0]
    benign_indices = np.where(y_test == 0)[0]
    bg_idx = np.random.choice(benign_indices, min(100, len(benign_indices)), replace=False)
    X_background = X_test[bg_idx]
    atk_idx = np.random.choice(attack_indices, min(20, len(attack_indices)), replace=False)
    ben_idx = np.random.choice(benign_indices, min(10, len(benign_indices)), replace=False)
    explain_idx = np.concatenate([atk_idx, ben_idx])
    X_explain = X_test[explain_idx]
    print('\nGenerating SHAP explanations for {} samples...'.format(len(X_explain)))
    print('  Background: {} benign samples'.format(len(X_background)))
    print('  Explaining: {} attacks + {} benign'.format(len(atk_idx), len(ben_idx)))
    print('  This may take a few minutes...')
    shap_values = explainer.explain(X_background, X_explain)
    print('\nGenerating plots...')
    explainer.plot_summary(shap_values, X_explain, save_path=RESULTS_DIR / 'shap_summary.png')
    explainer.plot_bar(shap_values, X_explain, save_path=RESULTS_DIR / 'shap_bar.png')
    print('\n[OK] Explainability analysis complete!')
    print('   Plots saved to {}'.format(RESULTS_DIR))

if __name__ == '__main__':
    run_explainability()
