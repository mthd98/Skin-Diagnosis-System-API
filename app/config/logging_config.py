import logging
import logging.config

from app.config import config

# Read the logging flag from the environment (defaulting to enabled)
LOGGING_ENABLED = config.is_logging_enabled()

# Define the global logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "INFO",  # Show INFO and above on the console
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": "app.log",  # Make sure the directory is writable
            "mode": "a",
            "level": "INFO",  # Log INFO and above to the file
        },
    },
    "loggers": {
        # Configure third-party loggers to only log warnings or above
        "pymongo": {
            "level": "WARNING",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "urllib3": {
            "level": "WARNING",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",  # The root logger logs INFO and above
    },
}

# Apply the logging configuration globally if enabled; otherwise, disable logging.
if LOGGING_ENABLED:
    logging.config.dictConfig(LOGGING_CONFIG)
else:
    logging.disable(logging.CRITICAL)
