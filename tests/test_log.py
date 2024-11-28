import pytest
import logging
import os
from io import StringIO
from acled.log import AcledLogger


@pytest.fixture
def reset_logger():
    # Reset the singleton instance before each test
    AcledLogger._instance = None
    yield
    # Clean up after each test
    AcledLogger._instance = None
    logging.getLogger("acled_logger").handlers = []


@pytest.fixture
def capture_logs():
    # Use a StringIO object to capture log output
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    logger = AcledLogger().get_logger()
    logger.addHandler(handler)
    logger.handlers = [handler]  # Remove default handler
    yield log_capture
    logger.removeHandler(handler)


def test_singleton_pattern(reset_logger):
    logger1 = AcledLogger()
    logger2 = AcledLogger()
    assert logger1 is logger2


def test_get_logger(reset_logger):
    logger = AcledLogger().get_logger()
    assert isinstance(logger, logging.Logger)
    assert logger.name == "acled_logger"


@pytest.mark.parametrize("log_level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
def test_log_level_setting(reset_logger, log_level):
    os.environ['LOG_LEVEL'] = log_level
    logger = AcledLogger().get_logger()
    assert logger.level == getattr(logging, log_level)


def test_default_log_level(reset_logger):
    if 'LOG_LEVEL' in os.environ:
        del os.environ['LOG_LEVEL']
    logger = AcledLogger().get_logger()
    assert logger.level == logging.WARNING


def test_invalid_log_level(reset_logger):
    os.environ['LOG_LEVEL'] = 'INVALID_LEVEL'
    logger = AcledLogger().get_logger()
    assert logger.level == logging.WARNING


def test_log_formatter(reset_logger):
    logger = AcledLogger().get_logger()
    handler = logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    assert isinstance(handler.formatter, logging.Formatter)
    expected_format = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - Thread:%(threadName)s(Process:%(processName)s) - %(message)s'
    assert handler.formatter._fmt == expected_format


# @pytest.mark.parametrize("log_method,log_level", [
#     ("debug", "DEBUG"),
#     ("info", "INFO"),
#     ("warning", "WARNING"),
#     ("error", "ERROR"),
#     ("critical", "CRITICAL"),
# ])
# def test_log_output(reset_logger, capture_logs, log_method, log_level):
#     os.environ['LOG_LEVEL'] = log_level
#     logger = AcledLogger().get_logger()
#     log_func = getattr(logger, log_method)
#     log_func("Test message")
#
#     output = capture_logs.getvalue()
#     assert log_level in output
#     assert "Test message" in output
#     assert "log.py" in output
#     assert "Thread:" in output
#     assert "Process:" in output


# def test_multiple_log_messages(reset_logger, capture_logs):
#     os.environ['LOG_LEVEL'] = 'DEBUG'
#     logger = AcledLogger().get_logger()
#
#     logger.debug("Debug message")
#     logger.info("Info message")
#     logger.warning("Warning message")
#     logger.error("Error message")
#     logger.critical("Critical message")
#
#     output = capture_logs.getvalue()
#     assert "DEBUG" in output and "Debug message" in output
#     assert "INFO" in output and "Info message" in output
#     assert "WARNING" in output and "Warning message" in output
#     assert "ERROR" in output and "Error message" in output
#     assert "CRITICAL" in output and "Critical message" in output


def test_logger_thread_safety(reset_logger):
    import threading

    def worker():
        logger = AcledLogger().get_logger()
        assert threading.current_thread().name in logger.handlers[0].formatter._fmt

    threads = [threading.Thread(target=worker) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    pytest.main()