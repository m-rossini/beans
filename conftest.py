"""Pytest configuration for beans project."""
import logging
import os


def pytest_configure(config):
    """Configure logging for pytest."""
    logging_level = os.getenv('LOGGING_LEVEL', 'INFO').upper()
    level = getattr(logging, logging_level, logging.INFO)
    
    logging.basicConfig(
        level=level,
        format='%(levelname)s - %(name)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
