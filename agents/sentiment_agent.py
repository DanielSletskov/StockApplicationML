from autogen import ConversableAgent
from .agent_config import get_llm_config

class SentimentAgent:
    def __init__(self):
        self.agent = ConversableAgent(
    name="SentimentEvaluator",
    llm_config=get_llm_config("sentiment"),
    system_message=(
        #PRE OPTIMIZATION
        # "You are a financial sentiment expert. Based on the following stock news headlines,
        # "respond with one word only: POSITIVE, NEUTRAL, or NEGATIVE."
        "You are a stock sentiment analysis expert.\n\n"
        "Your job is to analyze news headlines for a specific stock (e.g., SPY) "
        "and determine the overall sentiment affecting short-term price movement (1–3 days).\n\n"
        "Use the following rules:\n"
        "- Respond with ONLY one word: POSITIVE, NEUTRAL, or NEGATIVE.\n"
        "- Consider earnings, partnerships, analyst upgrades, economic impact, etc.\n"
        "- Ignore news unrelated to the stock.\n"
        "- POSITIVE if most headlines signal price appreciation or investor confidence.\n"
        "- NEGATIVE if news implies losses, uncertainty, or macro drag.\n\n"
        "Examples:\n"
        "Headline: 'SPY surges on strong earnings' → POSITIVE\n"
        "Headline: 'SPY dips slightly amid quiet trading' → NEUTRAL\n"
        "Headline: 'SPY tumbles after Fed rate hike' → NEGATIVE\n\n"
        "Return only POSITIVE, NEUTRAL, or NEGATIVE — no explanations."
    )
)

    def evaluate(self, headlines):
        if not headlines:
            return "NEUTRAL"
        prompt = "\n".join(headlines)
        response = self.agent.generate_reply([{"role": "user", "content": prompt}])
        return response["content"].strip().upper()
