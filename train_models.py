from time import time, ctime

from pandas import Series
from sklearn.preprocessing import StandardScaler

from log_helper import logging
from arima import ARIMA
from helper import LogScaler, MinMaxScaler, StockHelper, get_next_n_trading_days, save_predictions
from lstm import LSTM
from svm import SVM

logger = logging.getLogger("cron")


def run_service():
    stocks = StockHelper.get_stock_symbol_mapping()
    for stock, symbol in stocks.items():
        logger.info(f"Starting training for {stock} [{symbol}] at {ctime()}")
        models = {
            "SVM": SVM(symbol, scaler=StandardScaler),
            "ARIMA": ARIMA(symbol, scaler=LogScaler),
            "LSTM": LSTM(symbol, scaler=MinMaxScaler, is_keras=True),
        }

        for model_name, model in models.items():
            logger.info(f"\tTraining {model_name} for {stock}")
            start_time = time()
            train_data = model.train_data

            n_days = 300
            test_data = Series(index=get_next_n_trading_days(n_days))

            predictions = model.fit_predict(n_days)
            predictions = Series(data=predictions, index=test_data.index[: len(predictions)])

            save_predictions(predictions, type(model).__name__, symbol, train_data.index.max().to_pydatetime())
            logger.info(f"\tTrained {model_name} for {stock} in {time() - start_time:.3f} seconds")

        logger.info(f"Finished training for {stock} [{symbol}] at {ctime()}")


if __name__ == "__main__":
    run_service()
