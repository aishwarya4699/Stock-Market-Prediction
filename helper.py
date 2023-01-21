import threading
from abc import ABC, abstractmethod
from datetime import date
from functools import wraps
from io import BytesIO
from os import path
from pickle import dumps, loads
from tempfile import NamedTemporaryFile
from time import sleep, time
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import pandas_market_calendars as mcal
from bson import Binary
from dateutil.relativedelta import relativedelta
from keras.models import load_model, save_model
from nsepy import get_history
from pandas import Series
from pandas.core.indexes.datetimes import DatetimeIndex
from pandas.errors import EmptyDataError
from tqdm import tqdm

from config import Config
from database.NoSQLModel import PythonModel
from database.SQLModel import Stock, StockPrediction, StockPrice
from db_helper import connect_grid, session_scope
from log_helper import logging

logger = logging.getLogger("default")
_anim = r"|/-\|"
_columns = Config.NSECOLUMNS
tz = Config.TIMEZONE


class ElapsedTimeThread(threading.Thread):
    def __init__(self):
        super(ElapsedTimeThread, self).__init__()
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        thread_start = time()

        while not self.stopped():
            print(f"...{time() - thread_start:.2f} seconds elapsed", end="\r")
            sleep(0.25)

        print(f"Took {time() - thread_start:.2f} seconds\033[K")


def elapsed_time_update(f):
    @wraps(f)
    def print_elapsed_time(*args, **kwargs):
        (thread := ElapsedTimeThread()).start()
        return_val = None

        try:
            return_val = f(*args, **kwargs)

        except KeyboardInterrupt:
            thread.stop()
            thread.join()

        thread.stop()
        thread.join()

        return return_val

    return print_elapsed_time


@elapsed_time_update
def fetch_and_store_csv(
    symbol: str,
    data_dir: str,
    is_index: bool,
    set_key: str,
    from_date: date,
    to_date: date = date.today(),
) -> pd.DataFrame:
    hist = pd.DataFrame()

    try:
        hist = get_history(symbol=symbol, start=from_date, end=to_date, index=is_index)
        concat_df_to_csv(hist, f"{data_dir}/{symbol}.csv")

        if hist.empty:
            raise EmptyDataError

        hist.columns = _columns[set_key]
        hist = hist[~hist.index.duplicated()]
        hist = hist.where(pd.notnull(hist), 0)
        hist = hist.round(3)
        hist = hist.astype({"Volume": int})
        if not is_index:
            hist = hist.astype({"Trades": int, "Deliverable_Volume": int})
        hist.replace({0: None})

    except EmptyDataError:
        logger.warning(f"No data fetched for {symbol} from NSE")

    except Exception as e:
        logger.error(f"Error {e} while fetching {symbol} from NSE")

    else:
        logger.info(f"Fetched {symbol}")

    finally:
        return hist


def store_to_db(df: pd.DataFrame, stock_id: int, name: str):
    for (idx, row) in tqdm(
        df.iterrows(), desc=f"Storing {name} to db", unit=" rows", total=len(df)
    ):
        stock_price = StockPrice(
            date=idx,
            stock_id=stock_id,
            open_price=row.Open or None,
            high_price=row.High or None,
            low_price=row.Low or None,
            close_price=row.Close or None,
            volume=row.Volume or None,
            vwa_price=row.get("VWAP"),
            trades=row.get("Trades"),
            deliverable_volume=row.get("Deliverable_Volume"),
        )

        try:
            with session_scope(autocommit=True) as session:
                session.add(stock_price)
                session.flush()

        except Exception as e:
            logger.error(f"Error {e} while adding StockPrice for {name}. Rows {stock_price}")


def concat_df_to_csv(df: pd.DataFrame, csv_path: str):
    df_csv = (
        pd.read_csv(csv_path, index_col=0, parse_dates=[0])
        if path.exists(csv_path)
        else pd.DataFrame()
    )
    df_csv.combine_first(df).to_csv(csv_path)


def display_time(sec: int):
    print(f"\rCooldown: {_anim[sec % len(_anim)]} 00:{sec:02} remaining", end="", flush=True)


def countdown(sec: int):
    sep = "-" * 27
    print(sep)
    display_time(sec)

    while (sec := sec - 1) >= 0:
        sleep(1)
        display_time(sec)

    print(f"\n{sep}")


