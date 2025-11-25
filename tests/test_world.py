import logging
from beans.world import World
from config.loader import WorldConfig, BeansConfig
from beans.placement import GridPlacementStrategy, ClusteredPlacementStrategy, RandomPlacementStrategy

logger = logging.getLogger(__name__)


def test_grid_placement_strategy_positions():
    strategy = GridPlacementStrategy()
    positions = strategy.place(4, width=20, height=20, size=10)
    assert len(positions) == 4


def test_clustered_placement_strategy_clusters():
    strategy = ClusteredPlacementStrategy()
    positions = strategy.place(10, width=100, height=100, size=10)
    assert len(positions) == 10
    close_pairs = 0
    for i in range(len(positions)):
        for j in range(i+1, len(positions)):
            dx = positions[i][0] - positions[j][0]
            dy = positions[i][1] - positions[j][1]
            if (dx*dx + dy*dy) ** 0.5 < 15:
                close_pairs += 1
    assert close_pairs >= 1


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
