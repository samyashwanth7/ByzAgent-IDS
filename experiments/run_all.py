"""XFed-IDS: Run ALL experiments in sequence."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from run_centralized import run_centralized_experiment
from run_federated import run_federated_experiment
from run_local_only import run_local_only

if __name__ == '__main__':
    print('\n' + '#' * 60)
    print('  EXPERIMENT 1: Centralized Baseline')
    print('#' * 60)
    run_centralized_experiment()
    print('\n' + '#' * 60)
    print('  EXPERIMENT 2: Federated IID (FedAvg)')
    print('#' * 60)
    run_federated_experiment(non_iid=False, strategy_name='fedavg')
    print('\n' + '#' * 60)
    print('  EXPERIMENT 3: Federated Non-IID (FedAvg)')
    print('#' * 60)
    run_federated_experiment(non_iid=True, strategy_name='fedavg')
    print('\n' + '#' * 60)
    print('  EXPERIMENT 4: Federated Non-IID (FedProx)')
    print('#' * 60)
    run_federated_experiment(non_iid=True, strategy_name='fedprox')
    print('\n' + '#' * 60)
    print('  EXPERIMENT 5: Local-Only Baseline')
    print('#' * 60)
    run_local_only()
    print('\n\n[OK] ALL EXPERIMENTS COMPLETE!')
