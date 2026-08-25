import torch
import copy

def krum_aggregate(global_model, client_models, f=1):
    n = len(client_models)
    num_neighbors = max(1, n - f - 1) if n > 2 else 1
    
    client_weights = []
    for model in client_models:
        flat_w = torch.cat([p.flatten() for p in model.parameters()])
        client_weights.append(flat_w)
        
    scores = []
    for i in range(n):
        distances = []
        for j in range(n):
            if i == j:
                continue
            dist = torch.sum((client_weights[i] - client_weights[j]) ** 2).item()
            distances.append(dist)
        
        distances.sort()
        score = sum(distances[:num_neighbors])
        scores.append(score)
        
    best_client_idx = scores.index(min(scores))
    
    new_dict = copy.deepcopy(client_models[best_client_idx].state_dict())
    global_model.load_state_dict(new_dict)
    return global_model, best_client_idx

def trimmed_mean_aggregate(global_model, client_models, trim_count=1):
    n = len(client_models)
    if 2 * trim_count >= n:
        trim_count = max(0, (n - 1) // 2)
        
    new_dict = copy.deepcopy(global_model.state_dict())
    
    for key in new_dict.keys():
        stacked_params = torch.stack([m.state_dict()[key].float() for m in client_models], dim=0)
        
        if trim_count > 0:
            sorted_params, _ = torch.sort(stacked_params, dim=0)
            trimmed_params = sorted_params[trim_count : n - trim_count]
            new_dict[key] = trimmed_params.mean(dim=0)
        else:
            new_dict[key] = stacked_params.mean(dim=0)
            
    global_model.load_state_dict(new_dict)
    return global_model
