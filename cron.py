from functools import wraps
from importlib import import_module
from time import sleep
from uuid import uuid4

from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from config import Config
from daemon_helper import Daemon
from log_helper import logging

logger = logging.getLogger("cron")
tz = Config.TIMEZONE
jobs = Config.CRONJOBS
cron_pidfile = Config.CRONPIDFILE

jobstores = {"default": MongoDBJobStore()}
executors = {"default": ThreadPoolExecutor(20), "processpool": ProcessPoolExecutor(5)}
job_defaults = {"coalesce": False, "max_instances": 3}

scheduler = BackgroundScheduler()
scheduler.configure(
    jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=tz
)


def log_cronjob(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        job_id = uuid4()
        logger.info(f"Job {job_id} {f.__name__}(*args={args}, **kwargs={kwargs}")

        try:
            logger.info(f"Running job {job_id}")
            return_val = f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Error while running job {job_id}. {e}")
            raise e

        else:
            logger.info(f"Job {job_id} returned {return_val}")
            return return_val

    return wrapper


class SchedulerDaemon(Daemon):
    def run(self):
        for job, details in jobs.items():
            logger.info(f"Adding job {job} with {details}")
            module = import_module(details["module"])
            func = getattr(module, details["function"])
            wrapped_func = log_cronjob(func)
            scheduler.add_job(
                func=wrapped_func,
                trigger=details["trigger"],
                args=details.get("args", ()),
                kwargs=details.get("kwargs", {}),
                **details["job_kwargs"],
            )

        logger.info("Starting Scheduler")
        scheduler.start()

        try:
            while True:
                logger.info("Running jobs...")
                scheduler.print_jobs()
                sleep(60)

        finally:
            logger.info("Removing all jobs")
            scheduler.remove_all_jobs()
            logger.info("Stopping Scheduler")
            scheduler.shutdown()


if __name__ == "__main__":
    scheduler_daemon = SchedulerDaemon(pidfile=cron_pidfile)

    try:
        logger.info("Starting Daemon")
        scheduler_daemon.run()

    finally:
        logger.info("Stopping Daemon")
        scheduler_daemon.stop()
