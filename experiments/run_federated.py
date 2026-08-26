"""XFed-IDS: Experiment 2 -- Federated Training (Manual Simulation)"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import argparse
import config
import torch
import torch.nn as nn
import numpy as np
import time
import copy
import json
from config import (NUM_ROUNDS, NUM_CLIENTS, BATCH_SIZE, LEARNING_RATE,
                    LOCAL_EPOCHS, NON_IID_ALPHA, RESULTS_DIR, MODEL_DIR,
                    RANDOM_SEED, FEDPROX_MU, DP_ENABLED, DP_EPSILON,
                    DP_DELTA, DP_CLIP_NORM)
import math
from src.monitoring.client_stats import ByzAgentMonitor
from src.agents.byz_agent import ByzAgentTrustArbiter
from src.aggregation.robust_baselines import krum_aggregate, trimmed_mean_aggregate
from src.model import IDSModel, count_parameters
from src.dataset import (load_cicids2017, partition_data_iid, partition_data_non_iid, create_dataloaders)
from src.utils import (set_seed, get_device, train_one_epoch, evaluate, print_metrics, save_results, save_model)

def fedavg_aggregate(global_model, client_models, client_sizes, use_dp=DP_ENABLED):
    old_dict = {k: v.clone().float() for k, v in global_model.state_dict().items()}
    new_dict = global_model.state_dict()
    total_size = sum(client_sizes)

    for key in new_dict.keys():
        new_dict[key] = torch.zeros_like(new_dict[key], dtype=torch.float32)
        for i, client_model in enumerate(client_models):
            weight = client_sizes[i] / total_size
            new_dict[key] += weight * client_model.state_dict()[key].float()

    # Apply Differential Privacy: clip and noise the UPDATE (delta), not absolute weights
    if use_dp:
        sigma = DP_CLIP_NORM * math.sqrt(2.0 * math.log(1.25 / DP_DELTA)) / DP_EPSILON
        for key in new_dict.keys():
            delta = new_dict[key] - old_dict[key]
            # Clip the update
            delta_norm = torch.norm(delta)
            clip_factor = min(1.0, DP_CLIP_NORM / (delta_norm.item() + 1e-8))
            delta = delta * clip_factor
            # Add calibrated Gaussian noise
            noise = torch.normal(mean=0.0, std=sigma / len(client_models), size=delta.shape)
            new_dict[key] = old_dict[key] + delta + noise
        print('    [DP] Noise on updates (eps={}, clip={})'.format(DP_EPSILON, DP_CLIP_NORM))

    global_model.load_state_dict(new_dict)
    return global_model

def train_local_fedprox(model, global_model, dataloader, optimizer, criterion, device, mu=0.01):
    model.train()
    model.to(device)
    global_model.to(device)
    total_loss = 0.0
    correct = 0
    total = 0
    global_params = list(global_model.parameters())
    for batch_x, batch_y in dataloader:
        batch_x, batch_y = batch_x.to(device), batch_y.to(device)
        optimizer.zero_grad()
        outputs = model(batch_x)
        loss = criterion(outputs, batch_y)
        prox_term = 0.0
        for local_param, global_param in zip(model.parameters(), global_params):
            prox_term += ((local_param - global_param.detach()) ** 2).sum()
        loss += (mu / 2) * prox_term
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * batch_x.size(0)
        _, predicted = torch.max(outputs, 1)
        correct += (predicted == batch_y).sum().item()
        total += batch_y.size(0)
    return {'loss': total_loss / total, 'accuracy': correct / total}

def run_federated_experiment(non_iid=False, strategy_name='fedavg', alpha=NON_IID_ALPHA, num_rounds=NUM_ROUNDS):
    set_seed(RANDOM_SEED)
    device = get_device()
    partition_type = 'Non-IID' if non_iid else 'IID'
    print('=' * 60)
    print('  XFed-IDS: Federated Training Experiment')
    print('  Partition: {} | Strategy: {}'.format(partition_type, strategy_name))
    print('=' * 60)
    print('\nLoading dataset...')
    X_train, X_test, y_train, y_test, feature_names, label_names = load_cicids2017()
    input_dim = X_train.shape[1]
    num_classes = len(label_names)
    print('\nPartitioning data across {} organizations ({})...'.format(NUM_CLIENTS, partition_type))
    if non_iid:
        partitions = partition_data_non_iid(X_train, y_train, num_clients=NUM_CLIENTS, alpha=alpha)
    else:
        partitions = partition_data_iid(X_train, y_train, num_clients=NUM_CLIENTS)
    client_loaders = create_dataloaders(partitions, X_test, y_test)
    client_sizes = [len(p['y']) for p in partitions]
    global_model = IDSModel(input_dim=input_dim, num_classes=num_classes)
    print('\nModel: IDSModel (MLP)')
    print('  Parameters: {:,}'.format(count_parameters(global_model)))
    print('  Rounds:     {}'.format(num_rounds))
    print('  Clients:    {}'.format(NUM_CLIENTS))
    print('  Strategy:   {}'.format(strategy_name))
    criterion = nn.CrossEntropyLoss()
    _, testloader = client_loaders[0]
    monitor = ByzAgentMonitor(config.RESULTS_DIR / "byzagent_history.json")
    arbiter = ByzAgentTrustArbiter()
    all_decisions = []
    history = {'round': [], 'global_loss': [], 'global_acc': [], 'global_f1': [], 'global_precision': [], 'global_recall': []}
    print('\nStarting Federated Learning...')
    print('-' * 70)
    start_time = time.time()
    for round_num in range(1, num_rounds + 1):
        client_models = []
        client_losses = []
        client_val_accs = []
        for client_id in range(NUM_CLIENTS):
            local_model = IDSModel(input_dim=input_dim, num_classes=num_classes)
            local_model.load_state_dict(copy.deepcopy(global_model.state_dict()))
            trainloader, _ = client_loaders[client_id]
            
            # Apply Poisoning (ByzAgent Phase 0)
            if config.POISON_ENABLED and client_id in config.ATTACKER_CLIENTS:
                from src.attacks.label_flip import apply_label_flip
                trainloader = apply_label_flip(
                    trainloader, 
                    round_num, 
                    mode=config.POISON_MODE, 
                    sudden_frac=config.POISON_FRACTION_SUDDEN, 
                    gradual_step=config.POISON_FRACTION_GRADUAL_STEP,
                    num_classes=num_classes
                )
                
            optimizer = torch.optim.Adam(local_model.parameters(), lr=config.LEARNING_RATE)
            final_loss = 0.0
            for epoch in range(config.LOCAL_EPOCHS):
                if strategy_name == 'fedprox':
                    res = train_local_fedprox(local_model, global_model, trainloader, optimizer, criterion, device, mu=config.FEDPROX_MU)
                    final_loss = res['loss'] if isinstance(res, dict) else res
                else:
                    res = train_one_epoch(local_model, trainloader, optimizer, criterion, device)
                    final_loss = res['loss'] if isinstance(res, dict) else res
            
            client_models.append(local_model)
            client_losses.append(final_loss)
            
            # Validation accuracy on clean test set
            val_res = evaluate(local_model, testloader, criterion, device)
            client_val_accs.append(val_res['accuracy'])
        
        # ByzAgent Phase 1: Compute Stats
        round_stats = monitor.compute_round_stats(
            round_num=round_num,
            global_model=global_model,
            client_models=client_models,
            local_losses=client_losses,
            val_accuracies=client_val_accs
        )
        # Print stats for verification
        print(f"  [ByzAgent] Stats for Round {round_num}:")
        for cid, stats in round_stats.items():
            print(f"    {cid}: norm={stats['update_norm']:.4f}, cos_peer={stats['cos_sim_peer_mean']:.4f}, loss={stats['local_loss']:.4f}, val_acc={stats['val_accuracy']:.4f}")
            
        if config.AGG_STRATEGY == 'byzagent':
            decisions_json = arbiter.evaluate_clients(round_num, round_stats)
            decisions_json['round'] = round_num
            all_decisions.append(decisions_json)
            with open(config.RESULTS_DIR / 'byzagent_decisions.json', 'w') as df:
                json.dump(all_decisions, df, indent=2)
                
            trusted_models = []
            trusted_sizes = []
            for d in decisions_json.get('decisions', []):
                try:
                    c_idx = int(d['client_id'].split('_')[1])
                except Exception:
                    continue
                decision = d.get('decision', 'trust').lower()
                print(f"    -> {d['client_id']}: {decision.upper()} | {d.get('explanation', '')}")
                
                if decision == 'trust':
                    trusted_models.append(client_models[c_idx])
                    trusted_sizes.append(client_sizes[c_idx])
                elif decision == 'downweight':
                    trusted_models.append(client_models[c_idx])
                    trusted_sizes.append(client_sizes[c_idx] * 0.3)
                elif decision == 'quarantine':
                    pass # completely exclude
            
            if len(trusted_models) > 0:
                global_model = fedavg_aggregate(global_model, trusted_models, trusted_sizes)
            else:
                print("  [ERROR] All clients quarantined! Skipping update this round.")
        elif config.AGG_STRATEGY == 'krum':
            global_model, best_idx = krum_aggregate(global_model, client_models, f=len(config.ATTACKER_CLIENTS) if config.POISON_ENABLED else 1)
            print(f"  [Aggregation] Krum selected client_{best_idx}")
        elif config.AGG_STRATEGY == 'trimmed_mean':
            global_model = trimmed_mean_aggregate(global_model, client_models, trim_count=1)
            print("  [Aggregation] Trimmed-Mean applied")
        else:
            global_model = fedavg_aggregate(global_model, client_models, client_sizes)
        test_result = evaluate(global_model, testloader, criterion, device)
        history['round'].append(round_num)
        history['global_loss'].append(test_result['loss'])
        history['global_acc'].append(test_result['accuracy'])
        history['global_f1'].append(test_result['f1'])
        history['global_precision'].append(test_result['precision'])
        history['global_recall'].append(test_result['recall'])
        print('  Round {:2d}/{} | Loss: {:.4f} | Acc: {:.4f} | F1: {:.4f}'.format(
            round_num, num_rounds, test_result['loss'], test_result['accuracy'], test_result['f1']))
    elapsed = time.time() - start_time
    final_result = evaluate(global_model, testloader, criterion, device)
    print_metrics(final_result, 'Federated {} {} -- Final Results'.format(partition_type, strategy_name))
    print('  Training time: {:.1f}s'.format(elapsed))
    results = {
        'experiment': 'federated_{}_{}'.format(partition_type.lower(), strategy_name),
        'partition_type': partition_type, 'strategy': strategy_name,
        'num_rounds': num_rounds, 'num_clients': NUM_CLIENTS,
        'non_iid_alpha': alpha if non_iid else 'N/A',
        'training_time_seconds': elapsed,
        'final_accuracy': final_result['accuracy'], 'final_f1': final_result['f1'],
        'final_precision': final_result['precision'], 'final_recall': final_result['recall'],
        'final_loss': final_result['loss'], 'history': history, 'label_names': label_names,
    }
    result_filename = 'federated_{}_{}.json'.format(partition_type.lower(), strategy_name)
    save_results(results, RESULTS_DIR / result_filename)
    model_filename = 'federated_{}_{}.pt'.format(partition_type.lower(), strategy_name)
    save_model(global_model, MODEL_DIR / model_filename)
    print('\n[OK] Federated experiment complete!')
    print('   Accuracy: {:.2f}%'.format(final_result['accuracy']*100))
    print('   F1 Score: {:.4f}'.format(final_result['f1']))
    return global_model, final_result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='XFed-IDS Federated Training')
    parser.add_argument('--non-iid', action='store_true', help='Use non-IID partitioning')
    parser.add_argument('--strategy', choices=['fedavg', 'fedprox'], default='fedavg')
    parser.add_argument('--alpha', type=float, default=NON_IID_ALPHA)
    parser.add_argument('--rounds', type=int, default=NUM_ROUNDS)
    args = parser.parse_args()
    run_federated_experiment(non_iid=args.non_iid, strategy_name=args.strategy, alpha=args.alpha, num_rounds=args.rounds)
