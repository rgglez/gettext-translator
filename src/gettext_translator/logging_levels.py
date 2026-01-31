import logging

# -----------------------------------------------------------------------------


class LoggingLevels:
    @staticmethod
    def get(level: str):
        levels = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }
        return levels[level] if level in levels else logging.WARNING
    # get
# LoggingLevels
