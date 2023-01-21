from typing import Tuple

import numpy as np
from pandas import DataFrame, Series, read_sql

from database.SQLModel import Stock, StockPrice
from db_helper import session_scope


def get_stock_data(symbol: str, days: int = 300) -> DataFrame:
    with session_scope() as ssn:
        query = ssn.query(
            StockPrice.date,
            StockPrice.open_price,
            StockPrice.high_price,
            StockPrice.low_price,
            StockPrice.close_price,
            StockPrice.vwa_price,
            StockPrice.volume,
            StockPrice.trades,
            StockPrice.deliverable_volume,
        ).join(
            Stock, StockPrice.stock_id == Stock.id
        ).filter(
            Stock.symbol == symbol, Stock.is_index.is_(False)
        ).order_by(
            StockPrice.date.desc()
        ).limit(days).statement

        df = read_sql(query, ssn.bind, index_col=["date"], parse_dates=["date"])

    df = df.sort_index().replace(0, np.nan).bfill()

    df["percent_deliverable"] = df.deliverable_volume / df.volume * 100
    df["turnover"] = df.vwa_price * df.volume

    return df


def get_train_test_data(
    symbol: str, total_days: int = 300, train_size: float = 0.9
) -> Tuple[Series, Series]:
    df = get_stock_data(symbol, total_days)

    assert 0 < train_size <= 1

    close = df["close_price"]
    train_size = int(len(close) * train_size)
    train_data, test_data = close[:train_size], close[train_size:]

    return train_data, test_data


def get_train_data(symbol: str, total_days: int = 300) -> Series:
    df = get_stock_data(symbol, total_days)

    train_data = df["close_price"]

    return train_data
