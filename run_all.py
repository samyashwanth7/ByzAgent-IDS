import subprocess
import os

def set_strategy(strategy):
    with open('config.py', 'r') as f:
        content = f.read()
    
    import re
    # Match AGG_STRATEGY = ...
    content = re.sub(r'AGG_STRATEGY\s*=\s*\".*?\"', f'AGG_STRATEGY = \"{strategy}\"', content)
    
    with open('config.py', 'w') as f:
        f.write(content)
    print(f\"\n{'='*50}\n Starting run for strategy: {strategy}\n{'='*50}\")

strategies = ['fedavg', 'krum', 'byzagent']

for strat in strategies:
    set_strategy(strat)
    # Run the experiment
    subprocess.run(['python', 'experiments/run_federated.py'])

print(\"All strategies completed!\")
