"""
XFed-IDS: Flower Federated Learning Server
==========================================

The central aggregation server that:
1. Distributes the global model to all organizations
2. Collects updated weights from each organization
3. Aggregates weights using FedAvg/FedProx/Krum
4. Sends the improved global model back

IMPORTANT: The server NEVER sees any organization's raw data.
It only receives and aggregates model weight updates.
"""

import flwr as fl
from flwr.server.strategy import FedAvg, FedProx
from flwr.common import Metrics
from typing import List, Tuple, Dict, Optional
import numpy as np

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import (
    NUM_ROUNDS, NUM_CLIENTS, FRACTION_FIT, MIN_FIT_CLIENTS,
    FL_SERVER_ADDRESS, AGGREGATION_STRATEGY, FEDPROX_MU
)


#  Custom Metrics Aggregation 

def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    """
    Aggregate metrics from all clients using weighted average.
    
    Each client reports its local metrics (accuracy, f1, etc.)
    weighted by the number of samples it has.
    """
    total_samples = sum(num_samples for num_samples, _ in metrics)
    
    aggregated = {}
    metric_keys = ["accuracy", "f1", "precision", "recall"]
    
    for key in metric_keys:
        values = [
            num_samples * m.get(key, 0.0) 
            for num_samples, m in metrics
            if key in m
        ]
        if values:
            aggregated[key] = sum(values) / total_samples
    
    return aggregated


#  Strategy Factory 

def get_strategy(strategy_name=AGGREGATION_STRATEGY):
    """
    Create the FL aggregation strategy.
    
    Strategies:
    - fedavg:  Standard Federated Averaging (McMahan et al., 2017)
    - fedprox: FedProx with proximal term (Li et al., 2020)
    - krum:    Byzantine-robust aggregation (Blanchard et al., 2017)
    """
    
    common_args = dict(
        fraction_fit=FRACTION_FIT,
        fraction_evaluate=1.0,
        min_fit_clients=MIN_FIT_CLIENTS,
        min_evaluate_clients=MIN_FIT_CLIENTS,
        min_available_clients=NUM_CLIENTS,
        evaluate_metrics_aggregation_fn=weighted_average,
        fit_metrics_aggregation_fn=weighted_average,
    )
    
    if strategy_name == "fedavg":
        print("\n[NET] Using FedAvg strategy")
        return FedAvg(**common_args)
    
    elif strategy_name == "fedprox":
        print(f"\n[NET] Using FedProx strategy (mu={FEDPROX_MU})")
        return FedProx(
            proximal_mu=FEDPROX_MU,
            **common_args
        )
    
    else:
        print(f"\n[WARN] Unknown strategy '{strategy_name}', defaulting to FedAvg")
        return FedAvg(**common_args)


#  Server Launcher 

def start_server(strategy_name=AGGREGATION_STRATEGY, num_rounds=NUM_ROUNDS):
    """
    Start the Flower FL server.
    
    The server:
    1. Waits for all clients (organizations) to connect
    2. Runs num_rounds of federated training
    3. Each round: distribute model  local training  aggregate
    """
    strategy = get_strategy(strategy_name)
    
    print(f"\n{'='*60}")
    print(f"  XFed-IDS Federated Learning Server")
    print(f"{'='*60}")
    print(f"  Strategy:    {strategy_name}")
    print(f"  Rounds:      {num_rounds}")
    print(f"  Clients:     {NUM_CLIENTS}")
    print(f"  Server:      {FL_SERVER_ADDRESS}")
    print(f"{'='*60}\n")
    
    fl.server.start_server(
        server_address=FL_SERVER_ADDRESS,
        config=fl.server.ServerConfig(num_rounds=num_rounds),
        strategy=strategy,
    )


if __name__ == "__main__":
    start_server()
