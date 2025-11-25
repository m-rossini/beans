import sys
import argparse
import logging
import arcade
from config.loader import load_config
from beans.world import World
from beans.placement import RandomPlacementStrategy
from rendering.window import WorldWindow


def _configure_logging(level: str) -> None:
    """Configure logging based on provided level."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format='%(levelname)s - %(name)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def run(config_path: str | None = None):
    logger = logging.getLogger(__name__)
    logger.debug(f">>>>> Starting run with config_path={config_path}")
    
    if config_path:
        world_config, beans_config = load_config(config_path)
    else:
        from config.loader import DEFAULT_WORLD_CONFIG, DEFAULT_BEANS_CONFIG
        world_config = DEFAULT_WORLD_CONFIG
        beans_config = DEFAULT_BEANS_CONFIG
        logger.debug(">>>>> Using default configurations")

    world = World(config=world_config, beans_config=beans_config)
    window = WorldWindow(world)
    arcade.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Beans world simulation')
    parser.add_argument('config', nargs='?', default=None, help='Path to configuration file')
    parser.add_argument('--logging-level', default='INFO', help='Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    
    args = parser.parse_args()
    _configure_logging(args.logging_level)
    
    run(args.config)
