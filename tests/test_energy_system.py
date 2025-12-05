import pytest
import logging
from config.loader import BeansConfig

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
