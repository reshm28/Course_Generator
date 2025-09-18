import logging
from logging.config import dictConfig


def configure_logging(level: str = "INFO") -> None:
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": level,
                }
            },
            "root": {
                "handlers": ["console"],
                "level": level,
            },
        }
    )
    logging.getLogger(__name__).info("Logging configured at %s", level)
