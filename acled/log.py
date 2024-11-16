import logging
import os
import sys
from logging import Logger
from threading import current_thread
from multiprocessing import current_process


class AcledLogger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        log_level = os.getenv('LOG_LEVEL', 'WARNING').upper()
        self.logger: Logger = logging.getLogger("acled_logger")
        self.logger.setLevel(getattr(logging, log_level, logging.WARNING))

        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - '
            'Thread:%(threadName)s(Process:%(processName)s) - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def get_logger(self) -> Logger:
        return self.logger


# Usage
if __name__ == "__main__":
    logger = AcledLogger().get_logger()

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
