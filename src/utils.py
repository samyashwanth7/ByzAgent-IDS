"""XFed-IDS Utility Functions"""
import torch
import torch.nn as nn
import numpy as np
import json
import random
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def get_device():
    if torch.cuda.is_available():
        return torch.device('cuda')
    return torch.device('cpu')

def train_one_epoch(model, dataloader, optimizer, criterion, device):
    model.train()
    model.to(device)
    total_loss = 0.0
    correct = 0
    total = 0
    for batch_x, batch_y in dataloader:
        batch_x, batch_y = batch_x.to(device), batch_y.to(device)
        optimizer.zero_grad()
        outputs = model(batch_x)
        loss = criterion(outputs, batch_y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * batch_x.size(0)
        _, predicted = torch.max(outputs, 1)
        correct += (predicted == batch_y).sum().item()
        total += batch_y.size(0)
    return {'loss': total_loss / total, 'accuracy': correct / total}

def evaluate(model, dataloader, criterion, device):
    model.eval()
    model.to(device)
    total_loss = 0.0
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for batch_x, batch_y in dataloader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            total_loss += loss.item() * batch_x.size(0)
            _, predicted = torch.max(outputs, 1)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(batch_y.cpu().numpy())
    total = len(all_labels)
    acc = accuracy_score(all_labels, all_preds)
    prec = precision_score(all_labels, all_preds, average='weighted', zero_division=0)
    rec = recall_score(all_labels, all_preds, average='weighted', zero_division=0)
    f1 = f1_score(all_labels, all_preds, average='weighted', zero_division=0)
    return {'loss': total_loss / total, 'accuracy': acc, 'precision': prec, 'recall': rec, 'f1': f1}

def print_metrics(result, title='Results'):
    print()
    print('=' * 50)
    print('  ' + title)
    print('=' * 50)
    print('  Loss:      {:.4f}'.format(result['loss']))
    print('  Accuracy:  {:.4f} ({:.2f}%)'.format(result['accuracy'], result['accuracy']*100))
    print('  Precision: {:.4f}'.format(result['precision']))
    print('  Recall:    {:.4f}'.format(result['recall']))
    print('  F1 Score:  {:.4f}'.format(result['f1']))
    print('=' * 50)

def save_results(results, filepath):
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print('Results saved to {}'.format(filepath))

def save_model(model, filepath):
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), filepath)
    print('Model saved to {}'.format(filepath))
