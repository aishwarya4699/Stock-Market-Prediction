from datetime import date
from helper import get_next_n_trading_days

from fastquant import backtest
from pandas import Series

from database.SQLModel import Stock, StockPrediction
from db_helper import session_scope
from preproc import get_stock_data
from helper import logging

logger = logging.getLogger("default")


def get_predictions(symbol: str, from_date: date, to_date: date, model: str):
    with session_scope() as ssn:
        if to_date < from_date:
            raise Exception("Invalid Date Range")

        stock = ssn.query(Stock).filter(Stock.symbol == symbol).first()

        if not stock:
            raise Exception("Invalid Symbol")

        stock_id = stock.id

        preds = ssn.query(StockPrediction).filter(
            StockPrediction.stock_id == stock_id,
            StockPrediction.date.between(from_date, to_date),
            StockPrediction.predictor_model == model,
        ).order_by(
            StockPrediction.prediction_as_of
        ).all()

        if not preds:
            raise Exception("No prediction")

        predictions = {p.date: p.predicted_price for p in preds}

    return Series(predictions, name="Close")


def get_strategy(
    symbol: str,
    model: str,
    initial_cash: int,
    commission_percentage: float,
    short_sell: bool,
    margin_percentage: float,
    investment_period: int
):
    try:
        df = get_stock_data(symbol, investment_period)
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

        next_n_trading_days = get_next_n_trading_days(investment_period)
        preds = get_predictions(symbol, next_n_trading_days.min(), next_n_trading_days.max(), model).to_frame()

        df1 = preds.combine_first(df[["Close"]])

        kwargs = {
            "data": df1[-investment_period:].fillna(method="ffill"),
            "init_cash": initial_cash,
            "commission": commission_percentage,
            "allow_short": short_sell,
            "short_max": margin_percentage,
            "return_history": True,
            "verbose": 0,
            "plot": False
        }

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
        }

        strategies["multi"] = {"strats": {strat: strategies[strat] for strat in ("rsi", "smac")}}

        max_pnl = 0
        max_strategy = None
        max_res = None
        max_trades = None

        for strategy, s_kwargs in strategies.items():
            try:
                res, trades = backtest(strategy, **s_kwargs, **kwargs)

                net_pnl = res.pnl[0]

                if max_pnl < net_pnl:
                    max_pnl = net_pnl
                    max_res = res
                    max_trades = trades
                    max_strategy = strategy

            except Exception:
                pass

        if max_strategy:

            final_trades = [{
                "type": order['type'],
                "size": abs(order['size']),
                "price": order['price'],
                "date": order['dt'].to_pydatetime().date(),
                "value": order.value,
                "commission": order.commission,
                "pnl": order.pnl
            } for _, order in max_trades["orders"].iterrows()]

            final_value = max_res.final_value[0]
            final_capital = final_value - max_pnl

            return {
                "name": max_strategy,
                "pnl": max_pnl,
                "value": final_value,
                "capital": final_capital,
                "pnl_pct": (final_value - final_capital) / final_capital * 100,
                "trades": final_trades
            }

    except Exception as e:
        logger.exception(e)
        return
