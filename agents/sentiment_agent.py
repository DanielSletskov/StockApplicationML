from autogen import ConversableAgent
from agents.agent_config import get_llm_config
import json
from datetime import datetime
import os

class SentimentAgent:
    def __init__(self, trust_level=1.0, log_path="logs/sentiment_log.json"):
        self.trust_level = trust_level
        self.log_path = log_path
        self.agent = ConversableAgent(
            name="SentimentEvaluator",
            llm_config=get_llm_config("sentiment"),
            system_message=self._generate_system_message()
        )

    def _generate_system_message(self):
        return (
            f"You are a stock sentiment analysis expert.\n\n"
            f"TRUST LEVEL: {self.trust_level:.2f}\n"
            f"If trust level < 0.8, be more conservative in classifying news as POSITIVE.\n\n"
            "Your job is to analyze news headlines for a specific stock (e.g., SPY) "
            "and determine the overall sentiment affecting short-term price movement (1–3 days).\n\n"
            "Use the following rules:\n"
            "- Respond with ONLY one word: POSITIVE, NEUTRAL, or NEGATIVE.\n"
            "- Consider earnings, partnerships, analyst upgrades, economic impact, etc.\n"
            "- Ignore news unrelated to the stock.\n"
            "- POSITIVE if most headlines signal price appreciation or investor confidence.\n"
            "- NEGATIVE if news implies losses, uncertainty, or macro drag.\n\n"
            "Return only POSITIVE, NEUTRAL, or NEGATIVE — no explanations."
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