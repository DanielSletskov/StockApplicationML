from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from datetime import datetime
from alpaca_trade_api import REST
from timedelta import Timedelta

from agents.sentiment_agent import SentimentAgent
from agents.macro_agent import MacroNewsAgent
from agents.risk_agent import RiskAgent

API_KEY = "PK68T85U8L3DVY4MDB1D"
API_SECRET = "TyxLmcfIeW929amzkDqmhmchh899s0Uy8cLKwrmr"
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
        self.cash_at_risk = cash_at_risk
        self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)

        self.sentiment_agent = SentimentAgent()
        self.macro_agent = MacroNewsAgent()
        self.risk_agent = RiskAgent()

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
        headlines = [ev._raw.get("headline", "") for ev in news]
        return headlines

    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
        if cash < last_price or self.last_trade is not None:
            return

        headlines = self.get_news()
        sentiment = self.sentiment_agent.evaluate(headlines)
        print(f"[SentimentAgent] → {sentiment}")
        if sentiment != "POSITIVE":
            return

        macro_outlook = self.macro_agent.evaluate(headlines)
        print(f"[MacroNewsAgent] → {macro_outlook}")
        if macro_outlook != "POSITIVE":
            return

        risk = self.risk_agent.evaluate(self.get_datetime())
        print(f"[RiskAgent] → {risk}")
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
        self.last_trade = "buy"

start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 3, 31)

broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader(name="mlstrat", broker=broker, parameters={"symbol": "SPY", "cash_at_risk": 0.5})
strategy.backtest(YahooDataBacktesting, start_date, end_date)
