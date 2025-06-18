import json
import os
from datetime import datetime

class TradeLogger:
    def __init__(self, log_path="logs/trade_log.json"):
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def log_trade(self, trade_data):
        trade_data["timestamp"] = datetime.now().isoformat()
        with open(self.log_path, "a") as f:
            f.write(json.dumps(trade_data) + "\\n")

    def load_logs(self, limit=100):
        if not os.path.exists(self.log_path):
            return []
        with open(self.log_path, "r") as f:
            lines = f.readlines()[-limit:]
            return [json.loads(line) for line in lines if line.strip()]