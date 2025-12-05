import random
import logging
import pytest

from pydantic import ValidationError

from beans.bean import Bean, Sex
from beans.genetics import Gene, Genotype, Phenotype, create_random_genotype
from config.loader import BeansConfig
from beans.placement import RandomPlacementStrategy

logger = logging.getLogger(__name__)


@pytest.fixture
def sample_genotype() -> Genotype:
    """Create a valid genotype for testing."""
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


@pytest.fixture
def beans_config() -> BeansConfig:
    return BeansConfig(speed_min=-5, speed_max=5, max_age_rounds=100)


def test_create_bean_default_values(beans_config, sample_genotype, sample_phenotype):
    b = Bean(config=beans_config, id=1, sex=Sex.MALE, genotype=sample_genotype, phenotype=sample_phenotype)
    assert b.age == 0.0
    assert b.genotype == sample_genotype


def test_bean_update_increments_age(beans_config, sample_genotype):
    phenotype = Phenotype(age=0.0, speed=10.0, energy=100.0, size=5.0, target_size=5.0)
    b = Bean(config=beans_config, id=2, sex=Sex.FEMALE, genotype=sample_genotype, phenotype=phenotype)
    initial_age = b.age
    b.update(dt=1.0)
    assert b.age == initial_age + 1.0


def test_bean_mutable_fields(beans_config, sample_genotype, sample_phenotype):
    b = Bean(config=beans_config, id=3, sex=Sex.FEMALE, genotype=sample_genotype, phenotype=sample_phenotype)
    # Phenotype changes through update cycle, not direct assignment
    initial_age = b.age
    b.update(dt=1.0)
    assert b.age == initial_age + 1.0


def test_random_placement_within_bounds():
    strategy = RandomPlacementStrategy()
    positions = strategy.place(5, width=100, height=100, size=10)
    assert len(positions) == 5
    for x, y in positions:
        assert 0.0 <= x <= 100.0
        assert 0.0 <= y <= 100.0


# Genotype tests

def test_create_random_genotype_has_all_genes():
    genotype = create_random_genotype()
    for gene in Gene:
        assert gene in genotype.genes


def test_create_random_genotype_values_in_range():
    genotype = create_random_genotype()
    for gene in Gene:
        assert gene.min <= genotype.genes[gene] <= gene.max


def test_genotype_is_immutable():
    genotype = create_random_genotype()
    with pytest.raises(ValidationError):
        genotype.genes = {}


def test_genotype_missing_gene_raises_error():
    with pytest.raises(ValidationError):
        Genotype(genes={
            Gene.METABOLISM_SPEED: 0.5,
            Gene.MAX_GENETIC_SPEED: 0.5,
            # Missing FAT_ACCUMULATION and MAX_GENETIC_AGE
        })


def test_genotype_value_out_of_range_raises_error():
    with pytest.raises(ValidationError):
        Genotype(genes={
            Gene.METABOLISM_SPEED: 1.5,  # Out of range
            Gene.MAX_GENETIC_SPEED: 0.5,
            Gene.FAT_ACCUMULATION: 0.5,
            Gene.MAX_GENETIC_AGE: 0.5,
        })


def test_genotype_negative_value_raises_error():
    with pytest.raises(ValidationError):
        Genotype(genes={
            Gene.METABOLISM_SPEED: -0.1,  # Negative
            Gene.MAX_GENETIC_SPEED: 0.5,
            Gene.FAT_ACCUMULATION: 0.5,
            Gene.MAX_GENETIC_AGE: 0.5,
        })


def test_gene_enum_has_min_max_properties():
    for gene in Gene:
        assert hasattr(gene, 'min')
        assert hasattr(gene, 'max')
        assert gene.min <= gene.max


class TestBeanEnergySystemIntegration:
    """Tests for Bean integration with EnergySystem."""

    def test_bean_accepts_optional_energy_system(self, beans_config, sample_genotype, sample_phenotype):
        """Bean should accept an optional EnergySystem in constructor."""
        from beans.energy_system import StandardEnergySystem
        
        energy_system = StandardEnergySystem(beans_config)
        bean = Bean(
            config=beans_config, 
            id=1, 
            sex=Sex.MALE, 
            genotype=sample_genotype, 
            phenotype=sample_phenotype,
            energy_system=energy_system
        )
        
        assert bean._energy_system is energy_system

    def test_bean_uses_energy_system_for_basal_metabolism(self, beans_config, sample_genotype):
        """Bean.update() should delegate basal metabolism to EnergySystem when provided."""
        from beans.energy_system import StandardEnergySystem
        
        config = BeansConfig(
            speed_min=-5, 
            speed_max=5, 
            initial_energy=100.0,
            metabolism_base_burn=0.1,
            initial_bean_size=10
        )
        energy_system = StandardEnergySystem(config)
        
        phenotype = Phenotype(age=0.0, speed=5.0, energy=100.0, size=10.0, target_size=10.0)
        bean = Bean(
            config=config, 
            id=1, 
            sex=Sex.MALE, 
            genotype=sample_genotype, 
            phenotype=phenotype,
            energy_system=energy_system
        )
        
        initial_energy = bean.energy
        bean.update(dt=1.0)
        
        # Energy should have changed (basal metabolism applied)
        # With metabolism_base_burn=0.1, size=10, metabolism_factor~1.25 → burn ~1.25
        assert bean.energy != initial_energy

    def test_bean_without_energy_system_uses_legacy_behavior(self, beans_config, sample_genotype):
        """Bean without EnergySystem should use existing energy calculation methods."""
        phenotype = Phenotype(age=0.0, speed=5.0, energy=100.0, size=10.0, target_size=10.0)
        bean = Bean(
            config=beans_config, 
            id=1, 
            sex=Sex.MALE, 
            genotype=sample_genotype, 
            phenotype=phenotype
        )
        
        initial_energy = bean.energy
        bean.update(dt=1.0)
        
        # Legacy behavior: gain - cost calculation still works
        assert bean.energy != initial_energy
