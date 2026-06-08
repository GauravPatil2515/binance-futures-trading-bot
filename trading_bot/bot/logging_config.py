"""Logging configuration — call setup_logging() once at process start."""
import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR  = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "trading_bot.log")

_CONFIGURED = False   # guard against double-configuration


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure the 'trading_bot' logger with console (WARNING+) and rotating file (DEBUG+).

    Safe to call multiple times — only configures once per process.
    """
    global _CONFIGURED
    logger = logging.getLogger("trading_bot")

    if _CONFIGURED:
        return logger

    os.makedirs(LOG_DIR, exist_ok=True)
    logger.setLevel(logging.DEBUG)   # handlers filter to their own levels

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console — WARNING and above only (keeps terminal clean)
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(fmt)

    # File — DEBUG and above (full audit trail, rotates at 5 MB)
    fh = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.propagate = False   # don't bubble up to root logger

    _CONFIGURED = True
    return logger
