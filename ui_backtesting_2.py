from random import choice

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA

from helper import StockHelper
from postproc import get_predictions
from preproc import get_stock_data

stocks = StockHelper.list_all_symbols()

for i, s in enumerate(stocks, 1):
    print(f"({i}) {s}")

print("Select Stock: ")
i = int(input())

symbol = stocks[i - 1]
print(symbol)
print()

n_days = 300

print("Welcome")
print(f"Trading {symbol}")
print()
print("-" * 50)
print()


class SmaCross(Strategy):
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, 7)
        self.ma2 = self.I(SMA, price, 30)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()

        elif crossover(self.ma2, self.ma1):
            self.sell()


df = get_stock_data(symbol, n_days)
df.rename(
    columns={
        "open_price": "Open",
        "high_price": "High",
        "low_price": "Low",
        "close_price": "Close",
        "volume": "Volume",
    },
    inplace=True,
)

preds = get_predictions(symbol, df.index.min(), df.index.max())
df.update(preds)

init_cash = int(input("Initial Cash (₹): "))
commission = float(input("Commission Percentage (%): ")) / 100
margin = float(input("Margin (0-1x): "))
period = int(input("Number of days to invest (days): "))

# init_cash = 100000
# commission = 0.01
# margin = 1
# period = 300

bt = Backtest(
    df[-period:],
    SmaCross,
    cash=init_cash,
    exclusive_orders=True,
    commission=commission,
    margin=margin,
    trade_on_close=True,
)
stats = bt.run()
print()

for _, trade in stats._trades.iterrows():
    print(
        f"{'Buy' if trade['Size'] > 0 else 'Sell'} {abs(trade['Size'])} shares @ {trade['EntryPrice']:.2f} on {trade['EntryTime']}"
    )
    print(f"Hold for {trade['Duration']}")
    print(
        f"{'Sell' if trade['Size'] > 0 else 'Sell'} {abs(trade['Size'])} shares @ {trade['ExitPrice']:.2f} on {trade['ExitTime']}"
    )
    print(f"{trade['ReturnPct']:.2f}% return from trade. {trade['PnL']:.2f} P/L")
    print()

print()
print(f"Max PnL: {stats['Equity Final [$]'] - init_cash: .2f}. {stats['Return (Ann.) [%]']:.2f}% returns")

# bt.plot()
