from autogen import ConversableAgent
from .agent_config import get_llm_config

class RiskAgent:
    def __init__(self):
        self.agent = ConversableAgent(
    name="RiskManager",
    llm_config=get_llm_config("risk"),
    system_message=(
        #PRE OPTIMIZATION
        #"You are a portfolio risk expert. Given today's market context, respond with one word only "
        #"about trading risk: LOW, MEDIUM, or HIGH."

        "You are a portfolio risk manager. Assess whether today's market conditions are safe for trading SPY.\n\n"
        "You are given the current date, and must decide the risk level based on:\n"
        "- Overall volatility (e.g., VIX spikes, earnings week)\n"
        "- Market instability (e.g., crises, surprise data)\n"
        "- Calendar timing (e.g., Fridays, end-of-quarter, holidays)\n\n"
        "Return one word only: LOW, MEDIUM, or HIGH.\n\n"
        "Examples:\n"
        "'Today is 2024-07-03, one day before a holiday' → MEDIUM\n"
        "'Today is 2024-04-25, quiet week, stable data' → LOW\n"
        "'Today is 2024-10-30, earnings week and war tensions' → HIGH\n\n"
        "Respond with LOW, MEDIUM, or HIGH only. No explanation."
    )
)


    def evaluate(self, current_date):
        prompt = f"Today is {current_date.strftime('%Y-%m-%d')}. What is the trading risk today?"
        response = self.agent.generate_reply([{"role": "user", "content": prompt}])
        return response["content"].strip().upper()
