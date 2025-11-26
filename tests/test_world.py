import logging
from beans.world import World
from config.loader import WorldConfig, BeansConfig
from beans.placement import RandomPlacementStrategy

logger = logging.getLogger(__name__)


def test_world_initialize_counts_by_density():
    cfg = WorldConfig(male_sprite_color='blue', female_sprite_color='red', male_female_ratio=1.0, width=20, height=20, population_density=1.0, placement_strategy='random')
    bcfg = BeansConfig(max_bean_age=100, speed_min=-5, speed_max=5, initial_bean_size=10)
    w = World(config=cfg, beans_config=bcfg)
    assert len(w.beans) == 4


def test_world_uses_config_dimensions_by_default():
    cfg = WorldConfig(male_sprite_color='blue', female_sprite_color='red', male_female_ratio=1.0, width=20, height=20, population_density=1.0, placement_strategy='random')
    bcfg = BeansConfig(max_bean_age=100, speed_min=-5, speed_max=5, initial_bean_size=10)
    w = World(config=cfg, beans_config=bcfg)
    assert w.width == cfg.width
    assert w.height == cfg.height
