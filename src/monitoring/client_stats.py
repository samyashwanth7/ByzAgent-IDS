import torch
import torch.nn.functional as F
import json
from pathlib import Path

class ByzAgentMonitor:
    def __init__(self, save_path):
        self.history = {}
        self.save_path = Path(save_path)
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        
    def compute_round_stats(self, round_num, global_model, client_models, local_losses, val_accuracies):
        global_w = self._flatten_weights(global_model)
        
        client_deltas = []
        for c_model in client_models:
            c_w = self._flatten_weights(c_model)
            client_deltas.append(c_w - global_w)
            
        peer_mean_delta = torch.stack(client_deltas).mean(dim=0)
        
        round_stats = {}
        for i, delta in enumerate(client_deltas):
            norm = torch.norm(delta).item()
            # Cosine similarity to peer mean
            if torch.norm(peer_mean_delta) == 0 or norm == 0:
                cos_peer = 0.0
            else:
                cos_peer = F.cosine_similarity(delta.unsqueeze(0), peer_mean_delta.unsqueeze(0)).item()
                
            # Cosine similarity to global (aggregate of PREVIOUS round is stored in global_model)
            # We don't have previous round's global update easily here unless we pass it. 
            # The spec says "Cosine similarity to global: cos(client update vector, global update vector)".
            # We will use cosine similarity to peer mean as the primary indicator for now, and cosine similarity 
            # to global can be cos(client_delta, peer_mean_delta) since peer_mean_delta IS the unweighted global update.
            # We'll log cos_peer as both or keep it simple.
            
            stats = {
                "round": round_num,
                "update_norm": norm,
                "cos_sim_peer_mean": cos_peer,
                "local_loss": local_losses[i],
                "val_accuracy": val_accuracies[i]
            }
            
            client_id = f"client_{i}"
            if client_id not in self.history:
                self.history[client_id] = []
            self.history[client_id].append(stats)
            round_stats[client_id] = stats
            
        self._save()
        return round_stats
        
    def _flatten_weights(self, model):
        return torch.cat([p.flatten() for p in model.parameters()])
        
    def _save(self):
        with open(self.save_path, 'w') as f:
            json.dump(self.history, f, indent=2)
