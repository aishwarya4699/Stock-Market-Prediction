from datetime import datetime

from sqlalchemy import and_

from arima import ARIMA
from database.SQLModel import Stock, StockPrediction, StockPrice
from db_helper import session_scope
from helper import StockHelper
from lstm import LSTM
from svm import SVM

# ch = input("Interactive = 1: ")
ch = 1

stocks = StockHelper.list_all_symbols()

for i, s in enumerate(stocks, 1):
    print(f"({i}) {s}")

print("Select Stock: ")
i = int(input()) if ch else 12

symbol = stocks[i - 1]
print(symbol)
print()

models = {"ARIMA": ARIMA, "LSTM": LSTM, "SVM": SVM}

m_k, m_v = zip(*models.items())

for i, s in enumerate(m_k, 1):
    print(f"({i}) {s}")

print("Enter Model: ")
i = int(input()) if ch else 4

m = m_k[i - 1]
model = m_v[i - 1]
print(m)
print()

print("Start Date (YYYY-MM-DD): ")
s_d = (
    datetime.strptime(input(), "%Y-%m-%d").date()
    if ch
    else datetime(2021, 5, 1).date()
)
print("End Date (YYYY-MM-DD): ")
e_d = (
    datetime.strptime(input(), "%Y-%m-%d").date()
    if ch
    else datetime(2021, 6, 1).date()
)

with session_scope() as ssn:
    stock = ssn.query(Stock).filter(Stock.symbol == symbol).first()

    if not stock:
        raise Exception("Invalid Stock ID")

    stock_id = stock.id

    preds = (
        ssn.query(
            StockPrediction.date,
            StockPrediction.predicted_price,
            StockPrice.close_price,
        )
        .join(
            StockPrice, and_(
                StockPrice.stock_id == StockPrediction.stock_id,
                StockPrice.date == StockPrediction.date,
            ), isouter=True
        )
        .filter(
            StockPrediction.stock_id == stock_id,
            StockPrediction.date.between(s_d, e_d),
            StockPrediction.predictor_model == m,
        )
        .order_by(StockPrediction.date, StockPrediction.prediction_as_of.desc())
        .all()
    )

    print()
    dates = set()

    if not preds:
        print("No predictions")

    else:
        for pred in preds:
            date = pred.date
            prediction = pred.predicted_price
            actual = pred.close_price
            if date not in dates:
                print(f"{date}: {prediction}", end=" ")
                if actual is not None:
                    diff = abs(actual - prediction) / actual * 100
                    print(f"[Actual Price = {actual} ({diff}% error)]", end=" ")
                print()
                dates.add(date)
