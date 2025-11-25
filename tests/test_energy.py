import logging
from beans.bean import Bean, Sex
from beans.world import World
from config.loader import BeansConfig, WorldConfig
import pytest

logger = logging.getLogger(__name__)


def make_beans_config(**overrides) -> BeansConfig:
    return BeansConfig(max_bean_age=100, speed_min=-5, speed_max=5, **overrides)


def test_bean_initial_energy_from_config():
    cfg = make_beans_config(initial_energy=50.0)
    bean = Bean(config=cfg, id=1, sex=Sex.MALE)
    assert bean.energy == 50.0


def test_update_applies_gain_and_cost():
    cfg = make_beans_config(initial_energy=10.0, energy_gain_per_step=2.0, energy_cost_per_speed=1.0)
    bean = Bean(config=cfg, id=2, sex=Sex.FEMALE, speed=3.0)
    before = bean.energy
    result = bean.update(dt=1.0)
    energy_after = result["energy"]
    assert bean.energy == pytest.approx(before + 2.0 - 3.0)
    assert energy_after == pytest.approx(bean.energy)


def test_update_calls_energy_tick():
    cfg = make_beans_config(initial_energy=20.0, energy_gain_per_step=1.0, energy_cost_per_speed=0.5)
    bean = Bean(config=cfg, id=3, sex=Sex.FEMALE, speed=4.0)
    before = bean.energy
    result = bean.update(dt=2.0)
    energy_after = result["energy"]
    expected = before + 2 * 1.0 - abs(4.0) * 0.5 * 2.0
    assert bean.energy == pytest.approx(expected)
    assert energy_after == pytest.approx(bean.energy)


def test_world_records_dead_bean_with_reason():
    world_cfg = WorldConfig(
        male_sprite_color='blue',
        female_sprite_color='red',
        male_female_ratio=1.0,
        width=100,
        height=100,
        population_density=0.0,
        placement_strategy='random',
        population_estimator='density',
    )
    beans_cfg = make_beans_config(initial_energy=1.0, energy_gain_per_step=0.0, energy_cost_per_speed=1.0, initial_bean_size=5)
    world = World(config=world_cfg, beans_config=beans_cfg)
    world.beans = [Bean(config=beans_cfg, id=0, sex=Sex.MALE, speed=5.0)]
    world.step(dt=1.0)
    assert len(world.beans) == 0
    assert len(world.dead_beans) == 1
    assert world.dead_beans[0].reason == 'energy_depleted'
