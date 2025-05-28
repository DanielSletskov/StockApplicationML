import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_llm_config(agent_type="default"):
    base_config = {
        "temperature": 0.2,
        "config_list": [
            {
                "model": "gpt-4",
                "api_key": OPENAI_API_KEY
            }
        ]
    }

    if agent_type == "sentiment":
        base_config["temperature"] = 0.0
    elif agent_type == "macro":
        base_config["temperature"] = 0.0
    elif agent_type == "risk":
        base_config["temperature"] = 0.0

    return base_config
