import pytest
import logging
from config.loader import BeansConfig
from beans.bean import Bean, Sex
from beans.genetics import create_random_genotype, create_phenotype

logger = logging.getLogger(__name__)


class TestEnergySystemCreation:
    """Tests for EnergySystem class instantiation."""

    def test_energy_system_can_be_instantiated_with_config(self):
        """EnergySystem should be instantiable with a BeansConfig."""
        from beans.energy_system import EnergySystem
        
        config = BeansConfig(speed_min=-5, speed_max=5)
        energy_system = EnergySystem(config)
        
        assert energy_system is not None
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
