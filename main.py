import os
from datetime import datetime
from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from alpaca_trade_api import REST
from timedelta import Timedelta

from agents.sentiment_agent import SentimentAgent
from agents.macro_agent import MacroNewsAgent
from agents.risk_agent import RiskAgent
from agents.meta_evaluator_agent import MetaEvaluatorAgent
from agents.trade_logger import TradeLogger

API_KEY = os.getenv("APCA_API_KEY_ID")
API_SECRET = os.getenv("APCA_API_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets/v2"

ALPACA_CREDS = {
    "API_KEY": API_KEY,
    "API_SECRET": API_SECRET,
    "PAPER": True
}

class MLTrader(Strategy):
    def initialize(self, symbol="SPY", cash_at_risk=0.5):
        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.last_trade_date = None
        self.cash_at_risk = cash_at_risk
        self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)

        self.sentiment_agent = SentimentAgent()
        self.macro_agent = MacroNewsAgent()
        self.risk_agent = RiskAgent()
        self.meta_agent = MetaEvaluatorAgent()
        self.trade_logger = TradeLogger()

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk / last_price)
        return cash, last_price, quantity

    def get_dates(self):
        today = self.get_datetime()
        three_days_prior = today - Timedelta(days=3)
        return today.strftime('%Y-%m-%d'), three_days_prior.strftime('%Y-%m-%d')

    def get_news(self):
        today, three_days_prior = self.get_dates()
        news = self.api.get_news(symbol=self.symbol, start=three_days_prior, end=today)

        print(f"[DEBUG] Retrieved {len(news)} news articles from {three_days_prior} to {today}")
        if not news:
            print("[WARNING] No news returned from Alpaca API — using fallback dummy headlines.")
            headlines = [
                "SPY surges after strong jobs report",
                "Federal Reserve hints at possible rate pause",
                "Market reacts positively to inflation slowdown"
            ]
        else:
            headlines = [ev._raw.get("headline", "") for ev in news]
            for i, headline in enumerate(headlines):
                print(f"[{i+1}] Headline: {headline}")
        return headlines

    def on_trading_iteration(self):
        portfolio_value = self.get_portfolio_value()
        current_date = self.get_datetime()
        print(f"\n[INFO] {current_date.date()}: Portfolio Value: ${portfolio_value:,.2f}")

        if self.last_trade_date:
            days_since_trade = (current_date - self.last_trade_date).days
            if days_since_trade < 3:
                print(f"[INFO] Waiting — only {days_since_trade} day(s) since last trade")
                return

        cash, last_price, quantity = self.position_sizing()
        if cash < last_price:
            print(f"[INFO] Not enough cash to buy {self.symbol}")
            return

        headlines = self.get_news()
        sentiment = self.sentiment_agent.evaluate(headlines)
        print(f"[SentimentAgent]: {sentiment}")
        if sentiment != "POSITIVE":
            return

        recommendation = self.meta_agent.evaluate_trust()
        print(f"[MetaEvaluator]: {recommendation}")
        if "Set trust_level to" in recommendation:
            try:
                level = float(recommendation.split("to")[1].strip())
                self.macro_agent.adjust_config(trust_level=level)
            except Exception as e:
                print(f"[MetaEvaluator Error] Failed to parse trust_level: {e}")

        macro_outlook = self.macro_agent.evaluate(headlines)
        print(f"[MacroNewsAgent]: {macro_outlook}")
        if macro_outlook != "POSITIVE":
            return

        risk = self.risk_agent.evaluate(current_date)
        print(f"[RiskAgent]: {risk}")
        if risk != "LOW":
            return

        order = self.create_order(
            self.symbol,
            quantity,
            "buy",
            type="bracket",
            take_profit_price=last_price * 1.2,
            stop_loss_price=last_price * 0.95
        )
        self.submit_order(order)

        print(f"[TRADE] Bought {quantity} shares of {self.symbol} at ${last_price:.2f}")
        self.last_trade_date = current_date

        # Log the trade
        self.trade_logger.log_trade({
            "symbol": self.symbol,
            "entry_price": last_price,
            "outcome": "PENDING",
            "sentiment": sentiment,
            "macro": macro_outlook,
            "risk": risk
        })

# Run backtest
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 3, 31)

broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader(name="mlstrat", broker=broker, parameters={"symbol": "SPY", "cash_at_risk": 0.5})
strategy.backtest(YahooDataBacktesting, start_date, end_date)
