import sys
import arcade
from config.loader import load_config
from beans.world import World
from beans.placement import RandomPlacementStrategy
from rendering.window import WorldWindow


def run(config_path: str | None = None):
    if config_path:
        world_config, beans_config = load_config(config_path)
    else:
        # Try to import defaults from loader if available
        from config.loader import DEFAULT_WORLD_CONFIG, DEFAULT_BEANS_CONFIG
        world_config = DEFAULT_WORLD_CONFIG
        beans_config = DEFAULT_BEANS_CONFIG

    world = World(config=world_config, beans_config=beans_config)
    window = WorldWindow(world)
    arcade.run()


if __name__ == '__main__':
    cfg = sys.argv[1] if len(sys.argv) > 1 else None
    run(cfg)
