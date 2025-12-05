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
from beans.bean import Bean
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
    def apply_intake(self, bean: Bean, energy_eu: float) -> None:
        """Apply energy intake to a bean.
        
        Args:
            bean: The bean to apply intake to.
            energy_eu: Amount of energy units to add.
        """
        ...

    @abstractmethod
    def apply_basal_metabolism(self, bean: Bean) -> None:
        """Apply basal metabolic cost to a bean.
        
        Args:
            bean: The bean to apply basal metabolism to.
        """
        ...

    @abstractmethod
    def apply_movement_cost(self, bean: Bean) -> None:
        """Apply movement cost to a bean.
        
        Args:
            bean: The bean to apply movement cost to.
        """
        ...

    @abstractmethod
    def apply_fat_storage(self, bean: Bean) -> None:
        """Apply fat storage from energy surplus.
        
        Args:
            bean: The bean to apply fat storage to.
        """
        ...

    @abstractmethod
    def apply_fat_burning(self, bean: Bean) -> None:
        """Apply fat burning from energy deficit.
        
        Args:
            bean: The bean to apply fat burning to.
        """
        ...

    def _get_metabolism_factor(self, bean: Bean) -> float:
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

    def apply_intake(self, bean: Bean, energy_eu: float) -> None:
        """Apply energy intake to a bean.
        
        Called when the bean eats. Directly increases circulating energy.
        
        Args:
            bean: The bean to apply intake to.
            energy_eu: Amount of energy units to add.
        """
        bean._phenotype.energy += energy_eu
        logger.debug(f">>>>> Bean {bean.id} apply_intake: energy_eu={energy_eu}, new_energy={bean.energy:.2f}")

    def apply_basal_metabolism(self, bean: Bean) -> None:
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
        logger.debug(f">>>>> Bean {bean.id} apply_basal_metabolism: size={size:.2f}, metabolism_factor={metabolism_factor:.2f}, burn={burn:.2f}")

    def apply_movement_cost(self, bean: Bean) -> None:
        """Apply movement cost to a bean.
        
        Deducts energy based on absolute speed:
        cost = abs(speed) * energy_cost_per_speed
        
        Args:
            bean: The bean to apply movement cost to.
        """
        cost = abs(bean.speed) * self.config.energy_cost_per_speed
        bean._phenotype.energy -= cost
        logger.debug(f">>>>> Bean {bean.id} apply_movement_cost: speed={bean.speed:.2f}, cost={cost:.2f}, energy_cost_per_speed={self.config.energy_cost_per_speed:.2f}")

    def apply_fat_storage(self, bean: Bean) -> None:
        """Apply fat storage from energy surplus.
        
        When energy > energy_baseline, converts surplus to fat (size):
        fat_gain = fat_gain_rate * FAT_ACCUMULATION * surplus
        energy_cost = fat_gain * energy_to_fat_ratio
        
        Args:
            bean: The bean to apply fat storage to.
        """
        surplus = bean.energy - self.config.energy_baseline
        if surplus <= 0:
            return
        
        fat_accumulation = bean.genotype.genes[Gene.FAT_ACCUMULATION]
        fat_gain = self.config.fat_gain_rate * fat_accumulation * surplus
        energy_cost = fat_gain * self.config.energy_to_fat_ratio
        
        bean._phenotype.size += fat_gain
        bean._phenotype.energy -= energy_cost
        logger.debug(f">>>>> Bean {bean.id} apply_fat_storage: surplus={surplus:.2f}, fat_gain={fat_gain:.2f}, energy_cost={energy_cost:.2f}")

    def apply_fat_burning(self, bean: Bean) -> None:
        """Apply fat burning from energy deficit.
        
        When energy < energy_baseline, burns fat (size) to gain energy:
        fat_burned = fat_burn_rate * FAT_ACCUMULATION * deficit
        energy_gain = fat_burned * fat_to_energy_ratio
        
        Args:
            bean: The bean to apply fat burning to.
        """
        deficit = self.config.energy_baseline - bean.energy
        if deficit <= 0:
            return
        
        fat_accumulation = bean.genotype.genes[Gene.FAT_ACCUMULATION]
        fat_burned = self.config.fat_burn_rate * fat_accumulation * deficit
        energy_gain = fat_burned * self.config.fat_to_energy_ratio
        
        bean._phenotype.size -= fat_burned
        bean._phenotype.energy += energy_gain
        logger.debug(f">>>>> Bean {bean.id} apply_fat_burning: deficit={deficit:.2f}, fat_burned={fat_burned:.2f}, energy_gain={energy_gain:.2f}")