from pathlib import Path

from uvicorn.config import LOGGING_CONFIG

from odoorpc_api.settings import env

ROOT_DIR = Path.cwd()
LOG_FILE_PATH = ROOT_DIR / "logs" / "odooapi.log"

if env.LOGFILE:
    LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

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