class StockHelper:
    indices = Config.STOCKS["Indices"][0]
    stocks = Config.STOCKS["Stocks"][0]

    @classmethod
    def list_all_stocks(cls) -> List[str]:
        return list(cls.stocks.keys())

    @classmethod
    def list_all_symbols(cls) -> List[str]:
        return list(cls.stocks.values())

    @classmethod
    def get_stock_symbol_mapping(cls) -> Dict[str, str]:
        return cls.stocks

    @classmethod
    def get_symbol_stock_mapping(cls) -> Dict[str, str]:
        return {v: k for (k, v) in cls.stocks.items()}

    @classmethod
    def list_all_indices(cls) -> List[str]:
        return list(cls.indices.keys())

    @classmethod
    def list_all_index_symbols(cls) -> List[str]:
        return list(cls.indices.values())

    @classmethod
    def get_index_symbol_mapping(cls) -> Dict[str, str]:
        return cls.indices

    @classmethod
    def get_symbol_index_mapping(cls) -> Dict[str, str]:
        return {v: k for (k, v) in cls.indices.items()}


class ModelHelper:
    def __init__(self, model_name: str, symbol: str, is_keras_model: bool = False):
        self.model_name = model_name
        self.symbol = symbol
        self.keras = is_keras_model

    def save_model_to_mongo(self, model: Any, trained_from: date = None, trained_upto: date = None):
        fs = connect_grid()

        if self.keras:
            with NamedTemporaryFile(suffix='.hdf5', delete=True) as ntf:
                save_model(model, ntf.name, overwrite=True)
                with BytesIO(Binary(ntf.read())) as f:
                    objectId = fs.put(f, filename=self.model_name, chunk_size=2097152)

        else:
            with BytesIO(Binary(dumps(model))) as f:
                objectId = fs.put(f, filename=self.model_name, chunk_size=2097152)

        PythonModel(
            grid_fileid=objectId,
            model_name=self.model_name,
            symbol=self.symbol,
            trained_from=trained_from,
            trained_upto=trained_upto,
        ).save()

    def get_model_from_mongo(self, trained_upto: date) -> Optional[Any]:
        fs = connect_grid()

        python_model = PythonModel.objects(
            model_name=self.model_name, symbol=self.symbol, trained_upto__gte=trained_upto
        ).first()
        if not python_model:
            return

        if not fs.exists(python_model.grid_fileid):
            return

        if self.keras:
             with NamedTemporaryFile(suffix='.hdf5', delete=True) as ntf:
                ntf.write(fs.get_last_version(python_model.model_name).read())
                ntf.flush()
                return load_model(ntf.name)

        else:
            return loads(fs.get_last_version(python_model.model_name).read())

    def delete_model_in_mongo(self, trained_upto: date) -> None:
        fs = connect_grid()

        python_model = PythonModel.objects(
            model_name=self.model_name, symbol=self.symbol, trained_upto__gte=trained_upto
        ).first()
        if not python_model:
            return

        if not fs.exists(python_model.grid_fileid):
            return

        fs.delete(python_model.grid_fileid)
        python_model.delete()


class BaseScaler(ABC):
    @abstractmethod
    def fit(self, s: Series):
        # return self
        raise NotImplementedError

    @abstractmethod
    def transform(self, s):
        # return transform_magic(s)
        raise NotImplementedError

    def fit_transform(self, s):
        return self.fit(s).transform(s)

    @abstractmethod
    def inverse_transform(self, s):
        # return inverse_transform_magic(s)
        raise NotImplementedError


class MinMaxScaler(BaseScaler):
    def fit(self, s: Series):
        self.min = s.min()
        self.max = s.max()
        self.range = self.max - self.min
        return self

    def transform(self, s):
        return (s - self.min) / self.range

    def inverse_transform(self, s):
        return s * self.range + self.min


class LogScaler(BaseScaler):
    def fit(self, s: Series):
        return self

    def transform(self, s):
        return np.log(s)

    def inverse_transform(self, s):
        return np.exp(s)


def get_next_n_trading_days(n: int) -> DatetimeIndex:
    start_date = date.today()
    end_date = start_date + relativedelta(days=n * 3 // 2)

    trading_calendar = mcal.get_calendar("BSE")
    sched = trading_calendar.schedule(start_date, end_date, tz=tz)[:n]

    while len(sched) != n:
        start_date = end_date + relativedelta(days=1)
        end_date = start_date + relativedelta(days=20)
        sched = sched.combine_first(
            trading_calendar.schedule(start_date, end_date, tz=tz))[:n]

    return sched.index


def save_predictions(predictions: Series, model_name: str, stock_symbol, as_of: date) -> None:
    with session_scope(autocommit=True) as session:
        stock = session.query(Stock).filter(
            Stock.symbol == stock_symbol
        ).first()

        if not stock:
            raise Exception("Invalid Stock ID")

        stock_id = stock.id

        for timestamp, price in predictions.iteritems():
            pred = StockPrediction(timestamp.to_pydatetime(), stock_id, price, model_name, as_of)
            session.add(pred)
            session.flush()
