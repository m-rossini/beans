import pytest
import logging
from abc import ABC
from config.loader import BeansConfig
from beans.bean import Bean, Sex
from beans.genetics import create_random_genotype, create_phenotype, Genotype, Gene

logger = logging.getLogger(__name__)


class TestEnergySystemABC:
    """Tests for EnergySystem abstract base class structure."""

    def test_energy_system_is_abstract_base_class(self):
        """EnergySystem should be an abstract base class."""
        from beans.energy_system import EnergySystem
        
        assert issubclass(EnergySystem, ABC)

    def test_energy_system_cannot_be_instantiated_directly(self):
        """EnergySystem should not be directly instantiable."""
        from beans.energy_system import EnergySystem
        
        config = BeansConfig(speed_min=-5, speed_max=5)
        with pytest.raises(TypeError):
            EnergySystem(config)

    def test_standard_energy_system_is_concrete_implementation(self):
        """StandardEnergySystem should be a concrete implementation."""
        from beans.energy_system import EnergySystem, StandardEnergySystem
        
        config = BeansConfig(speed_min=-5, speed_max=5)
        energy_system = StandardEnergySystem(config)
        
        assert isinstance(energy_system, EnergySystem)
        assert energy_system.config == config


class TestApplyIntake:
    """Tests for EnergySystem.apply_intake method."""

    def test_apply_intake_increases_bean_energy(self):
        """apply_intake should increase bean's energy by the given amount."""
        from beans.energy_system import EnergySystem
        
        config = BeansConfig(speed_min=-5, speed_max=5, initial_energy=50.0)
        energy_system = EnergySystem(config)
        
        genotype = create_random_genotype()
        phenotype = create_phenotype(config, genotype)
        bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=genotype, phenotype=phenotype)
        
        initial_energy = bean.energy
        energy_system.apply_intake(bean, 10.0)
        
        assert bean.energy == initial_energy + 10.0


class TestApplyBasalMetabolism:
    """Tests for EnergySystem.apply_basal_metabolism method."""

    def test_apply_basal_metabolism_uses_correct_formula(self):
        """apply_basal_metabolism should use: burn = base * (1 + 0.5 * metabolism) * size."""
        from beans.energy_system import EnergySystem
        
        config = BeansConfig(
            speed_min=-5, 
            speed_max=5, 
            initial_energy=100.0,
            initial_bean_size=10,
            metabolism_base_burn=0.10
        )
        energy_system = EnergySystem(config)
        
        # Create genotype with known metabolism value
        genes = {
            Gene.METABOLISM_SPEED: 0.5,
            Gene.MAX_GENETIC_SPEED: 0.5,
            Gene.FAT_ACCUMULATION: 0.5,
            Gene.MAX_GENETIC_AGE: 0.5,
        }
        genotype = Genotype(genes=genes)
        phenotype = create_phenotype(config, genotype)
        phenotype.size = 10.0
        bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=genotype, phenotype=phenotype)
        bean._phenotype.energy = 100.0
        
        initial_energy = bean.energy
        energy_system.apply_basal_metabolism(bean)
        
        # burn = 0.10 * (1 + 0.5 * 0.5) * 10 = 0.10 * 1.25 * 10 = 1.25
        expected_burn = config.metabolism_base_burn * (1 + 0.5 * 0.5) * 10.0
        assert bean.energy == initial_energy - expected_burn

    def test_higher_metabolism_gene_increases_burn_rate(self):
        """Higher METABOLISM_SPEED gene value should increase basal burn rate."""
        from beans.energy_system import EnergySystem
        
        config = BeansConfig(
            speed_min=-5, 
            speed_max=5, 
            initial_energy=100.0,
            initial_bean_size=10,
            metabolism_base_burn=0.10
        )
        energy_system = EnergySystem(config)
        
        # Create two genotypes with different metabolism speeds
        low_metabolism_genes = {
            Gene.METABOLISM_SPEED: 0.0,
            Gene.MAX_GENETIC_SPEED: 0.5,
            Gene.FAT_ACCUMULATION: 0.5,
            Gene.MAX_GENETIC_AGE: 0.5,
        }
        high_metabolism_genes = {
            Gene.METABOLISM_SPEED: 1.0,
            Gene.MAX_GENETIC_SPEED: 0.5,
            Gene.FAT_ACCUMULATION: 0.5,
            Gene.MAX_GENETIC_AGE: 0.5,
        }
        
        low_genotype = Genotype(genes=low_metabolism_genes)
        high_genotype = Genotype(genes=high_metabolism_genes)
        
        # Create phenotypes with same size to isolate metabolism effect
        low_phenotype = create_phenotype(config, low_genotype)
        high_phenotype = create_phenotype(config, high_genotype)
        low_phenotype.size = 10.0
        high_phenotype.size = 10.0
        
        low_bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=low_genotype, phenotype=low_phenotype)
        high_bean = Bean(config=config, id=2, sex=Sex.MALE, genotype=high_genotype, phenotype=high_phenotype)
        
        # Set same initial energy
        low_bean._phenotype.energy = 100.0
        high_bean._phenotype.energy = 100.0
        
        energy_system.apply_basal_metabolism(low_bean)
        energy_system.apply_basal_metabolism(high_bean)
        
        # Higher metabolism should burn more energy
        assert high_bean.energy < low_bean.energy
