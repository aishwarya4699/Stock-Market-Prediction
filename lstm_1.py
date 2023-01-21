# %%
import math
from random import choice

import matplotlib.pyplot as plt
import numpy as np
from pandas import Series
from sklearn.metrics import mean_absolute_error, mean_squared_error

from helper import MinMaxScaler, StockHelper
from preproc import get_train_test_data

# %%
stocks = StockHelper.get_stock_symbol_mapping()
stock, symbol = choice(list(stocks.items()))

# %%
train_size = 0.9

train_data, test_data = get_train_test_data(symbol, 300, train_size)
print(train_data.tail(), test_data.head(), sep="\n")

# %%
n_days = 10
sc = MinMaxScaler()

train_data = sc.fit_transform(train_data)
window = 60

predictions = []
X_test_values = train_data[-window:].values

for i in range(n_days):
    X_test = np.array([X_test_values]).reshape(1, -1, 1)
    predicted_stock_price = model.predict(X_test)
    predictions.append(predicted_stock_price[0][0])
    X_test_values = np.delete(X_test_values, 0)
    X_test_values = np.concatenate((X_test_values, predicted_stock_price[0]))

predictions = np.array(predictions)

# %%
predictions = sc.inverse_transform(predictions)
predictions = Series(predictions, test_data.index[:10])

train_data = sc.inverse_transform(train_data)

# %%
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(train_data, color="black", label="actual")
ax.plot(test_data, color="blue", label="actual")
ax.plot(predictions, color="green", label="predicted")
ax.grid(True)
ax.legend()
plt.show()

# %%
mae_score = mean_absolute_error(test_data, predictions)
print(f"MAE: {mae_score}")
rmse_score = math.sqrt(mean_squared_error(test_data, predictions))
print(f"RMSE: {rmse_score}")
normalised_rmse_score = mean_squared_error(test_data, predictions, squared=False) / (
    test_data.max() - test_data.min()
)
print(f"NRMSE: {normalised_rmse_score}")
mape_score = np.mean(np.abs(predictions - test_data) / np.abs(test_data))
print(f"MAPE: {mape_score}")

# %%
