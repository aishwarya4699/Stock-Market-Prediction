import logging
from os import makedirs

from sqlalchemy_utils import create_database, database_exists

from config import Config
from database.SQLModel import Base
from db_helper import db_uri, get_engine

logging.basicConfig(filename="setup.log", level="DEBUG", format="%(asctime)s - %(levelname)s - %(message)s")
paths = Config.PATHS

if __name__ == "__main__":
    logging.info("Starting Setup")

    for set_key, paths_set in paths.items():
        for path in paths_set.values():
            logging.info(f"Creating {path}")
            makedirs(path, exist_ok=True)

    try:
        engine = get_engine(db_uri)
        if not database_exists(db_uri):
            logging.info("Creating Database")
            create_database(db_uri)

        else:
            logging.info("Database exists")

        logging.info("Creating DB tables.")
        Base.metadata.create_all(engine)

    except Exception as e:
        logging.error(f"Couldn't create DB tables. {e}")

    logging.info("Finished Setup")
