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
import math
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

    @abstractmethod
    def handle_negative_energy(self, bean: Bean) -> None:
        """Handle negative energy by burning fat to compensate.
        
        Args:
            bean: The bean to handle negative energy for.
        """
        ...

    @abstractmethod
    def clamp_size(self, bean: Bean) -> None:
        """Clamp bean size to valid range.
        
        Args:
            bean: The bean to clamp size for.
        """
        ...

    @abstractmethod
    def size_speed_penalty(self, bean: Bean) -> float:
        """Calculate speed penalty based on bean size deviation from target.
        
        Returns 1.0 when within ±2σ of target size, otherwise a penalty < 1.0.
        
        Args:
            bean: The bean to calculate penalty for.
            
        Returns:
            Penalty multiplier between min_penalty and 1.0.
        """
        ...

    @abstractmethod
    def can_survive_starvation(self, bean: Bean) -> bool:
        """Check if bean survives starvation based on size.
        
        Args:
            bean: The bean to check.
            
        Returns:
            True if size > min_bean_size, False otherwise.
        """
        ...

    @abstractmethod
    def can_survive_health(self, bean: Bean) -> bool:
        """Check if bean survives obesity-related health issues.
        
        Args:
            bean: The bean to check.
            
        Returns:
            True if survives, False if dies from obesity.
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

    def handle_negative_energy(self, bean: Bean) -> None:
        """Handle negative energy by burning fat to compensate.
        
        When energy < 0, burns fat to bring energy back to 0:
        fat_burned = abs(energy) / fat_to_energy_ratio
        
        Args:
            bean: The bean to handle negative energy for.
        """
        if bean.energy >= 0:
            return
        
        fat_burned = abs(bean.energy) / self.config.fat_to_energy_ratio
        bean._phenotype.size -= fat_burned
        bean._phenotype.energy = 0.0
        logger.debug(f">>>>> Bean {bean.id} handle_negative_energy: negative_energy={bean.energy:.2f}, fat_burned={fat_burned:.2f}, new_energy={bean.energy:.2f}")

    def clamp_size(self, bean: Bean) -> None:
        """Clamp bean size to valid range.
        
        Ensures size stays within [min_bean_size, max_bean_size].
        
        Args:
            bean: The bean to clamp size for.
        """
        # TODO: Extract size changes and clamping to separate sizing subsystem
        if bean.size < self.config.min_bean_size:
            bean._phenotype.size = self.config.min_bean_size
        elif bean.size > self.config.max_bean_size:
            bean._phenotype.size = self.config.max_bean_size
            
        logger.debug(f">>>>> Bean {bean.id} clamp_size: clamped_size={bean.size:.2f}, clamp_range=({self.config.min_bean_size}, {self.config.max_bean_size})")

    def size_speed_penalty(self, bean: Bean) -> float:
        """Calculate speed penalty based on bean size deviation from target.
        
        Returns 1.0 when within ±2σ of target size, otherwise applies
        exponential decay penalty based on z-score.
        
        Args:
            bean: The bean to calculate penalty for.
            
        Returns:
            Penalty multiplier between min_penalty and 1.0.
        """
        # TODO: Extract size speed penalty to sizing subsystem
        target_size = self.config.initial_bean_size
        sigma = target_size * self.config.size_sigma_frac
        z_score = (bean.size - target_size) / sigma
        
        if abs(z_score) <= 2:
            return 1.0
        
        if z_score > 2:
            # Overweight penalty
            excess_z = z_score - 2
            penalty = math.exp(-self.config.size_penalty_above_k * excess_z)
            result = max(penalty, self.config.size_penalty_min_above)
        else:
            # Underweight penalty
            deficit_z = abs(z_score) - 2
            penalty = math.exp(-self.config.size_penalty_below_k * deficit_z)
            result = max(penalty, self.config.size_penalty_min_below)
        
        logger.debug(f">>>>> Bean {bean.id} size_speed_penalty: size={bean.size:.2f}, z_score={z_score:.2f}, penalty={result:.3f}")
        return result

    def can_survive_starvation(self, bean: Bean) -> bool:
        """Check if bean survives starvation based on size.
        
        Bean dies of starvation when size reaches minimum (no more fat to burn).
        
        Args:
            bean: The bean to check.
            
        Returns:
            True if size > min_bean_size, False otherwise.
        """
        survives = bean.size > self.config.min_bean_size
        logger.debug(f">>>>> Bean {bean.id} can_survive_starvation: size={bean.size:.2f}, min_size={self.config.min_bean_size:.2f}, survives={survives}")
        return survives

    def can_survive_health(self, bean: Bean) -> bool:
        """Check if bean survives obesity-related health issues.
        
        When size > target_size * 2.5, there's a probability of death.
        The probability increases with excess size.
        
        Args:
            bean: The bean to check.
            
        Returns:
            True if survives, False if dies from obesity.
        """
        import random
        
        obesity_threshold = self.config.initial_bean_size * 2.5
        if bean.size <= obesity_threshold:
            return True
        
        # Probability of death increases with excess size
        excess_ratio = (bean.size - obesity_threshold) / obesity_threshold
        death_probability = min(0.5, excess_ratio * 0.2)  # Max 50% death chance
        
        survives = random.random() > death_probability
        logger.debug(f">>>>> Bean {bean.id} can_survive_health: size={bean.size:.2f}, obesity_threshold={obesity_threshold:.2f}, death_prob={death_probability:.2f}, survives={survives}")
        return survives