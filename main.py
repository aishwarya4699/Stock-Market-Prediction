# %%
import math

import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame, Series
from sklearn.metrics import mean_absolute_error, mean_squared_error

from arima import ARIMA
from helper import (LogScaler, MinMaxScaler, StockHelper,
                    get_next_n_trading_days, save_predictions)
from lstm import LSTM
from svm import SVM

# %%
stocks = StockHelper.get_stock_symbol_mapping()
mylist = list(stocks.items())
stock, symbol = mylist[11]

# %%
total_days = 300
train_size = 0.95
testing = train_size != 1
save_model = False
to_save_predictions = False

# %%
# model_name = "SVM"
model_name = "ARIMA"
# model_name = "LSTM"

if model_name == "ARIMA":
    model = ARIMA(symbol, total_days, train_size, scaler=LogScaler, save_model=save_model)

elif model_name == "LSTM":
    model = LSTM(symbol, total_days, train_size, scaler=MinMaxScaler, is_keras=True, save_model=save_model)

elif model_name == "SVM":
    model = SVM(symbol, total_days, train_size, scaler=MinMaxScaler, save_model=save_model)

else:
    raise NotImplementedError

# %%
train_data = model.train_data

if testing:
    n_days = 0
    test_data = model.test_data

else:
    n_days = 10
    test_data = Series(index=get_next_n_trading_days(n_days))

# %%
fig, ax = plt.subplots(figsize=(10, 6))
ax.grid(True)
ax.set_title(stock)
ax.set_xlabel("Dates")
ax.set_ylabel("Closing Price")
ax.plot(train_data, c="red", label="Training Data")
ax.plot(test_data, c="black", label="Testing Data")
ax.legend()
plt.show()

# %%
predictions = model.fit_predict(n_days)
predictions
# %%
predictions = Series(data=predictions, index=test_data.index[:len(predictions)])

# %%
if to_save_predictions:
    save_predictions(
        predictions, type(model).__name__, symbol, train_data.index.max().to_pydatetime()
    )

# %%
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(train_data, c="red", label="Training Data")
ax.plot(test_data, c="black", label="Testing Data")
ax.plot(predictions, c="green", label="Predicted Price")
ax.grid(True)
ax.legend()
plt.show()

# %%
if testing:
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
dff = DataFrame({"actual": test_data, "predictions": predictions})
print(dff)

# %%
