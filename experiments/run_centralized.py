"""XFed-IDS: Experiment 1 -- Centralized Baseline"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import torch
import torch.nn as nn
import time
from config import NUM_EPOCHS, BATCH_SIZE, LEARNING_RATE, RESULTS_DIR, MODEL_DIR, RANDOM_SEED
from src.model import IDSModel, count_parameters
from src.dataset import load_cicids2017, IDSDataset
from src.utils import set_seed, get_device, train_one_epoch, evaluate, print_metrics, save_results, save_model
from torch.utils.data import DataLoader

def run_centralized_experiment():
    set_seed(RANDOM_SEED)
    device = get_device()
    print('=' * 60)
    print('  XFed-IDS: Centralized Baseline Experiment')
    print('  (Upper bound -- all data shared, no privacy)')
    print('=' * 60)
    print('\n[DATA] Loading dataset...')
    X_train, X_test, y_train, y_test, feature_names, label_names = load_cicids2017()
    train_dataset = IDSDataset(X_train, y_train)
    test_dataset = IDSDataset(X_test, y_test)
    trainloader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    testloader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)
    input_dim = X_train.shape[1]
    num_classes = len(label_names)
    model = IDSModel(input_dim=input_dim, num_classes=num_classes)
    print('\n[MODEL] Model: IDSModel (MLP)')
    print('   Input:      {} features'.format(input_dim))
    print('   Output:     {} classes'.format(num_classes))
    print('   Parameters: {:,}'.format(count_parameters(model)))
    print('   Device:     {}'.format(device))
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    print('\n[TRAIN] Training for {} epochs...'.format(NUM_EPOCHS))
    print('-' * 50)
    history = {'epoch': [], 'train_loss': [], 'train_acc': [], 'test_acc': [], 'test_f1': []}
    start_time = time.time()
    for epoch in range(1, NUM_EPOCHS + 1):
        train_result = train_one_epoch(model, trainloader, optimizer, criterion, device)
        test_result = evaluate(model, testloader, criterion, device)
        history['epoch'].append(epoch)
        history['train_loss'].append(train_result['loss'])
        history['train_acc'].append(train_result['accuracy'])
        history['test_acc'].append(test_result['accuracy'])
        history['test_f1'].append(test_result['f1'])
        print('  Epoch {:2d}/{} | Train Loss: {:.4f} | Train Acc: {:.4f} | Test Acc: {:.4f} | Test F1: {:.4f}'.format(
            epoch, NUM_EPOCHS, train_result['loss'], train_result['accuracy'], test_result['accuracy'], test_result['f1']))
    elapsed = time.time() - start_time
    final = evaluate(model, testloader, criterion, device)
    print_metrics(final, 'Centralized Baseline -- Final Results')
    print('  Training time: {:.1f}s'.format(elapsed))
    results = {
        'experiment': 'centralized_baseline', 'training_time_seconds': elapsed,
        'final_accuracy': final['accuracy'], 'final_f1': final['f1'],
        'final_precision': final['precision'], 'final_recall': final['recall'],
        'final_loss': final['loss'], 'history': history, 'label_names': label_names,
    }
    save_results(results, RESULTS_DIR / 'centralized_baseline.json')
    save_model(model, MODEL_DIR / 'centralized_baseline.pt')
    print('\n[OK] Centralized baseline experiment complete!')
    print('   Accuracy: {:.2f}%'.format(final['accuracy']*100))
    print('   F1 Score: {:.4f}'.format(final['f1']))

if __name__ == '__main__':
    run_centralized_experiment()
