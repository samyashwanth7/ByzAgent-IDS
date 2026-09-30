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
            input_variables=['round_num', 'stats_json'],
            template='''You are ByzAgent, an AI Security Arbiter overseeing a Federated Learning Intrusion Detection System.
It is currently Round {round_num} of federated training.
Review the following behavioral statistics extracted from each client's model update this round:

{stats_json}

Context for the metrics:
- 'update_norm': The size of the client's weight update. Malicious clients often have unusually small or large norms.
- 'cos_sim_peer_mean': The cosine similarity (1.0 to -1.0) of this client's update compared to the average of all clients. A drop indicates the client is diverging from the consensus.
- 'local_loss': The client's local training loss. A high loss compared to peers indicates they are struggling to fit their local data (classic symptom of label-flipping poisoning).
- 'val_accuracy': The client's model evaluated on a clean held-out server dataset. A sharp drop indicates poisoning.

Your task is to assign a trust decision to EACH client based on these statistics.
Decisions:
- "trust": Client appears completely normal. Include their update.
- "downweight": Client is slightly anomalous. Include their update but reduce its weight.
- "quarantine": Client is clearly poisoned (e.g., high loss, low val_accuracy, low peer similarity). Reject their update entirely.

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

    def evaluate_clients(self, round_num: int, round_stats: Dict) -> Dict:
        stats_str = json.dumps(round_stats, indent=2)
        print(f"  [ByzAgent] Thinking... analyzing stats for {len(round_stats)} clients.")
        
        try:
            response = self.chain.invoke({
                'round_num': round_num, 
                'stats_json': stats_str
            })
            result = json.loads(response.content)
            return result
        except Exception as e:
            print(f"  [ERROR] ByzAgent failed to parse JSON or call API: {e}")
            print("  [ERROR] Defaulting to 'trust' for all clients as fallback.")
            return {
                'decisions': [
                    {'client_id': cid, 'decision': 'trust', 'explanation': 'Fallback due to API error.'} 
                    for cid in round_stats.keys()
                ]
            }
