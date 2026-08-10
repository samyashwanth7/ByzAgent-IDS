"""XFed-IDS SHAP Explainability Module"""
import numpy as np
import torch
import shap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def _extract_attack_class(shap_values):
    """Extract SHAP values for the ATTACK class (class 1).
    
    Handles both formats:
    - list of arrays: [class0_shape, class1_shape] -> take index 1
    - single array (n_samples, n_features, n_classes) -> take [:, :, 1]
    """
    if isinstance(shap_values, list):
        return shap_values[1]  # class 1 = ATTACK
    sv = np.array(shap_values)
    if sv.ndim == 3:
        return sv[:, :, 1]  # (samples, features, classes) -> take class 1
    return sv  # already 2D


class IDSExplainer:
    def __init__(self, model, feature_names, device='cpu'):
        self.model = model
        self.model.eval()
        self.model.to(device)
        self.feature_names = feature_names
        self.device = device

    def _predict(self, X):
        if isinstance(X, np.ndarray):
            X = torch.FloatTensor(X).to(self.device)
        with torch.no_grad():
            outputs = self.model(X)
            probs = torch.softmax(outputs, dim=1)
        return probs.cpu().numpy()

    def explain(self, X_background, X_explain, max_background=100):
        if len(X_background) > max_background:
            idx = np.random.choice(len(X_background), max_background, replace=False)
            X_background = X_background[idx]
        explainer = shap.KernelExplainer(self._predict, X_background)
        shap_values = explainer.shap_values(X_explain)
        return shap_values

    def plot_summary(self, shap_values, X, save_path=None):
        plt.figure(figsize=(12, 8))
        sv = _extract_attack_class(shap_values)
        shap.summary_plot(sv, X, feature_names=self.feature_names, show=False, max_display=15)
        plt.title('XFed-IDS: Feature Importance (SHAP)', fontsize=14)
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print('SHAP summary plot saved to {}'.format(save_path))
        plt.close()

    def plot_bar(self, shap_values, X, save_path=None):
        plt.figure(figsize=(10, 6))
        sv = _extract_attack_class(shap_values)
        # sv is now (n_samples, n_features)
        mean_abs = np.abs(sv).mean(axis=0)  # shape: (n_features,)
        top_idx = np.argsort(mean_abs)[-15:][::-1].tolist()
        top_features = [self.feature_names[i] for i in top_idx]
        top_values = [float(mean_abs[i]) for i in top_idx]
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(top_features)))
        plt.barh(range(len(top_features)), top_values[::-1], color=colors)
        plt.yticks(range(len(top_features)), top_features[::-1])
        plt.xlabel('Mean |SHAP Value|')
        plt.title('XFed-IDS: Top 15 Features for Attack Detection')
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print('SHAP bar plot saved to {}'.format(save_path))
        plt.close()
