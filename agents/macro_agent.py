from autogen import ConversableAgent
from agents.agent_config import get_llm_config
import json
from datetime import datetime
import os

class MacroNewsAgent:
    def __init__(self, trust_level=1.0, log_path="logs/macro_log.json"):
        self.trust_level = trust_level
        self.log_path = log_path
        self.agent = ConversableAgent(
            name="MacroNewsAnalyst",
            llm_config=get_llm_config("macro"),
            system_message=self._generate_system_message()
        )

    def _generate_system_message(self):
        return (
            f"You are a macroeconomic risk analyst.\n\n"
            f"TRUST LEVEL: {self.trust_level:.2f}\n"
            f"If trust level < 0.8, lean toward NEGATIVE evaluations.\n\n"
            "Analyze news headlines for broad economic or geopolitical concerns "
            "that may affect all stocks, including SPY.\n\n"
            "Use the following criteria:\n"
            "- Return one word only: POSITIVE, NEUTRAL, or NEGATIVE.\n"
            "- POSITIVE: News on interest rate cuts, economic growth, peace deals, low inflation.\n"
            "- NEGATIVE: News on inflation, rate hikes, war, economic contraction, or mass layoffs.\n"
            "- NEUTRAL: Mixed news or no significant macro impact.\n\n"
            "Do not explain your reasoning. Just return POSITIVE, NEUTRAL, or NEGATIVE."
        )

    def log_evaluation(self, input_text, result):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "input": input_text,
            "result": result,
            "trust_level": self.trust_level
        }
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def evaluate(self, headlines):
        if not headlines:
            result = "NEUTRAL"
        else:
            prompt = "\n".join(headlines)
            response = self.agent.generate_reply([{"role": "user", "content": prompt}])
            if isinstance(response, dict) and "content" in response:
                result = response["content"].strip().upper()
            else:
                print(f"[ERROR] Unexpected response format: {response}")
                result = "NEUTRAL"

        self.log_evaluation("\n".join(headlines), result)
        return result

    def adjust_config(self, trust_level=None):
        if trust_level is not None:
            self.trust_level = trust_level
            self.agent.system_message = self._generate_system_message()
        return {"trust_level": self.trust_level}