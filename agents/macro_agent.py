from autogen import ConversableAgent
from .agent_config import get_llm_config

class MacroNewsAgent:
    def __init__(self):
        self.agent = ConversableAgent(
    name="MacroNewsAnalyst",
    llm_config=get_llm_config("macro"),
    system_message=(
        #pre OPTIMIZATION
        #"You are a macroeconomic news analyst. Examine these headlines for inflation, interest rate, "
        #"or geopolitical risks. Respond with one word only: POSITIVE, NEUTRAL, or NEGATIVE."
        

        "You are a macroeconomic risk analyst. Analyze news headlines for broad economic or geopolitical concerns "
        "that may affect all stocks, including SPY.\n\n"
        "Use the following criteria:\n"
        "- Return one word only: POSITIVE, NEUTRAL, or NEGATIVE.\n"
        "- POSITIVE: News on interest rate cuts, economic growth, peace deals, low inflation.\n"
        "- NEGATIVE: News on inflation, rate hikes, war, economic contraction, or mass layoffs.\n"
        "- NEUTRAL: Mixed news or no significant macro impact.\n\n"
        "Examples:\n"
        "'Fed signals pause in rate hikes' → POSITIVE\n"
        "'US GDP contracts 0.5%' → NEGATIVE\n"
        "'Unemployment steady at 3.8%' → NEUTRAL\n\n"
        "Do not explain your reasoning. Just return POSITIVE, NEUTRAL, or NEGATIVE."
    )
)

    def evaluate(self, headlines):
        if not headlines:
            return "NEUTRAL"
        prompt = "\n".join(headlines)
        response = self.agent.generate_reply([{"role": "user", "content": prompt}])
        return response["content"].strip().upper()
