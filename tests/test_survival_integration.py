from beans.world import World
from config.loader import BeansConfig, EnvironmentConfig, WorldConfig


def make_world(seed: int = 42) -> tuple[World, BeansConfig]:
    wcfg = WorldConfig(
        male_sprite_color="blue",
        female_sprite_color="red",
        male_female_ratio=1.0,
        width=20,
        height=20,
        population_density=1.0,
        placement_strategy="random",
        seed=seed,
    )
    # Ensure no automatic energy intake to exercise starvation behavior deterministically
    bcfg = BeansConfig(speed_min=-1.0, speed_max=1.0, energy_gain_per_step=0.0)
    env_cfg = EnvironmentConfig()
    return World(config=wcfg, beans_config=bcfg, env_config=env_cfg), bcfg


def test_starvation_depletes_fat_and_survives_until_min_size():
    world, bcfg = make_world(seed=123)
    assert len(world.beans) >= 1
    bean = world.beans[0]

    # Force energy to zero and ensure size is above min_bean_size
    state = bean.to_state()
    state.store(energy=0.0, size=bcfg.min_bean_size + 2.0)
    bean.update_from_state(state)

    world.step(dt=1.0)

    # Expect bean to still be alive and size to have decreased (starvation draws on fat)
    assert bean in world.beans, "Bean should survive while drawing on fat"
    assert bean.size < bcfg.min_bean_size + 2.0, "Bean size should have decreased due to starvation"


def test_death_when_fat_depleted_and_energy_zero():
    world, bcfg = make_world(seed=124)
    assert len(world.beans) >= 1
    bean = world.beans[0]

    # Force energy zero and size at or below min_bean_size to trigger starvation death
    state = bean.to_state()
    state.store(energy=0.0, size=bcfg.min_bean_size)
    bean.update_from_state(state)

    world.step(dt=1.0)

    # Expect bean to be removed and recorded as dead for starvation
    assert bean not in world.beans, "Bean should die when fat is depleted"
    # Use canonical reason string used across the codebase
    assert any(rec.bean == bean and rec.reason == "energy_depleted" for rec in world.dead_beans), "Dead reason should be energy_depleted"


def test_age_death():
    world, bcfg = make_world(seed=125)
    assert len(world.beans) >= 1
    bean = world.beans[0]

    # Set bean age to maximum allowed
    max_age = bean._max_age
    state = bean.to_state()
    state.store(age=max_age + 1)
    bean.update_from_state(state)

    world.step(dt=1.0)

    assert bean not in world.beans
    # Use canonical reason string used across the codebase
    assert any(rec.bean == bean and rec.reason == "max_age_reached" for rec in world.dead_beans)


def test_obesity_probabilistic_death_seeded():
    world, bcfg = make_world(seed=42)
    assert len(world.beans) >= 1
    bean = world.beans[0]

    # Make bean extremely large to be above any obesity threshold
    state = bean.to_state()
    state.store(size=bcfg.max_bean_size * 10)
    bean.update_from_state(state)

    # Enable deterministic obesity death for this test: set config so threshold is low and probability is 1.0
    bcfg.obesity_death_probability = 1.0
    bcfg.obesity_threshold_factor = 0.5

    # Make bean extremely large to be above the obesity threshold
    state = bean.to_state()
    state.store(size=bcfg.max_bean_size * 2)
    bean.update_from_state(state)

    world.step(dt=1.0)

    # Expect the bean to be removed and recorded with obesity reason
    assert bean not in world.beans
    assert any(rec.bean == bean and rec.reason == "obesity" for rec in world.dead_beans)


def test_starvation_depletion_rate_respected():
    # TDD: verify starvation depletion uses configured base and multiplier
    world, bcfg = make_world(seed=314)
    assert len(world.beans) >= 1
    bean = world.beans[0]

    # Configure depletion: base 1.0, multiplier 2.0 so expected depletion is 2.0 units
    bcfg.starvation_base_depletion = 1.0
    bcfg.starvation_depletion_multiplier = 2.0
    # Disable energy-system-driven fat burning for deterministic check
    bcfg.fat_burn_rate = 0.0
    bcfg.metabolism_base_burn = 0.0

    # Force energy zero and set a size so drawing fat is possible
    state = bean.to_state()
    initial_size = bcfg.min_bean_size + 3.0
    state.store(energy=0.0, size=initial_size)
    bean.update_from_state(state)

    world.step(dt=1.0)

    # Bean should survive and size should be reduced by base * multiplier
    assert bean in world.beans
    expected_depletion = bcfg.starvation_base_depletion * bcfg.starvation_depletion_multiplier
    assert round(bean.size, 6) == round(initial_size - expected_depletion, 6)


def test_external_event_hook_noop():
    # smoke test: running a world step without registered external event handlers should do nothing harmful
    world, bcfg = make_world(seed=999)
    initial_beans = list(world.beans)

    world.step(dt=1.0)

    # Ensure no unexpected deaths occurred when nothing external is registered
    assert len(world.dead_beans) == 0
    assert len(world.beans) == len(initial_beans)
