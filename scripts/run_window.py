import argparse
import logging
import os

import arcade

from beans.world import World
from config.loader import load_config
from rendering.window import WorldWindow


def _configure_logging(level: str, log_file: str | None = None) -> None:
    """Configure logging based on provided level.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to

    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        "%(levelname)s - %(name)s - %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Console handler (always added)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (only if log_file is provided)
    if log_file:
        os.makedirs(os.path.dirname(log_file) or ".", exist_ok=True)
        file_handler = logging.FileHandler(log_file, mode="w")
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        root_logger.info(f"Logging to file: {log_file}")


def run(config_path: str | None = None):
    logger = logging.getLogger(__name__)
    logger.debug(f">>>>> Starting run with config_path={config_path}")

    if config_path:
        world_config, beans_config = load_config(config_path)
    else:
        from config.loader import DEFAULT_BEANS_CONFIG, DEFAULT_WORLD_CONFIG
        world_config = DEFAULT_WORLD_CONFIG
        beans_config = DEFAULT_BEANS_CONFIG
        logger.debug(">>>>> Using default configurations")

    world = World(config=world_config, beans_config=beans_config)
    window = WorldWindow(world)
    arcade.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Beans world simulation")
    parser.add_argument("config", nargs="?", default=None, help="Path to configuration file")
    parser.add_argument("--logging-level", default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    parser.add_argument("--log-file", default=None, help="Log file path (logs to console by default)")

    args = parser.parse_args()
    _configure_logging(args.logging_level, args.log_file)

    run(args.config)

