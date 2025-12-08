import logging
from beans.bean import Bean, Sex
from beans.genetics import Gene, Genotype, Phenotype, create_random_genotype, create_phenotype
from beans.world import World
from config.loader import BeansConfig, WorldConfig
import pytest

logger = logging.getLogger(__name__)


@pytest.fixture
def sample_genotype() -> Genotype:
    return Genotype(genes={
        Gene.METABOLISM_SPEED: 0.5,
        Gene.MAX_GENETIC_SPEED: 0.5,
        Gene.FAT_ACCUMULATION: 0.5,
        Gene.MAX_GENETIC_AGE: 0.5,
    })


@pytest.fixture
def sample_phenotype() -> Phenotype:
    """Create a phenotype for testing with controlled values."""
    return Phenotype(age=0.0, speed=5.0, energy=100.0, size=5.0, target_size=5.0)


def make_beans_config(**overrides) -> BeansConfig:
    return BeansConfig(speed_min=-5, speed_max=5, max_age_rounds=100, **overrides)


def test_bean_initial_energy_from_config(sample_genotype):
    cfg = make_beans_config(initial_energy=50.0)
    phenotype = Phenotype(age=0.0, speed=5.0, energy=50.0, size=5.0, target_size=5.0)
    bean = Bean(config=cfg, id=1, sex=Sex.MALE, genotype=sample_genotype, phenotype=phenotype)
    assert bean.energy == 50.0


class TestBeanSurvival:
    """Tests for Bean survival methods."""

    def test_can_survive_age_true_when_below_max(self, sample_genotype):
        """Bean can survive when age is below genetic max age."""
        cfg = make_beans_config()
        phenotype = Phenotype(age=10.0, speed=5.0, energy=100.0, size=5.0, target_size=5.0)
        bean = Bean(config=cfg, id=1, sex=Sex.MALE, genotype=sample_genotype, phenotype=phenotype)
        assert bean.can_survive_age() is True

    def test_can_survive_age_false_when_at_max(self, sample_genotype):
        """Bean cannot survive when age equals genetic max age."""
        cfg = make_beans_config()
        # Gene value 0.5 means max age = 100 * 0.5 = 50 rounds
        phenotype = Phenotype(age=50.0, speed=5.0, energy=100.0, size=5.0, target_size=5.0)
        bean = Bean(config=cfg, id=1, sex=Sex.MALE, genotype=sample_genotype, phenotype=phenotype)
        assert bean.can_survive_age() is False

    def test_can_survive_age_false_when_above_max(self, sample_genotype):
        """Bean cannot survive when age exceeds genetic max age."""
        cfg = make_beans_config()
        phenotype = Phenotype(age=60.0, speed=5.0, energy=100.0, size=5.0, target_size=5.0)
        bean = Bean(config=cfg, id=1, sex=Sex.MALE, genotype=sample_genotype, phenotype=phenotype)
        assert bean.can_survive_age() is False

    def test_survive_returns_true_when_healthy(self, sample_genotype):
        """survive() returns True when bean has energy and is young enough."""
        cfg = make_beans_config()
        phenotype = Phenotype(age=10.0, speed=5.0, energy=50.0, size=5.0, target_size=5.0)
        bean = Bean(config=cfg, id=1, sex=Sex.MALE, genotype=sample_genotype, phenotype=phenotype)
        alive, reason = bean.survive()
        assert alive is True
        assert reason is None

    def test_survive_returns_false_with_reason_when_too_old(self, sample_genotype):
        """survive() returns False with reason when bean exceeds max age."""
        cfg = make_beans_config()
        phenotype = Phenotype(age=60.0, speed=5.0, energy=50.0, size=5.0, target_size=5.0)
        bean = Bean(config=cfg, id=1, sex=Sex.MALE, genotype=sample_genotype, phenotype=phenotype)
        alive, reason = bean.survive()
        assert alive is False
        assert reason == "max_age_reached"

    def test_survive_returns_false_with_reason_when_no_energy(self, sample_genotype):
        """survive() returns False with reason when energy is depleted."""
        cfg = make_beans_config()
        phenotype = Phenotype(age=10.0, speed=5.0, energy=0.0, size=5.0, target_size=5.0)
        bean = Bean(config=cfg, id=1, sex=Sex.MALE, genotype=sample_genotype, phenotype=phenotype)
        alive, reason = bean.survive()
        assert alive is False
        assert reason == "energy_depleted"

    def test_survive_age_takes_priority_over_energy(self, sample_genotype):
        """When both conditions fail, age death reason takes priority."""
        cfg = make_beans_config()
        phenotype = Phenotype(age=60.0, speed=5.0, energy=0.0, size=5.0, target_size=5.0)
        bean = Bean(config=cfg, id=1, sex=Sex.MALE, genotype=sample_genotype, phenotype=phenotype)
        alive, reason = bean.survive()
        assert alive is False
        assert reason == "max_age_reached"


class TestAgeEnergyEfficiency:
    """Tests for age_energy_efficiency function in genetics."""

    def test_newborn_has_minimum_efficiency(self, sample_genotype):
        """At age=0, efficiency equals min_energy_efficiency from config."""
        from beans.genetics import age_energy_efficiency
        cfg = make_beans_config(min_energy_efficiency=0.3)
        efficiency = age_energy_efficiency(age=0.0, max_age=100.0, min_efficiency=cfg.min_energy_efficiency)
        assert efficiency == pytest.approx(0.3)

    def test_midlife_has_peak_efficiency(self, sample_genotype):
        """At mid-life, efficiency is near or at 1.0 (peak)."""
        from beans.genetics import age_energy_efficiency
        cfg = make_beans_config(min_energy_efficiency=0.3)
        # Mid-life at about 25% of max age (similar to age_speed_factor peak)
        efficiency = age_energy_efficiency(age=25.0, max_age=100.0, min_efficiency=cfg.min_energy_efficiency)
        assert efficiency > 0.5  # Should be higher than minimum

    def test_old_age_has_reduced_efficiency(self, sample_genotype):
        """At old age, efficiency declines but stays above minimum."""
        from beans.genetics import age_energy_efficiency
        cfg = make_beans_config(min_energy_efficiency=0.3)
        efficiency = age_energy_efficiency(age=95.0, max_age=100.0, min_efficiency=cfg.min_energy_efficiency)
        assert efficiency >= 0.3  # Never below floor
        assert efficiency < 1.0   # But reduced from peak

    def test_efficiency_never_below_minimum(self, sample_genotype):
        """Efficiency never falls below min_energy_efficiency."""
        from beans.genetics import age_energy_efficiency
        min_eff = 0.3
        for age in [0, 10, 50, 90, 99, 100]:
            efficiency = age_energy_efficiency(age=float(age), max_age=100.0, min_efficiency=min_eff)
            assert efficiency >= min_eff


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
    genotype = create_random_genotype()
    phenotype = Phenotype(age=0.0, speed=5.0, energy=1.0, size=5.0, target_size=5.0)
    world.beans = [Bean(config=beans_cfg, id=0, sex=Sex.MALE, genotype=genotype, phenotype=phenotype)]
    world.step(dt=1.0)
    assert len(world.beans) == 0
    assert len(world.dead_beans) == 1
    assert world.dead_beans[0].reason == 'energy_depleted'
