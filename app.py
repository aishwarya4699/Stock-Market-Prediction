from datetime import datetime
from flask import Flask, render_template, request

from helper import StockHelper
from postproc import get_predictions, get_strategy

app = Flask(__name__)

stocks = StockHelper.get_symbol_stock_mapping()
models = ["SVM", "LSTM", "ARIMA"]


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/prediction_form", methods=["GET"])
def prediction_form():
    return render_template("prediction_form.html", stocks=stocks, models=models)


@app.route("/predictions", methods=["GET"])
def predictions():
    request_data = request.args
    print(request.args)
    symbol = request_data.get("symbol", "")
    model = request_data.get("model", "")
    start_date = request_data.get("start_date", "")
    end_date = request_data.get("end_date", "")
    from_date = datetime.strptime(start_date, "%Y-%m-%d")
    to_date = datetime.strptime(end_date, "%Y-%m-%d")

    return render_template("predictions.html", predictions=get_predictions(symbol, from_date, to_date, model), symbol=symbol)


@app.route("/strategy_form", methods=["GET"])
def strategy_form():
    return render_template("strategy_form.html", stocks=stocks, models=models)


@app.route("/strategy", methods=["GET"])
def strategy():
    request_data = request.args
    symbol = request_data.get("symbol", "")
    model = request_data.get("model", "")
    initial_cash = int(request_data.get("initial_cash", "0"))
    commission_percentage = int(request_data.get("commission_percentage", "0")) / 100
    short_sell = request_data.get("short_sell") == "on"
    margin_percentage = int(request_data.get("margin_percentage", "0")) / 100
    investment_period = int(request_data.get("investment_period", "0"))

    return render_template(
        "strategy.html", strategy=get_strategy(
            symbol,
            model,
            initial_cash,
            commission_percentage,
            short_sell,
            margin_percentage,
            investment_period,
        ), symbol=symbol
    )


if __name__ == "__main__":
    app.run(debug=True)
