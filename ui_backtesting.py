import matplotlib.pyplot as plt
import mplfinance as mpf
from fastquant import backtest

from helper import StockHelper, get_next_n_trading_days
from postproc import get_predictions
from preproc import get_stock_data

# %%
print("Welcome")
print()

stocks = StockHelper.list_all_symbols()

for i, m in enumerate(stocks, 1):
    print(f"({i}) {m}")

print()
i = int(input("Select Stock: "))

symbol = stocks[i - 1]
print(symbol)
print()

models = ["SVM", "LSTM", "ARIMA"]

for i, m in enumerate(models, 1):
    print(f"({i}) {m}")

print()
i = int(input("Select Model: "))

model = models[i - 1]
print(model)
print()

print(f"Trading {symbol}")
print()
print("-" * 50)
print()

# %%
init_cash = int(input("Initial Cash (₹): "))
commission = float(input("Commission Percentage (%): ")) / 100
allow_short = input("OK to Short Sell ? (y/n): ").lower() == "y"
short_max = float(input("Maximum short position allowable relative to portfolio (x): "))
period = int(input("Number of days to invest (days): "))
# add_cash_freq = input("How often to add more cash (D/W/M/Y): ")
# add_cash_amount = int(input("How much more cash (₹): "))

# init_cash = 100000
# commission = 0.01
# allow_short = True
# short_max = 1.25
# period = 150
# add_cash_freq = "M"
# add_cash_amount = 0
# print(df1)
# print()
# print(df1[-period:].dropna())

# %%
df = get_stock_data(symbol, period)
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

# %%
show_roc = False
show_bollinger = not False
show_ema = not False
show_sma = not False

fig, ax = plt.subplots()

if show_roc:
    n = 2
    df["roc"] = df["Close"].diff(n) / df["Close"].shift(n)
    df["roc"].plot(label="ROC", secondary_y=True, ax=ax, legend=True)

if show_bollinger:
    window = 20
    n = 2
    df["middle_band"] = df["Close"].rolling(window=window).mean()
    df["upper_band"] = (
        df["Close"].rolling(window=window).mean() + df["Close"].rolling(window=window).std() * n
    )
    df["lower_band"] = (
        df["Close"].rolling(window=window).mean() - df["Close"].rolling(window=window).std() * n
    )
    ax.fill_between(df.index, df["upper_band"], df["lower_band"], alpha=0.2, label="Bollinger Band")
    ax.plot(df["middle_band"], "y--")
    # plt.plot(df["upper_band"], "g--", label="upper")
    # ax.plot(df["middle_band"], "y--", label="middle")
    # plt.plot(df["lower_band"], "r--", label="lower")

if show_ema:
    df["EWMA"] = df["Close"].ewm(halflife=0.5, min_periods=20).mean()
    ax.plot(df["EWMA"], label="EWMA")

if show_sma:
    for w in (5, 15, 30, 50, 100, 200):
        df[f"SMA{w}"] = df["Close"].rolling(window=w).mean()
        ax.plot(df[f"SMA{w}"], label=f"SMA{w}")

ax.plot(df["Close"], label="close", linewidth=2)

ax.legend()
plt.show()

# %%
mc = mpf.make_marketcolors(up="g", down="r", wick={"up": "blue", "down": "orange"})
m = mpf.make_mpf_style(marketcolors=mc)
# roc_plot = mpf.make_addplot(df.roc, panel=2, ylabel="ROC")
mpf.plot(
    df,
    style="yahoo",
    type="candle",
    mav=(5, 15, 30, 50, 100, 200),
    returnfig=True,
    title=f"{symbol}, {period} days",
    # addplot=[roc_plot],
    figratio=(12, 8),
    figscale=1.5,
    ylabel="Price (INR)",
    volume=True,
)

mpf.show()

# %%
next_n_trading_days = get_next_n_trading_days(period)
# preds = get_predictions(symbol, df.index.min(), df.index.max(), model)
preds = get_predictions(symbol, next_n_trading_days.min(), next_n_trading_days.max(), model).to_frame()

df1 = preds.combine_first(df[["Close"]])

# # %%
# sma5 = df.Close.rolling(window=5).mean()
# sma30 = df.Close.rolling(window=30).mean()
# sma100 = df.Close.rolling(window=100).mean()

# buy1 = df.Open > sma5
# buy2 = df.Open > sma30
# buy3 = df.Open > sma100
# BUY = buy1 & buy2 & buy3

# sell1 = df.Open < sma5
# sell2 = df.Open < sma30
# sell3 = df.Open < sma100
# SELL = sell1 & sell2 & sell3

# custom = "custom1"

# df1.loc[BUY & 1, custom] = -1
# df1.loc[SELL & 1, custom] = 1

# # %%
# prev_close = df.Close.shift(-1)
# buy1 = df.Open < prev_close
# BUY = buy1

# sell1 = df.Open > prev_close
# SELL = sell1

# custom = "custom2"

# df1.loc[BUY & 1, custom] = -1
# df1.loc[SELL & 1, custom] = 1

# %%
kwargs = {
    "data": df1[-period:].fillna(method="ffill"),
    "init_cash": init_cash,
    "commission": commission,
    "allow_short": allow_short,
    "short_max": short_max,
    # "add_cash_freq": add_cash_freq,
    # "add_cash_amount": add_cash_amount,
    "return_history": True,
    # "verbose": 0,
}

# %%
strategies = {
    "smac": {
        "fast_period": 15,
        "slow_period": 40,
    },
    "emac": {
        "fast_period": 15,
        "slow_period": 40,
    },
    "buynhold": {},
    "bbands": {
        "period": 30,
        "devfactor": 1,
    },
    "rsi": {
        "rsi_period": 7,
        "rsi_upper": 70,
        "rsi_lower": 35,
    },
    "macd": {
        "fast_period": 15,
        "slow_period": 40,
        "signal_period": 20,
        "sma_period": 30,
        "dir_period": 10,
    },
    # "custom": {
    #     "upper_limit": 0.5,
    #     "lower_limit": -0.5,
    #     "custom_column": "custom1"
    # },
    # "custom": {
    #     "upper_limit": 0.5,
    #     "lower_limit": -0.5,
    #     "custom_column": "custom2"
    # },
}

strategies["multi"] = {"strats": {strat: strategies[strat] for strat in ("rsi", "smac")}}

max_pnl = 0
max_strategy = None
max_res = None

for strategy, s_kwargs in strategies.items():
    try:
        res = backtest(strategy, **s_kwargs, **kwargs)

        net_pnl = res[0].pnl[0]

        print(strategy)
        print(f"Net PnL: {net_pnl}")
        print()

        if max_pnl < net_pnl:
            max_pnl = net_pnl
            max_res = res
            max_strategy = strategy
    except Exception:
        pass

print()

if max_strategy is not None:
    for _, order in max_res[1]["orders"].iterrows():
        print(
            f"{order['type']} {abs(order['size'])} shares @ {order['price']:.2f} on {order['dt']}",
            f"{order.value:.2f} Value. {order.commission:.2f} Commission. {order.pnl:.2f} P/L",
            sep="\n"
        )
        print()

    final_value = max_res[0].final_value[0]
    final_capital = final_value - max_pnl

    print()
    print(
        f"Using {max_strategy} strategy",
        f"Final Portfolio Value: {final_value:.2f}. {final_capital:.2f} Invested",
        f"Max PnL: {max_pnl:.2f}. {(final_value - final_capital) / final_capital * 100:.2f}% return",
        sep="\n"
    )

else:
    print("Error")
