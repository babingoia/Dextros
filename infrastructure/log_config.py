import logging
import os
from typing import Optional

try:
    import colorama
    colorama.init(autoreset=True)
except Exception:
    colorama = None

# Simple ANSI color codes
_COLORS = {
    "grey": "\x1b[90m",
    "red": "\x1b[31m",
    "green": "\x1b[32m",
    "yellow": "\x1b[33m",
    "blue": "\x1b[34m",
    "magenta": "\x1b[35m",
    "cyan": "\x1b[36m",
    "white": "\x1b[37m",
    "reset": "\x1b[0m",
}

_LEVEL_COLORS = {
    "DEBUG": _COLORS["cyan"],
    "INFO": _COLORS["green"],
    "WARNING": _COLORS["yellow"],
    "ERROR": _COLORS["red"],
    "CRITICAL": _COLORS["magenta"],
}

_FIELD_COLORS = {
    "time": _COLORS["blue"],
    "name": _COLORS["magenta"],
    "message": _COLORS["reset"],
}


DATE_FORMAT = "%Y/%m/%d | %H:%M:%S"
MESSAGE_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"


class ColoredFormatter(logging.Formatter):
    """Formatter that colors individual fields and varies message color by level.

    Use only on console handlers. File handlers should use a plain formatter.
    """

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None):
        super().__init__(fmt=fmt, datefmt=datefmt)


    def format(self, record: logging.LogRecord) -> str:
        ts = self.formatTime(record, self.datefmt) if self.datefmt else self.formatTime(record, DATE_FORMAT)
        ts_colored = f"{_FIELD_COLORS['time']}{ts}{_COLORS['reset']}"

        level = record.levelname
        level_color = _LEVEL_COLORS.get(level, _COLORS["white"])
        level_colored = f"{level_color}{level}{_COLORS['reset']}"

        name_colored = f"{_FIELD_COLORS['name']}{record.name}{_COLORS['reset']}"

        msg_color = _FIELD_COLORS.get("message", _COLORS["reset"])
        message = record.getMessage()
        message_colored = f"{msg_color}{message}{_COLORS['reset']}"

        return f"[{ts_colored}] [{name_colored}] [{level_colored}]: {message_colored}"


def configure_logging(console_level: int = logging.INFO) -> None:
    """Configure the root logger with a colored console handler.

    Call this once at application startup. File handler is added later
    via `add_file_handler` so the file can live in the app's runtime dir.
    """

    root = logging.getLogger()
    root.setLevel(console_level)

    # avoid duplicate handlers if reconfiguring
    for h in list(root.handlers):
        root.removeHandler(h)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(ColoredFormatter(datefmt=DATE_FORMAT))
    root.addHandler(console_handler)


def add_file_handler(logs_dir: str, filename: str = "app.log", level: int = logging.INFO) -> logging.Handler:
    """Create logs directory and add a plain FileHandler to the root logger.

    Returns the handler so callers can keep a reference (for removal/close).
    """
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, filename)

    fh = logging.FileHandler(log_file, mode="w")
    fh.setLevel(level)
    plain_fmt = logging.Formatter(MESSAGE_FORMAT, datefmt=DATE_FORMAT)
    fh.setFormatter(plain_fmt)

    logging.getLogger().addHandler(fh)
    return fh


def get_logger(name: str):
    return logging.getLogger(name)
