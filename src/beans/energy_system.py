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
from beans.genetics import Gene

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

    def apply_basal_metabolism(self, bean) -> None:
        """Apply basal metabolic cost to a bean.
        
        Deducts metabolism burn from the bean's energy based on:
        burn = metabolism_base_burn * (1 + 0.5 * METABOLISM_SPEED) * size
        
        Higher metabolism gene and larger size increase burn rate.
        
        Args:
            bean: The bean to apply basal metabolism to.
        """
        metabolism_speed = bean.genotype.genes[Gene.METABOLISM_SPEED]
        size = bean.size
        burn = self.config.metabolism_base_burn * (1 + 0.5 * metabolism_speed) * size
        bean._phenotype.energy -= burn
