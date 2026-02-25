import os
from pathlib import Path

from uvicorn.config import LOGGING_CONFIG

from core.settings import env

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE_PATH = os.path.join(BASE_DIR, "logs", "odooapi.log")

if env.LOGFILE:
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

    LOGGING_CONFIG["formatters"]["myformat"] = {
        "format": "{asctime} {levelname} {message}",
        "datefmt": "%Y-%m-%d %H:%M:%S",
        "style": "{",
    }

    LOGGING_CONFIG["handlers"]["file_handler"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "level": "INFO",
        "formatter": "myformat",
        "filename": LOG_FILE_PATH,
        "maxBytes": 5 * 1024 * 1024,
        "backupCount": 3,
        "mode": "a",
        "encoding": "utf8",
    }

    LOGGING_CONFIG["loggers"]["odooapi_logger"] = {
        "handlers": ["default", "file_handler"],
        "level": "INFO",
        "propagate": False,
    }
