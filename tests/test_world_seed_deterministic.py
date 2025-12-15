import pytest

from beans.genetics import (
    age_speed_factor,
    genetic_max_age,
    genetic_max_speed,
    size_target,
)
from beans.world import World
from config.loader import BeansConfig, EnvironmentConfig, WorldConfig


def make_seeded_world(
    seed: int,
    width: int = 20,
    height: int = 20,
    density: float = 1.0,
    speed_min=0.1,
    speed_max=1.0,
    min_speed_factor=0.2,
):
    wcfg = WorldConfig(
        male_sprite_color="blue",
        female_sprite_color="red",
        male_female_ratio=1.0,
        width=width,
        height=height,
        population_density=density,
        placement_strategy="random",
        seed=seed,
    )
    bcfg = BeansConfig(
        speed_min=speed_min,
        speed_max=speed_max,
        min_speed_factor=min_speed_factor,
        energy_cost_per_speed=0.0,
        metabolism_base_burn=0.0,
        fat_gain_rate=0.0,
        fat_burn_rate=0.0,
        energy_gain_per_step=0.0,
        initial_bean_size=10,
    )
    env_cfg = EnvironmentConfig()
    return World(config=wcfg, beans_config=bcfg, env_config=env_cfg), bcfg


def assert_worlds_same_initial(world_a: World, world_b: World):
    assert len(world_a.beans) == len(world_b.beans)
    for a, b in zip(world_a.beans, world_b.beans):
        # Compare genotype gene dicts
        assert a.genotype.genes == b.genotype.genes
        # Compare initial phenotypes via public to_state()
        sa = a.to_state()
        sb = b.to_state()
        assert sa.age == sb.age
        assert sa.size == sb.size
        assert sa.energy == sb.energy


def test_world_seed_produces_deterministic_genotypes_and_phenotypes():
    world_a, _ = make_seeded_world(seed=42)
    world_b, _ = make_seeded_world(seed=42)
    assert_worlds_same_initial(world_a, world_b)


def test_world_seed_repeatable_speed_after_step():
    world_a, bcfg = make_seeded_world(seed=99)
    world_b, _ = make_seeded_world(seed=99)

    assert len(world_a.beans) >= 1
    bean_a = world_a.beans[0]
    bean_b = world_b.beans[0]

    # Prepare deterministic equal states
    state_a = bean_a.to_state()
    state_b = bean_b.to_state()

    target = size_target(5, bean_a.genotype, bcfg)
    state_a.store(age=5, size=target, energy=bcfg.initial_energy * 10.0, speed=0.0)
    state_b.store(age=5, size=target, energy=bcfg.initial_energy * 10.0, speed=0.0)
    bean_a.update_from_state(state_a)
    bean_b.update_from_state(state_b)

    world_a.step(dt=1.0)
    world_b.step(dt=1.0)

    assert pytest.approx(bean_a.speed, rel=1e-6) == bean_b.speed
    # And make sure it matches the expected public-calculated speed
    max_age = genetic_max_age(bcfg, bean_a.genotype)
    vmax = genetic_max_speed(bcfg, bean_a.genotype)
    age_factor = age_speed_factor(5, max_age, bcfg.min_speed_factor)
    expected_speed = max(bcfg.min_speed_factor, vmax * age_factor)
    assert pytest.approx(expected_speed, rel=1e-6) == bean_a.speed
