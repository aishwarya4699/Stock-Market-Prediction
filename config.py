from os import getenv

from pytz import timezone


class Config:
    STOCKS = {
        "Indices": ({"NIFTY Bank": "BANKNIFTY"}, True),
        "Stocks": (
            {
                "Axis Bank": "AXISBANK",
                "Bandhan Bank": "BANDHANBNK",
                "Bank of Baroda": "BANKBARODA",
                "Federal Bank": "FEDERALBNK",
                "HDFC Bank": "HDFCBANK",
                "ICICI Bank": "ICICIBANK",
                "IDFC First Bank": "IDFCFIRSTB",
                "IndusInd Bank": "INDUSINDBK",
                "Kotak Mahindra Bank": "KOTAKBANK",
                "Punjab National Bank": "PNB",
                "RBL Bank": "RBLBANK",
                "State Bank of India": "SBIN",
            },
            False,
        ),
    }
    SQLALCHEMY = {
        "MYSQL": {
            "drivername": "mysql+pymysql",
            "username": "root",
            "password": getenv("MYSQL_PASSWORD", "root"),
            "host": "127.0.0.1",
            "port": 3306,
            "database": "capstone",
        },
        "POSTGRES": {
            "drivername": "postgres",
            "username": "root",
            "password": getenv("POSTGRES_PASSWORD"),
            "host": "localhost",
            "port": 5432,
            "database": "capstone",
        },
    }
    BASEDIR = "data"
    PATHS = {"csv": {"Indices": f"{BASEDIR}/csv/indices", "Stocks": f"{BASEDIR}/csv/stocks"}}
    NSECOLUMNS = {
        "Indices": ("Open", "High", "Low", "Close", "Volume", "Turnover"),
        "Stocks": (
            "Symbol",
            "Series",
            "Prev Close",
            "Open",
            "High",
            "Low",
            "Last",
            "Close",
            "VWAP",
            "Volume",
            "Turnover",
            "Trades",
            "Deliverable_Volume",
            "Percent_Deliverble",
        ),
    }
    TIMEZONE = timezone("Asia/Kolkata")
    LOGS = {
        "default": {"filename": "root.log", "level": "INFO"},
        "fetch": {"filename": "fetch.log", "level": "INFO"},
        "cron": {"filename": "cron.log", "level": "INFO"},
        "debug": {"filename": "debug.log", "level": "DEBUG"},
    }
    CRONJOBS = {
        "data_fetch": {
            "module": "data_service",
            "function": "run_service",
            "trigger": "cron",
            "job_kwargs": {"hour": "6,22", "minute": 30},
        },
        "train_models": {
            "module": "train_models",
            "function": "run_service",
            "trigger": "cron",
            "job_kwargs": {"hour": 3, "minute": 0},
        },
    }
    CRONPIDFILE = "/tmp/cron_pid"
    MONGODB = "capstone"
    RSSURLS = {
        "Brokerage Recos": "https://www.moneycontrol.com/rss/brokeragerecos.xml",
        "Business News": "https://www.moneycontrol.com/rss/business.xml",
        "Buzzing Stocks": "https://www.moneycontrol.com/rss/buzzingstocks.xml",
        "Currency News": "https://www.moneycontrol.com/rss/currency.xml",
        "Current Affairs": "https://www.moneycontrol.com/rss/currentaffairs.xml",
        "Economy News": "https://www.moneycontrol.com/rss/economy.xml",
        "Global Markets": "https://www.moneycontrol.com/rss/internationalmarkets.xml",
        "IPO News": "https://www.moneycontrol.com/rss/iponews.xml",
        "Latest News": "https://www.moneycontrol.com/rss/latestnews.xml",
        "Market Edge": "https://www.moneycontrol.com/rss/marketedge.xml",
        "Market Outlook": "https://www.moneycontrol.com/rss/marketoutlook.xml",
        "Market Reports": "https://www.moneycontrol.com/rss/marketreports.xml",
        "Results News": "https://www.moneycontrol.com/rss/results.xml",
        "Technicals": "https://www.moneycontrol.com/rss/technicals.xml",
        "World News": "https://www.moneycontrol.com/rss/worldnews.xml",
    }
