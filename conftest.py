"""Pytest configuration for beans project."""
import logging
import os


def pytest_configure(config):
    """Configure logging for pytest with per-module logging levels.
    
    Environment variables:
    - LOGGING_LEVEL: Global logging level (default: INFO)
    - DEBUG_MODULE: Specific module to set to DEBUG level (e.g., 'beans.world', 'config.loader')
    
    Example:
        LOGGING_LEVEL=INFO DEBUG_MODULE=beans.world pytest -v -s
    """
    global_level = os.getenv('LOGGING_LEVEL', 'INFO').upper()
    global_log_level = getattr(logging, global_level, logging.INFO)
    debug_module = os.getenv('DEBUG_MODULE', '').strip()
    
    logging.basicConfig(
        level=global_log_level,
        format='%(levelname)s - %(name)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set specific module to DEBUG if specified
    if debug_module:
        logger = logging.getLogger(debug_module)
        logger.setLevel(logging.DEBUG)

