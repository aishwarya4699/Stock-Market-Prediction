from datetime import date as dt_date

from sqlalchemy import (Boolean, BigInteger, Column, Date, DateTime, DECIMAL, ForeignKey,
                        String, UniqueConstraint, event, func)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Stock(Base):
    __tablename__ = "stocks"
    id = Column("id", BigInteger, autoincrement=True, primary_key=True)
    name = Column("name", String(64), nullable=False)
    symbol = Column("symbol", String(24), nullable=False)
    is_index = Column("is_index", Boolean, server_default="0")
    latest_date = Column("latest_date", Date)
    created_at = Column("created_at", DateTime, server_default=func.now())
    updated_at = Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now())

    data = relationship("StockPrice", back_populates="stock", cascade="all, delete")

    __table_args__ = (UniqueConstraint("name", "symbol"),)

    def __init__(self, name: str, symbol: str, is_index: bool):
        self.name = name
        self.symbol = symbol
        self.is_index = is_index

    def __repr__(self) -> str:
        return str({
            'Index' if self.is_index else 'Stock': {
                "id": self.id,
                "name": self.name,
                "symbol": self.symbol,
                "latest_date": self.latest_date,
            }
        })


class StockPrice(Base):
    __tablename__ = "stock_prices"
    id = Column("id", BigInteger, autoincrement=True, primary_key=True)
    date = Column("date", Date, nullable=False)
    stock_id = Column(BigInteger, ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False)
    open_price = Column(DECIMAL(12, 5))
    high_price = Column(DECIMAL(12, 5))
    low_price = Column(DECIMAL(12, 5))
    close_price = Column(DECIMAL(12, 5))
    vwa_price = Column(DECIMAL(12, 5))
    volume = Column(BigInteger)
    trades = Column(BigInteger)
    deliverable_volume = Column(BigInteger)
    created_at = Column("created_at", DateTime, server_default=func.now(), nullable=False)

    stock = relationship("Stock", back_populates="data")

    __table_args__ = (UniqueConstraint("date", "stock_id"),)

    def __init__(
        self,
        date: dt_date,
        stock_id: int,
        open_price: float = None,
        high_price: float = None,
        low_price: float = None,
        close_price: float = None,
        vwa_price: float = None,
        volume: int = None,
        trades: int = None,
        deliverable_volume: int = None,
    ):
        self.date = date
        self.stock_id = stock_id
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.vwa_price = vwa_price
        self.volume = volume
        self.trades = trades
        self.deliverable_volume = deliverable_volume

    def __repr__(self) -> str:
        return str({
            "StockPrice": {
                "date": self.date,
                "stock id": self.stock_id,
                "open": self.open_price,
                "high": self.high_price,
                "low": self.low_price,
                "close": self.close_price,
                "vwap": self.vwa_price,
                "volume": self.volume,
                "trades": self.trades,
                "deliverable volume": self.deliverable_volume,
            }
        })


@event.listens_for(StockPrice, "after_insert")
def update_latest_date(mapper, connection, price):
    stocks_table = Stock.__table__
    connection.execute(
        stocks_table.update()
        .where(stocks_table.c.id == price.stock_id)
        .values(latest_date=price.date)
    )


class StockPrediction(Base):
    __tablename__ = "stock_predictions"
    id = Column("id", BigInteger, autoincrement=True, primary_key=True)
    date = Column("date", Date, nullable=False)
    stock_id = Column(BigInteger, ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False)
    predicted_price = Column(DECIMAL(12, 5), nullable=False)
    predictor_model = Column(String(48), nullable=False)
    prediction_as_of = Column(Date)
    created_at = Column("created_at", DateTime, server_default=func.now(), nullable=False)

    def __init__(
        self,
        date: dt_date,
        stock_id: int,
        predicted_price: float,
        predictor_model: str,
        prediction_as_of: dt_date = None,
    ):
        self.date = date
        self.stock_id = stock_id
        self.predicted_price = predicted_price
        self.predictor_model = predictor_model
        self.prediction_as_of = prediction_as_of

    def __repr__(self) -> str:
        return str({
            "StockPrediction": {
                "date": self.date,
                "stock_id": self.stock_id,
                "predicted price": self.predicted_price,
                "predictor model": self.predictor_model,
                "prediction_as_of": self.prediction_as_of,
            }
        })
