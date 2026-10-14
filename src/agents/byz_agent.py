import os
import json
from typing import Dict
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

load_dotenv()

class ByzAgentTrustArbiter:
    def __init__(self):
        self.llm = ChatGroq(
            model='openai/gpt-oss-120b',
            temperature=0.0,
            model_kwargs={'response_format': {'type': 'json_object'}}
        )
        
        self.prompt = PromptTemplate(
            input_variables=['round_num', 'stats_json', 'history_json'],
            template='''You are ByzAgent, an AI Security Arbiter overseeing a Federated Learning Intrusion Detection System.
It is currently Round {round_num} of federated training.

Current Round Behavioral Statistics:
{stats_json}

Recent Historical Trajectory (Last 3 Rounds):
{history_json}

Context for the metrics:
- 'update_norm': The size of the client's weight update. Malicious clients often have unusually small or large norms.
- 'cos_sim_peer_mean': The cosine similarity (1.0 to -1.0) of this client's update compared to the average of all clients. A drop indicates the client is diverging from the consensus.
- 'local_loss': The client's local training loss. A high loss compared to peers indicates they are struggling to fit their local data (classic symptom of label-flipping poisoning).
- 'val_accuracy': The client's model evaluated on a clean held-out server validation dataset. A sharp drop indicates poisoning.

Temporal reasoning instruction:
Look at the TREND across recent rounds. A client whose loss steadily rises or whose cos_sim / val_accuracy steadily falls over rounds is likely being gradually poisoned, even if their current metrics have not fully collapsed yet.

Your task is to assign a trust decision to EACH client based on these statistics and their historical trajectory.
Decisions:
- "trust": Client appears completely normal. Include their update.
- "downweight": Client is slightly anomalous or showing early signs of divergence. Include their update but reduce its weight.
- "quarantine": Client is clearly poisoned (e.g., high loss, low val_accuracy, declining peer similarity). Reject their update entirely.

You MUST output valid JSON exactly matching this schema:
{{
  "decisions": [
    {{
      "client_id": "client_X",
      "decision": "trust|downweight|quarantine",
      "explanation": "1 concise sentence explicitly referencing the metrics that led to this decision."
    }}
  ]
}}
'''
        )
        self.chain = self.prompt | self.llm

    def evaluate_clients(self, round_num: int, round_stats: Dict, history: Dict = None) -> Dict:
        stats_str = json.dumps(round_stats, indent=2)
        recent_history = {}
        if history:
            for cid in round_stats.keys():
                client_hist = history.get(cid, [])
                recent_history[cid] = client_hist[-3:] if len(client_hist) > 0 else []
        history_str = json.dumps(recent_history, indent=2)

        print(f"  [ByzAgent] Thinking... analyzing stats and history for {len(round_stats)} clients.")
        
        try:
            response = self.chain.invoke({
                'round_num': round_num, 
                'stats_json': stats_str,
                'history_json': history_str
            })
            result = json.loads(response.content)
            
            # Validator: keep only valid decisions for known clients
            valid_decisions = {}
            for item in result.get('decisions', []):
                cid = item.get('client_id')
                dec = str(item.get('decision', '')).lower().strip()
                exp = str(item.get('explanation', 'Validated decision.'))
                if cid in round_stats and dec in {'trust', 'downweight', 'quarantine'}:
                    valid_decisions[cid] = {'client_id': cid, 'decision': dec, 'explanation': exp}
            
            # Any client missing from output gets 'downweight'
            final_decisions = []
            for cid in round_stats.keys():
                if cid in valid_decisions:
                    final_decisions.append(valid_decisions[cid])
                else:
                    final_decisions.append({
                        'client_id': cid,
                        'decision': 'downweight',
                        'explanation': 'Fallback: omitted by agent decision output.'
                    })
            return {'decisions': final_decisions}

        except Exception as e:
            print(f"  [ERROR] ByzAgent failed to parse JSON or call API: {e}")
            print("  [ERROR] Fail-safe fallback: assigning 'downweight' to all clients.")
            return {
                'decisions': [
                    {'client_id': cid, 'decision': 'downweight', 'explanation': 'Fallback: agent unavailable'} 
                    for cid in round_stats.keys()
                ]
            }
