import os
import json
from autogen import ConversableAgent
from agents.agent_config import get_llm_config

class MetaEvaluatorAgent:
    def __init__(self, log_paths=None):
        self.log_paths = log_paths or {
            "macro": "logs/macro_log.json",
            "sentiment": "logs/sentiment_log.json",
            "risk": "logs/risk_log.json",
            "trade": "logs/trade_log.json"
        }
        self.agent = ConversableAgent(
            name="MetaEvaluator",
            llm_config=get_llm_config("default"),
            system_message=(
                "You are a meta-analysis agent that reviews past decisions made by other AI agents in a trading system.\n"
                "You are given logs from agents that analyze sentiment, macroeconomic conditions, and risk.\n"
                "You also see the trade outcomes.\n\n"
                "Your job is to determine if any agent consistently gives misleading results and should have its trust level adjusted.\n"
                "Return recommendations like:\n"
                "'Set sentiment trust_level to 0.6'\n"
                "'Keep macro trust_level at current level'\n"
                "'Increase risk trust_level to 1.2'\n"
                "Provide one line per agent. No explanations."
            )
        )

    def _load_recent_logs(self, path, limit=10):
        if not os.path.exists(path):
            return []
        with open(path, "r") as f:
            lines = f.readlines()[-limit:]
            return [json.loads(line) for line in lines if line.strip()]

    def evaluate_trust(self):
        summaries = []
        for name, path in self.log_paths.items():
            logs = self._load_recent_logs(path)
            summaries.append(f"=== {name.upper()} AGENT LOG ===")
            for entry in logs:
                if name == "trade":
                    summaries.append(
                        f"{entry['timestamp']} | Result: {entry.get('outcome')} | Inputs: "
                        f"Sentiment={entry.get('sentiment')} Macro={entry.get('macro')} Risk={entry.get('risk')}"
                    )
                else:
                    input_preview = entry["input"].replace("\n", " ")[:80]
                    summaries.append(f"{entry['timestamp']} | {entry['result']} | {input_preview}...")

        prompt = "\n".join(summaries)
        response = self.agent.generate_reply([{"role": "user", "content": prompt}])
        if isinstance(response, dict) and "content" in response:
            return response["content"].strip()
        else:
            print(f"[ERROR] Unexpected response format: {response}")
            return "No recommendations"