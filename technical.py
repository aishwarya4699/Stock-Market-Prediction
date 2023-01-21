import matplotlib.pyplot as plt
import pandas as pd
from stockstats import StockDataFrame

stocks = StockDataFrame.retype(pd.read_csv("AXISBANK.csv"))


# Moving average Convergence Divergence
plt.figure(figsize=(16, 8))
stocks["macd"].plot()


stocks["close_10_sma"].head()


# Simple moving average
plt.figure(figsize=(16, 8))
stocks["close_10_sma"].plot()


stocks["rsi_6"].head()


# RSI
plt.figure(figsize=(16, 8))
stocks["rsi_6"].plot()


# true range
plt.figure(figsize=(16, 8))
stocks["tr"].plot()


# triple EMA
plt.figure(figsize=(16, 8))
stocks["tema"].plot()
