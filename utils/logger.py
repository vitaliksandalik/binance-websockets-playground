import logging
from colorlog import ColoredFormatter


class Logger:
    def __init__(self, logger_name, log_file):
        self._log = logging.getLogger(logger_name)
        self._log.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)

        colored_formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
        console_handler.setFormatter(colored_formatter)

        self._log.addHandler(console_handler)
        self._log.addHandler(file_handler)

    def __getattr__(self, name):
        return getattr(self._log, name)
