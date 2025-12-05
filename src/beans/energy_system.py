"""Energy System module for bean energy management.

This module provides a pluggable energy system responsible for:
- Energy intake
- Energy storage
- Fat accumulation
- Fat burning
- Metabolic cost
- Body size consequence

The module uses an abstract base class pattern to allow different
energy system implementations while sharing common logic.
"""
import logging
from abc import ABC, abstractmethod
from config.loader import BeansConfig
from beans.genetics import Gene

logger = logging.getLogger(__name__)


class EnergySystem(ABC):
    """Abstract base class for energy system implementations.
    
    Defines the interface for energy management and provides common
    helper methods that concrete implementations can use.
    """

    def __init__(self, config: BeansConfig) -> None:
        """Initialize the EnergySystem with configuration.
        
        Args:
            config: BeansConfig containing energy system parameters.
        """
        self.config = config

    @abstractmethod
    def apply_intake(self, bean, energy_eu: float) -> None:
        """Apply energy intake to a bean.
        
        Args:
            bean: The bean to apply intake to.
            energy_eu: Amount of energy units to add.
        """
        ...

    @abstractmethod
    def apply_basal_metabolism(self, bean) -> None:
        """Apply basal metabolic cost to a bean.
        
        Args:
            bean: The bean to apply basal metabolism to.
        """
        ...

    def _get_metabolism_factor(self, bean) -> float:
        """Calculate metabolism factor from bean's genetics.
        
        Returns a multiplier based on METABOLISM_SPEED gene.
        
        Args:
            bean: The bean to get metabolism factor for.
            
        Returns:
            Metabolism factor (1.0 to 1.5 based on gene value).
        """
        metabolism_speed = bean.genotype.genes[Gene.METABOLISM_SPEED]
        return 1 + 0.5 * metabolism_speed


class StandardEnergySystem(EnergySystem):
    """Standard implementation of the energy system.
    
    Implements the default energy mechanics including:
    - Direct energy intake
    - Size and metabolism-based basal burn
    """

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
        burn = metabolism_base_burn * metabolism_factor * size
        
        Higher metabolism gene and larger size increase burn rate.
        
        Args:
            bean: The bean to apply basal metabolism to.
        """
        metabolism_factor = self._get_metabolism_factor(bean)
        size = bean.size
        burn = self.config.metabolism_base_burn * metabolism_factor * size
        bean._phenotype.energy -= burn
