import pytest

from beans.genetics import Gene, Genotype, age_speed_factor, genetic_max_age, genetic_max_speed, size_target
from beans.world import World
from config.loader import BeansConfig, WorldConfig
from src.beans.bean import BeanState
from src.beans.dynamics.bean_dynamics import BeanDynamics


def test_bean_dynamics_speed_calculation():
    config = BeansConfig(speed_min=0.1, speed_max=1.0, min_speed_factor=0.2)
    bean_state = BeanState(id=1, age=5, speed=1.0, energy=10.0, size=10.0, target_size=10.0, alive=True)
    # Provide dummy genotype and max_age for calculation
    genes = {
        Gene.METABOLISM_SPEED: 1.0,
        Gene.MAX_GENETIC_SPEED: 1.0,
        Gene.FAT_ACCUMULATION: 1.0,
        Gene.MAX_GENETIC_AGE: 1.0,
    }
    genotype = Genotype(genes=genes)
    dummy_max_age = 100
    dynamics = BeanDynamics(config)
    speed = dynamics.calculate_speed(bean_state,genotype, dummy_max_age)
    # Expected: vmax * age_factor * size_penalty, all factors = 1.0 except min_speed_factor
    # For age=5, max_age=100, min_speed_factor=0.2, vmax=1.0, size_penalty=1.0
    expected_age_factor = age_speed_factor(5, dummy_max_age, config.min_speed_factor)
    expected_speed = max(config.min_speed_factor, config.speed_max * expected_age_factor * 1.0)
    assert speed == expected_speed


def test_world_step_calculates_bean_speed_correctly():
    # Deterministic world creation using seed
    wcfg = WorldConfig(male_sprite_color="blue", female_sprite_color="red", male_female_ratio=1.0, width=20, height=20, population_density=1.0, placement_strategy="random", seed=42)
    bcfg = BeansConfig(speed_min=0.1, speed_max=1.0, min_speed_factor=0.2, energy_cost_per_speed=0.0, metabolism_base_burn=0.0, fat_gain_rate=0.0, fat_burn_rate=0.0, energy_gain_per_step=0.0, initial_bean_size=10)
    world = World(config=wcfg, beans_config=bcfg)
    assert len(world.beans) >= 1

    bean = world.beans[0]
    # prepare deterministic state: age placed in growth region
    state = bean.to_state()
    # Ensure target_size is consistent by computing target_size via public API
    target = size_target(5, bean.genotype, bcfg)
    state.store(age=5, size=target, energy=bcfg.initial_energy * 10.0, speed=0.0)
    bean.update_from_state(state)

    # Run step and assert speed matches expected value
    world.step(dt=1.0)

    max_age = genetic_max_age(bcfg, bean.genotype)
    vmax = genetic_max_speed(bcfg, bean.genotype)
    age_factor = age_speed_factor(5, max_age, bcfg.min_speed_factor)
    expected_speed = max(bcfg.min_speed_factor, vmax * age_factor)
    assert pytest.approx(expected_speed, rel=1e-6) == bean.speed


def test_world_min_speed_floor():
    # Use very small age where age_factor is 0 and ensures min floor
    wcfg = WorldConfig(male_sprite_color="blue", female_sprite_color="red", male_female_ratio=1.0, width=20, height=20, population_density=1.0, placement_strategy="random", seed=99)
    bcfg = BeansConfig(speed_min=0.05, speed_max=0.5, min_speed_factor=0.2, energy_cost_per_speed=0.0, metabolism_base_burn=0.0, fat_gain_rate=0.0, fat_burn_rate=0.0, energy_gain_per_step=0.0, initial_bean_size=10)
    world = World(config=wcfg, beans_config=bcfg)
    bean = world.beans[0]
    state = bean.to_state()
    target = size_target(0, bean.genotype, bcfg)
    state.store(age=0, size=target, energy=bcfg.initial_energy * 10.0, speed=0.0)
    bean.update_from_state(state)
    world.step(dt=1.0)
    assert bean.speed == pytest.approx(bcfg.min_speed_factor)


def test_bean_dynamics_size_speed_penalty_behaviour():
    """Behavioural test: ensure size deviations reduce calculated speed via public API.

    This avoids calling private methods directly and verifies the effective
    speed penalty by observing the public `calculate_speed` output.
    """
    cfg = BeansConfig(speed_min=0.0, speed_max=1.0, min_speed_factor=0.0, initial_bean_size=10)
    bd = BeanDynamics(cfg)

    # deterministic genotype and max age to ensure stable calculations
    genes = {
        Gene.METABOLISM_SPEED: 1.0,
        Gene.MAX_GENETIC_SPEED: 1.0,
        Gene.FAT_ACCUMULATION: 1.0,
        Gene.MAX_GENETIC_AGE: 1.0,
    }
    genotype = Genotype(genes=genes)
    dummy_max_age = 100

    # size equal to target -> baseline speed
    state = BeanState(id=1, age=5, speed=0.0, energy=10.0, size=10.0, target_size=10.0, alive=True)
    speed_target = bd.calculate_speed(state, genotype, dummy_max_age)
    assert speed_target > 0.0

    # significantly larger than target -> calculated speed is reduced
    state.store(size=100.0)
    speed_large = bd.calculate_speed(state, genotype, dummy_max_age)
    assert speed_large < speed_target

    # significantly smaller than target -> calculated speed is reduced
    state.store(size=1.0)
    speed_small = bd.calculate_speed(state, genotype, dummy_max_age)
    assert speed_small < speed_target
