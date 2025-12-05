"""Energy System module for bean energy management.

This module provides a pluggable energy system responsible for:
- Energy intake
- Energy storage
- Fat accumulation
- Fat burning
- Metabolic cost
- Body size consequence
"""
import logging
from config.loader import BeansConfig

logger = logging.getLogger(__name__)


class EnergySystem:
    """Manages energy mechanics for beans.
    
    The EnergySystem handles all energy-related calculations including
    intake, metabolism, fat storage/burning, and size consequences.
    """

    def __init__(self, config: BeansConfig) -> None:
        """Initialize the EnergySystem with configuration.
        
        Args:
            config: BeansConfig containing energy system parameters.
        """
        self.config = config

    def apply_intake(self, bean, energy_eu: float) -> None:
        """Apply energy intake to a bean.
        
        Called when the bean eats. Directly increases circulating energy.
        
        Args:
            bean: The bean to apply intake to.
            energy_eu: Amount of energy units to add.
        """
        bean._phenotype.energy += energy_eu
