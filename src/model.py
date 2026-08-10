"""XFed-IDS Neural Network Model"""
import torch
import torch.nn as nn

class IDSModel(nn.Module):
    def __init__(self, input_dim=78, num_classes=2):
        super(IDSModel, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        return self.network(x)

def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
