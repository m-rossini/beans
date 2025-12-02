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


def test_update_applies_gain_and_cost(sample_genotype):
    cfg = make_beans_config(initial_energy=10.0, energy_gain_per_step=2.0, energy_cost_per_speed=1.0)
    phenotype = Phenotype(age=0.0, speed=3.0, energy=10.0, size=5.0, target_size=5.0)
    bean = Bean(config=cfg, id=2, sex=Sex.FEMALE, genotype=sample_genotype, phenotype=phenotype)
    before = bean.energy
    result = bean.update(dt=1.0)
    energy_after = result["phenotype"]["energy"]
    assert bean.energy == pytest.approx(before + 2.0 - 3.0)
    assert energy_after == pytest.approx(bean.energy)

def test_update_calls_energy_tick(sample_genotype):
    cfg = make_beans_config(initial_energy=20.0, energy_gain_per_step=1.0, energy_cost_per_speed=0.5)
    phenotype = Phenotype(age=0.0, speed=4.0, energy=20.0, size=5.0, target_size=5.0)
    bean = Bean(config=cfg, id=3, sex=Sex.FEMALE, genotype=sample_genotype, phenotype=phenotype)
    before = bean.energy
    initial_speed = bean.speed
    result = bean.update(dt=2.0)
    energy_after = result["phenotype"]["energy"]
    expected = before + (cfg.energy_gain_per_step) - (cfg.energy_cost_per_speed * initial_speed)
    assert bean.energy == pytest.approx(expected)
    assert energy_after == pytest.approx(bean.energy)


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
