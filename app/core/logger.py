"""Logger."""

import functools
import logging

DEFAULT_LOGGER_NAMESPACE = "am-crm-service"


# This format will show exactly from where the log called
# <Module>::<Function>:<Line> => <Log Message>
LOGGING_FORMAT = (
    "%(levelname)s: \t  %(asctime)s "
    "%(module)s::%(funcName)s::%(lineno)s "
    "=> %(message)s"
)


@functools.lru_cache(maxsize=1)
class ColorFormatter(logging.Formatter):
    """Change logging formatter that adds color to log messages.

    This coloring will only be used in the local environment.
    The only reason for using it is to improve readability in the terminal.
    """

    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
    RESET_SEQ = "\033[0m"
    COLOR_SEQ = "\033[1;%dm"
    COLORS = {
        "WARNING": YELLOW,
        "INFO": GREEN,
        "DEBUG": BLUE,
        "CRITICAL": MAGENTA,
        "ERROR": RED,
    }

    def format(self, record):
        """Format the log message with color based on the log level."""
        levelname = record.levelname
        if levelname in self.COLORS:
            color_code = self.COLOR_SEQ % (30 + self.COLORS[levelname])
            message = super().format(record)
            return color_code + message + self.RESET_SEQ
        return super().format(record)


@functools.lru_cache(maxsize=1)
def get_logger(namespace: str = DEFAULT_LOGGER_NAMESPACE) -> logging.Logger:
    """Return a logger instance configured.

    Args:
    ----
        namespace: The namespace to use for the logger.
                    Defaults to "member-app-core".

    Returns:
    -------
        A logger instance configured for the specified namespace with INFO
        level.

    """
    # Create a new logger instance with the specified namespace
    logger = logging.getLogger(namespace)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = ColorFormatter(LOGGING_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
