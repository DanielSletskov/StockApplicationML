from autogen import ConversableAgent
from agents.agent_config import get_llm_config
import json
from datetime import datetime
import os

class RiskAgent:
    def __init__(self, trust_level=1.0, log_path="logs/risk_log.json"):
        self.trust_level = trust_level
        self.log_path = log_path
        self.agent = ConversableAgent(
            name="RiskManager",
            llm_config=get_llm_config("risk"),
            system_message=self._generate_system_message()
        )

    def _generate_system_message(self):
        return (
            f"You are a portfolio risk manager.\n\n"
            f"TRUST LEVEL: {self.trust_level:.2f}\n"
            f"If trust level < 0.8, classify more conditions as MEDIUM or HIGH risk.\n\n"
            "Assess whether today's market conditions are safe for trading SPY.\n\n"
            "Use the current date to decide the risk level based on:\n"
            "- Overall volatility (e.g., VIX spikes, earnings week)\n"
            "- Market instability (e.g., crises, surprise data)\n"
            "- Calendar timing (e.g., Fridays, end-of-quarter, holidays)\n\n"
            "Return one word only: LOW, MEDIUM, or HIGH.\n\n"
            "Respond with LOW, MEDIUM, or HIGH only. No explanation."
        )

    def log_evaluation(self, prompt, result):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "input": prompt,
            "result": result,
            "trust_level": self.trust_level
        }
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def evaluate(self, current_date):
        prompt = f"Today is {current_date.strftime('%Y-%m-%d')}. What is the trading risk today?"
        response = self.agent.generate_reply([{"role": "user", "content": prompt}])
        if isinstance(response, dict) and "content" in response:
            result = response["content"].strip().upper()
        else:
            print(f"[ERROR] Unexpected response format: {response}")
            result = "NEUTRAL"

        self.log_evaluation(prompt, result)
        return result

    def adjust_config(self, trust_level=None):
        if trust_level is not None:
            self.trust_level = trust_level
            self.agent.system_message = self._generate_system_message()
        return {"trust_level": self.trust_level}
