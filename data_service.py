from datetime import date, datetime

import pandas_market_calendars as mcal
from dateutil.relativedelta import relativedelta

from config import Config
from database.SQLModel import Stock
from db_helper import session_scope
from helper import countdown, fetch_and_store_csv, store_to_db
from log_helper import logging

logger = logging.getLogger("fetch")
csv_dirs = Config.PATHS["csv"]
stocks = Config.STOCKS
tz = Config.TIMEZONE


def run_service():
    trading_calendar = mcal.get_calendar("BSE")

    for set_key, (stock_set, is_index) in stocks.items():
        n = len(stock_set)
        logger.info(f"Fetching {n} {set_key}\n")

        for i, (name, symb) in enumerate(stock_set.items(), 1):
            logger.info(f"{i}/{n} Fetching {symb}...")

            try:
                with session_scope(autocommit=True) as session:
                    if not (stock := session.query(Stock).filter(Stock.name == name).first()):
                        stock = Stock(name=name, symbol=symb, is_index=is_index)
                        session.add(stock)
                        session.flush()
                    latest_date = stock.latest_date
                    stock_id = stock.id

            except Exception as e:
                logger.error(f"Error {e} while adding Stock {name} {symb}")
                continue

            from_date = latest_date + relativedelta(days=1) if latest_date else date(1996, 1, 1)
            to_date = date.today()

            if from_date > to_date or (
                dates_to_fetch := trading_calendar.schedule(from_date, to_date, tz=tz)
            ).empty: continue

            if dates_to_fetch.market_close.max() + relativedelta(hours=2) > datetime.now(tz=tz):
                to_date -= relativedelta(days=1)

            if from_date > to_date or (
                dates_to_fetch := trading_calendar.schedule(from_date, to_date, tz=tz)
            ).empty: continue

            num_attempts, cooldown_time = 3, 5
            for attempt in range(1, num_attempts + 1):
                countdown(cooldown_time + (attempt - 1) * 2)
                logger.info(
                    f"\nAttempt {attempt}/{num_attempts}. Fetching {name} data from " +
                    f"{dates_to_fetch.index.min().date()} to {dates_to_fetch.index.max().date()}"
                )

                if (df := fetch_and_store_csv(
                    symb, csv_dirs[set_key], is_index, set_key, from_date, to_date
                )).empty: continue
                logger.info(f"Saved {symb} to file")

                store_to_db(df, stock_id, name)
                logger.info(f"Saved {name} to DB\n")

                break


if __name__ == "__main__":
    run_service()
