from os import path
from shutil import rmtree

from sqlalchemy_utils import database_exists

from config import Config
from database.SQLModel import Base
from db_helper import db_uri, get_engine

paths = Config.PATHS
logconfigs = Config.LOGS

if __name__ == "__main__":
    print("[INFO] Starting Teardown")

    for set_key, paths_set in paths.items():
        for folder in paths_set.values():
            rmtree(folder, ignore_errors=True)
            print(f"[INFO] Removed {folder}")

    for logfile in logconfigs.values():
        logpath = logfile["filename"]
        if path.exists(logpath):
            open(logpath, "w").close()
            print(f"[INFO] Clearing {logpath}")

    try:
        engine = get_engine(db_uri)
        if database_exists(engine.url): Base.metadata.drop_all(engine)

    except Exception as e: print(f"[ERROR] Couldn't drop DB tables. {e}")

    else: print("[INFO] Dropped DB tables.")

    print("[INFO] Finished Teardown")
