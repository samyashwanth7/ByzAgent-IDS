"""XFed-IDS: Experiment 3 -- Local-Only Baseline"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import torch
import torch.nn as nn
import time
from config import (NUM_CLIENTS, BATCH_SIZE, LEARNING_RATE, NUM_EPOCHS,
                    RESULTS_DIR, MODEL_DIR, RANDOM_SEED, NON_IID_ALPHA)
from src.model import IDSModel, count_parameters
from src.dataset import (load_cicids2017, partition_data_non_iid, create_dataloaders)
from src.utils import (set_seed, get_device, train_one_epoch, evaluate, print_metrics, save_results)

def run_local_only():
    set_seed(RANDOM_SEED)
    device = get_device()
    print('=' * 60)
    print('  XFed-IDS: Local-Only Baseline Experiment')
    print('  (Each org trains alone -- no collaboration)')
    print('=' * 60)
    print('\nLoading dataset...')
    X_train, X_test, y_train, y_test, feature_names, label_names = load_cicids2017()
    input_dim = X_train.shape[1]
    num_classes = len(label_names)
    print('\nPartitioning data across {} organizations (Non-IID)...'.format(NUM_CLIENTS))
    partitions = partition_data_non_iid(X_train, y_train, num_clients=NUM_CLIENTS, alpha=NON_IID_ALPHA)
    client_loaders = create_dataloaders(partitions, X_test, y_test)
    criterion = nn.CrossEntropyLoss()
    client_results = []
    start_time = time.time()
    for client_id in range(NUM_CLIENTS):
        print('\n--- Training Client {} (independently) ---'.format(client_id))
        model = IDSModel(input_dim=input_dim, num_classes=num_classes)
        optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
        trainloader, testloader = client_loaders[client_id]
        for epoch in range(1, NUM_EPOCHS + 1):
            train_result = train_one_epoch(model, trainloader, optimizer, criterion, device)
            if epoch % 5 == 0 or epoch == 1:
                test_result = evaluate(model, testloader, criterion, device)
                print('  Epoch {:2d}/{} | Train Acc: {:.4f} | Test Acc: {:.4f}'.format(
                    epoch, NUM_EPOCHS, train_result['accuracy'], test_result['accuracy']))
        final = evaluate(model, testloader, criterion, device)
        client_results.append(final)
        print_metrics(final, 'Client {} -- Final Results'.format(client_id))
    elapsed = time.time() - start_time
    avg_acc = sum(r['accuracy'] for r in client_results) / len(client_results)
    avg_f1 = sum(r['f1'] for r in client_results) / len(client_results)
    print('\n' + '=' * 50)
    print('  Local-Only -- Average Results')
    print('=' * 50)
    print('  Avg Accuracy: {:.4f} ({:.2f}%)'.format(avg_acc, avg_acc*100))
    print('  Avg F1 Score: {:.4f}'.format(avg_f1))
    for i, r in enumerate(client_results):
        print('  Client {}: Acc={:.2f}%, F1={:.4f}'.format(i, r['accuracy']*100, r['f1']))
    print('  Training time: {:.1f}s'.format(elapsed))
    print('=' * 50)
    results = {
        'experiment': 'local_only', 'training_time_seconds': elapsed,
        'avg_accuracy': avg_acc, 'avg_f1': avg_f1,
        'client_results': [
            {'client_id': i, 'accuracy': r['accuracy'], 'f1': r['f1'],
             'precision': r['precision'], 'recall': r['recall']}
            for i, r in enumerate(client_results)
        ]
    }
    save_results(results, RESULTS_DIR / 'local_only.json')
    print('\n[OK] Local-only experiment complete!')

if __name__ == '__main__':
    run_local_only()
