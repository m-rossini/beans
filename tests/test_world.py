import logging
import arcade
from beans.world import World
from beans.bean import Bean, Sex
from rendering.window import WorldWindow
from config.loader import WorldConfig, BeansConfig

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


def test_world_window_title_displays_round_number():
    cfg = WorldConfig(male_sprite_color='blue', female_sprite_color='red', male_female_ratio=1.0, width=20, height=20, population_density=1.0, placement_strategy='random')
    bcfg = BeansConfig(max_bean_age=100, speed_min=-5, speed_max=5, initial_bean_size=10)
    world = World(config=cfg, beans_config=bcfg)
    window = WorldWindow(world)
    
    # After first on_update, round should be 2
    window.on_update(0.1)
    assert "round: 2" in window.title
    
    # After second on_update, round should be 3
    window.on_update(0.1)
    assert "round: 3" in window.title


def test_world_kills_beans_when_age_limit_reached():
    cfg = WorldConfig(
        male_sprite_color='blue',
        female_sprite_color='red',
        male_female_ratio=1.0,
        width=20,
        height=20,
        population_density=1.0,
        placement_strategy='random',
        max_age_years=1,
        rounds_per_year=12,
    )
    bcfg = BeansConfig(max_bean_age=100, speed_min=-5, speed_max=5, initial_bean_size=10)
    world = World(config=cfg, beans_config=bcfg)
    bean = Bean(config=bcfg, id=0, sex=Sex.MALE)
    world.beans = [bean]
    for _ in range(world.max_age_months):
        world.step(dt=1.0)

    assert bean not in world.beans
    assert any(record.reason == "max_age_reached" for record in world.dead_beans)
