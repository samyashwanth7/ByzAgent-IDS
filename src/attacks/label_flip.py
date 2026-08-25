import torch
from torch.utils.data import DataLoader, TensorDataset

def apply_label_flip(dataloader, round_num, mode='sudden', sudden_frac=0.4, gradual_step=0.05, num_classes=8):
    if mode == 'sudden':
        fraction = sudden_frac
    elif mode == 'gradual':
        fraction = min(1.0, gradual_step * round_num)
    else:
        fraction = 0.0
        
    if fraction <= 0.0:
        return dataloader

    x_list, y_list = [], []
    for x, y in dataloader:
        x_list.append(x)
        y_list.append(y)
        
    X = torch.cat(x_list)
    Y = torch.cat(y_list)
    
    num_samples = len(Y)
    num_to_flip = int(num_samples * fraction)
    
    if num_to_flip == 0:
        return dataloader

    flip_indices = torch.randperm(num_samples)[:num_to_flip]
    
    for idx in flip_indices:
        if Y[idx] == 0:
            Y[idx] = torch.randint(1, num_classes, (1,)).item()
        else:
            Y[idx] = 0

    poisoned_dataset = TensorDataset(X, Y)
    return DataLoader(poisoned_dataset, batch_size=dataloader.batch_size, shuffle=True)
