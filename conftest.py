"""Pytest configuration for beans project."""
import logging
import os


def pytest_configure(config):
    """Configure logging for pytest.
    
    Environment variables:
    - LOGGING_LEVEL: Global logging level (default: INFO)
    - LOG_FILE: File path to write logs to (optional, logs to console by default)
    
    Example:
        LOGGING_LEVEL=DEBUG LOG_FILE=test_debug.log pytest -v -s
    """
    logging_level = os.getenv('LOGGING_LEVEL', 'INFO').upper()
    log_file = os.getenv('LOG_FILE', '').strip() or None
    
    level = getattr(logging, logging_level, logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(levelname)s - %(name)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Console handler (always added)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (only if LOG_FILE is provided)
    if log_file:
        os.makedirs(os.path.dirname(log_file) or '.', exist_ok=True)
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

