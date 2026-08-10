"""
XFed-IDS: Flower Federated Learning Client
==========================================

Each client represents one organization (hospital, bank, university)
training its local IDS model on its own network traffic data.

The client:
1. Receives the global model from the server
2. Trains locally on its private network data
3. Sends only the updated model weights back (NOT the data)
"""

import flwr as fl
import torch
import torch.nn as nn
from collections import OrderedDict

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import LEARNING_RATE, LOCAL_EPOCHS, BATCH_SIZE
from src.model import IDSModel
from src.utils import train_one_epoch, evaluate, get_device


class IDSFlowerClient(fl.client.NumPyClient):
    """
    Flower client for federated IDS training.
    
    Each instance represents one organization's local training.
    The organization's network traffic data NEVER leaves this client.
    Only model weight updates are communicated to the server.
    """
    
    def __init__(self, model, trainloader, testloader, client_id="unknown"):
        self.model = model
        self.trainloader = trainloader
        self.testloader = testloader
        self.client_id = client_id
        self.device = get_device()
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.Adam(
            self.model.parameters(), lr=LEARNING_RATE
        )
    
    def get_parameters(self, config):
        """Return model parameters as NumPy arrays to the server."""
        return self.model.get_parameters()
    
    def set_parameters(self, parameters):
        """Receive and set model parameters from the server."""
        self.model.set_parameters(parameters)
    
    def fit(self, parameters, config):
        """
        Train the model locally on this organization's data.
        
        This is where the LOCAL training happens:
        1. Receive global model weights from server
        2. Train on LOCAL data for LOCAL_EPOCHS
        3. Return updated weights (NOT the data!)
        """
        self.set_parameters(parameters)
        
        # Train locally
        for epoch in range(LOCAL_EPOCHS):
            result = train_one_epoch(
                self.model, self.trainloader, 
                self.optimizer, self.criterion, self.device
            )
        
        print(f"  [Client {self.client_id}] Local training: "
              f"loss={result['loss']:.4f}, acc={result['accuracy']:.4f}")
        
        return (
            self.get_parameters(config={}),
            len(self.trainloader.dataset),
            {"loss": result["loss"], "accuracy": result["accuracy"]}
        )
    
    def evaluate(self, parameters, config):
        """
        Evaluate the global model on this organization's local test data.
        
        This tells us: how well does the GLOBAL model work
        on THIS organization's specific network traffic?
        """
        self.set_parameters(parameters)
        
        result = evaluate(
            self.model, self.testloader, 
            self.criterion, self.device
        )
        
        print(f"  [Client {self.client_id}] Evaluation: "
              f"loss={result['loss']:.4f}, acc={result['accuracy']:.4f}, "
              f"f1={result['f1']:.4f}")
        
        return (
            result["loss"],
            len(self.testloader.dataset),
            {
                "accuracy": result["accuracy"],
                "f1": result["f1"],
                "precision": result["precision"],
                "recall": result["recall"],
            }
        )


def create_client(model, trainloader, testloader, client_id):
    """Factory function to create a Flower client."""
    return IDSFlowerClient(
        model=model,
        trainloader=trainloader,
        testloader=testloader,
        client_id=client_id
    ).to_client()
