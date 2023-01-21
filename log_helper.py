from os import makedirs
import logging
import logging.config

from config import Config

logconfigs = Config.LOGS
logfolder = "logs"
makedirs(logfolder, exist_ok=True)


class LoggerConfig:
    dictConfig = {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] {%(filename)s:%(funcName)s:%(lineno)d} %(levelname)s - %(message)s"
            },
            "console": {
                "format": "[%(levelname)s] %(message)s",
            },
        },
        "handlers": {**{
            logkey: {
                "level": logconfig["level"],
                "formatter": "default",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": f"{logfolder}/{logconfig['filename']}",
                "maxBytes": 1000000,
                "backupCount": 5,
            }
            for logkey, logconfig in logconfigs.items()
        }, **{
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "console",
                "stream": "ext://sys.stdout",
            }
        }},
        "loggers": {
            logkey: {"level": logconfig["level"], "handlers": ["console", logkey]}
            for logkey, logconfig in logconfigs.items()
        },
    }


logging.config.dictConfig(LoggerConfig.dictConfig)
