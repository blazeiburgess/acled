import pytest
import os
import logging
from unittest.mock import patch, MagicMock
from acled.log import AcledLogger

def test_singleton_pattern():
    """Test that AcledLogger follows the singleton pattern."""
    logger1 = AcledLogger()
    logger2 = AcledLogger()
    assert logger1 is logger2

def test_get_logger():
    """Test that get_logger returns a Logger instance."""
    logger = AcledLogger().get_logger()
    assert isinstance(logger, logging.Logger)
    assert logger.name == "acled_logger"

def test_default_log_level():
    """Test that the default log level is WARNING."""
    with patch.dict(os.environ, {}, clear=True):  # Clear environment variables
        # Reset the singleton instance to force reinitialization
        AcledLogger._instance = None
        logger = AcledLogger().get_logger()
        assert logger.level == logging.WARNING

def test_custom_log_level():
    """Test that the log level can be customized via environment variable."""
    with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}, clear=True):
        # Reset the singleton instance to force reinitialization
        AcledLogger._instance = None
        logger = AcledLogger().get_logger()
        assert logger.level == logging.DEBUG

def test_invalid_log_level():
    """Test that an invalid log level defaults to WARNING."""
    with patch.dict(os.environ, {"LOG_LEVEL": "INVALID"}, clear=True):
        # Reset the singleton instance to force reinitialization
        AcledLogger._instance = None
        logger = AcledLogger().get_logger()
        assert logger.level == logging.WARNING

def test_logger_handler():
    """Test that the logger has a StreamHandler."""
    logger = AcledLogger().get_logger()
    assert len(logger.handlers) > 0
    assert isinstance(logger.handlers[0], logging.StreamHandler)

def test_logger_formatter():
    """Test that the logger has the correct formatter."""
    logger = AcledLogger().get_logger()
    formatter = logger.handlers[0].formatter
    assert '%(asctime)s' in formatter._fmt
    assert '%(levelname)s' in formatter._fmt
    assert '%(filename)s:%(lineno)d' in formatter._fmt
    assert 'Thread:%(threadName)s' in formatter._fmt
    assert 'Process:%(processName)s' in formatter._fmt
    assert '%(message)s' in formatter._fmt

def test_logging_messages():
    """Test that messages can be logged at different levels."""
    # Reset the singleton instance to force reinitialization
    AcledLogger._instance = None
    
    # Mock the logger to capture log messages
    mock_logger = MagicMock()
    with patch('logging.getLogger', return_value=mock_logger):
        logger = AcledLogger().get_logger()
        
        # Log messages at different levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        # Verify that the logger methods were called
        mock_logger.debug.assert_called_once_with("Debug message")
        mock_logger.info.assert_called_once_with("Info message")
        mock_logger.warning.assert_called_once_with("Warning message")
        mock_logger.error.assert_called_once_with("Error message")
        mock_logger.critical.assert_called_once_with("Critical message")