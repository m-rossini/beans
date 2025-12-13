import logging
from beans.bean import Bean, Sex
from beans.genetics import create_phenotype, create_random_genotype
from beans.world import World
from config.loader import BeansConfig, WorldConfig
from rendering.window import WorldWindow
from beans.dynamics.bean_dynamics import BeanDynamics
logger = logging.getLogger(__name__)


def test_world_initialize_counts_by_density():
    cfg = WorldConfig(male_sprite_color="blue", female_sprite_color="red", male_female_ratio=1.0, width=20, height=20, population_density=1.0, placement_strategy="random")
    bcfg = BeansConfig(speed_min=-5, speed_max=5, max_age_rounds=100, initial_bean_size=10)
    w = World(config=cfg, beans_config=bcfg)
    assert len(w.beans) == 4


def test_world_uses_config_dimensions_by_default():
    cfg = WorldConfig(male_sprite_color="blue", female_sprite_color="red", male_female_ratio=1.0, width=20, height=20, population_density=1.0, placement_strategy="random")
    bcfg = BeansConfig(speed_min=-5, speed_max=5, max_age_rounds=100, initial_bean_size=10)
    w = World(config=cfg, beans_config=bcfg)
    assert w.width == cfg.width
    assert w.height == cfg.height


def test_world_window_title_displays_round_number():
    cfg = WorldConfig(male_sprite_color="blue", female_sprite_color="red", male_female_ratio=1.0, width=200, height=200, population_density=0.1, placement_strategy="random")
    bcfg = BeansConfig(speed_min=-5, speed_max=5, max_age_rounds=100, initial_bean_size=10)
    world = World(config=cfg, beans_config=bcfg)
    window = WorldWindow(world)
    # Patch bean_dynamics to use the first bean's genotype and max_age
    if world.beans:
        bean = world.beans[0]
        world.bean_dynamics = BeanDynamics(bcfg, bean.genotype, bean._max_age)

    # After first on_update, round should be 2
    window.on_update(0.1)
    assert "round: 2" in window.title

    # After second on_update, round should be 3
    window.on_update(0.1)
    assert "round: 3" in window.title


def test_world_kills_beans_when_age_limit_reached():
    cfg = WorldConfig(
        male_sprite_color="blue",
        female_sprite_color="red",
        male_female_ratio=1.0,
        width=20,
        height=20,
        population_density=1.0,
        placement_strategy="random",
        max_age_years=1,
        rounds_per_year=12,
    )
    bcfg = BeansConfig(speed_min=-5, speed_max=5, max_age_rounds=12, initial_bean_size=10)
    world = World(config=cfg, beans_config=bcfg)
    genotype = create_random_genotype()
    phenotype = create_phenotype(bcfg, genotype)
    bean = Bean(config=bcfg, id=0, sex=Sex.MALE, genotype=genotype, phenotype=phenotype)
    world.beans = [bean]
    world.bean_dynamics = BeanDynamics(bcfg, genotype, bean._max_age)
    for _ in range(bcfg.max_age_rounds):
        world.step(dt=1.0)

    assert bean not in world.beans
    assert any(record.reason == "max_age_reached" for record in world.dead_beans)


class TestWorldEnvironmentStubs:
    """Tests for world environment stubs (energy intake and temperature)."""

    def test_world_get_energy_intake_returns_default(self):
        """World.get_energy_intake() should return DEFAULT_ENERGY_INTAKE (1.0)."""
        cfg = WorldConfig(
            male_sprite_color="blue",
            female_sprite_color="red",
            male_female_ratio=1.0,
            width=20,
            height=20,
            population_density=0.0,
            placement_strategy="random",
        )
        bcfg = BeansConfig(speed_min=-5, speed_max=5)
        world = World(config=cfg, beans_config=bcfg)

        assert world.get_energy_intake() == 1.0

    def test_world_get_temperature_returns_default(self):
        """World.get_temperature() should return DEFAULT_TEMPERATURE (1.0)."""
        cfg = WorldConfig(
            male_sprite_color="blue",
            female_sprite_color="red",
            male_female_ratio=1.0,
            width=20,
            height=20,
            population_density=0.0,
            placement_strategy="random",
        )
        bcfg = BeansConfig(speed_min=-5, speed_max=5)
        world = World(config=cfg, beans_config=bcfg)

        assert world.get_temperature() == 1.0
