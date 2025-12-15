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
from typing import Tuple

from beans.bean import Bean, BeanState
from beans.genetics import Gene, size_target
from config.loader import BeansConfig

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

    def apply_energy_system(self, bean: Bean, energy_intake_eu: float) -> BeanState:
        """Apply the energy system mechanics to a bean for one update cycle.

        This method orchestrates the energy system steps:
        1. Apply energy intake
        2. Apply basal metabolism cost
        3. Apply movement cost
        4. Apply fat storage from surplus energy
        5. Apply fat burning from energy deficit
        6. Handle negative energy by burning fat
        7. Clamp size to valid range

        Args:
            bean: The bean to apply the energy system to.
            energy_intake_eu: Amount of energy units the bean has ingested.

        """
        bean_state: BeanState = bean.to_state()
        # Set target_size every step
        bean_state.target_size = self._calculate_target_size(bean)

        bean_state.energy = self._apply_intake(bean_state, energy_intake_eu)
        bean_state.energy = self._apply_basal_metabolism(bean_state, self._get_metabolism_factor(bean))
        bean_state.energy = self._apply_movement_cost(bean_state)
        bean_state.energy, bean_state.size = self._apply_fat_storage(bean_state, bean.genotype.genes[Gene.FAT_ACCUMULATION])
        bean_state.energy, bean_state.size = self._apply_fat_burning(bean_state, bean.genotype.genes[Gene.FAT_ACCUMULATION])
        bean_state.energy, bean_state.size = self._handle_negative_energy(bean_state)
        bean_state.size = self._clamp_size(bean_state)

        return bean_state

    def _calculate_target_size(self, bean: Bean) -> float:
        """Calculate the target size for a bean using genotype and config."""
        return size_target(bean.age, bean.genotype, self.config)

    @abstractmethod
    def _apply_intake(self, bean_state: BeanState, energy_eu: float) -> float:
        """Apply energy intake to a bean.

        Args:
            bean: The bean to apply intake to.
            energy_eu: Amount of energy units to add.

        """
        ...

    @abstractmethod
    def _apply_basal_metabolism(self, bean_state: BeanState, metabolism_factor: float) -> float:
        """Apply basal metabolic cost to a bean.

        Args:
            bean: The bean to apply basal metabolism to.

        """
        ...

    @abstractmethod
    def _apply_movement_cost(self, bean_state: BeanState) -> float:
        """Apply movement cost to a bean.

        Args:
            bean: The bean to apply movement cost to.

        """
        ...

    @abstractmethod
    def _apply_fat_storage(self, bean_state: BeanState, fat_accumulation: float) -> Tuple[float, float]:
        """Apply fat storage from energy surplus.

        Args:
            bean: The bean to apply fat storage to.

        """
        ...

    @abstractmethod
    def _apply_fat_burning(self, bean_state: BeanState, fat_accumulation: float) -> Tuple[float, float]:
        """Apply fat burning from energy deficit.

        Args:
            bean: The bean to apply fat burning to.

        """
        ...

    @abstractmethod
    def _handle_negative_energy(self, bean_state: BeanState) -> Tuple[float, float]:
        """Handle negative energy by burning fat to compensate.

        Args:
            bean: The bean to handle negative energy for.

        """
        ...

    @abstractmethod
    def _clamp_size(self, bean_state: BeanState) -> float:
        """Clamp bean size to valid range.

        Args:
            bean: The bean to clamp size for.

        """
        ...

    @abstractmethod
    def _can_survive_starvation(self, bean: Bean) -> bool:
        """Check if bean survives starvation based on size.

        Args:
            bean: The bean to check.

        Returns:
            True if size > min_bean_size, False otherwise.

        """
        ...

    @abstractmethod
    def _can_survive_health(self, bean: Bean) -> bool:
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

    def _apply_intake(self, bean_state: BeanState, energy_eu: float) -> float:
        """Apply energy intake to a bean.

        Called when the bean eats. Directly increases circulating energy.

        Args:
            bean: The bean to apply intake to.
            energy_eu: Amount of energy units to add.

        """
        ret_val = bean_state.energy + energy_eu
        logger.debug(
            f">>>>> Bean {bean_state.id}"
            f" apply_intake: energy_eu={energy_eu},"
            f" old_energy={bean_state.energy:.2f},"
            f" new_energy={ret_val:.2f}"
        )
        return ret_val

    def _apply_basal_metabolism(self, bean_state: BeanState, metabolism_factor: float) -> float:
        """Apply basal metabolic cost to a bean.

        Deducts metabolism burn from the bean's energy based on:
        burn = metabolism_base_burn * metabolism_factor * size
        size = bean_state.size
        Higher metabolism gene and larger size increase burn rate.

        Args:
            bean: The bean to apply basal metabolism to.

        """
        size = bean_state.size
        burn = self.config.metabolism_base_burn * metabolism_factor * size
        ret_val = bean_state.energy - burn
        logger.debug(
            f">>>>> Bean {bean_state.id}"
            f" apply_basal_metabolism: size={size:.2f},"
            f" metabolism_factor={metabolism_factor:.2f},"
            f" burn={burn:.2f}"
            f" new_energy={ret_val:.2f}"
        )
        return ret_val

    def _apply_movement_cost(self, bean_state: BeanState) -> float:
        """Apply movement cost to a bean.

        Deducts energy based on absolute speed:
        cost = abs(speed) * energy_cost_per_speed

        Args:
            bean: The bean to apply movement cost to.

        """
        cost = abs(bean_state.speed) * self.config.energy_cost_per_speed
        ret_val = bean_state.energy - cost
        logger.debug(
            f">>>>> Bean {bean_state.id}"
            f" apply_movement_cost: speed={bean_state.speed:.2f},"
            f" cost={cost:.2f},"
            f" energy_cost_per_speed={self.config.energy_cost_per_speed:.2f},"
            f" new_energy={ret_val:.2f}"
        )
        return ret_val

    def _apply_fat_storage(self, bean_state: BeanState, fat_accumulation: float) -> Tuple[float, float]:
        """Apply fat storage from energy surplus.

        When energy > energy_baseline, converts surplus to fat (size):
        fat_gain = fat_gain_rate * FAT_ACCUMULATION * surplus
        energy_cost = fat_gain * energy_to_fat_ratio

        Args:
            bean: The bean to apply fat storage to.

        """
        surplus = bean_state.energy - self.config.energy_baseline
        if surplus <= 0:
            return bean_state.energy, bean_state.size

        fat_gain = self.config.fat_gain_rate * fat_accumulation * surplus
        energy_cost = fat_gain * self.config.energy_to_fat_ratio

        phenotype_size = bean_state.size + fat_gain
        phenotype_energy = bean_state.energy - energy_cost
        logger.debug(
            f">>>>> Bean {bean_state.id}"
            f" apply_fat_storage: surplus={surplus:.2f},"
            f" fat_gain={fat_gain:.2f},"
            f" energy_cost={energy_cost:.2f}"
            f" new_energy={phenotype_energy:.2f},"
            f" new_size={phenotype_size:.2f}"
        )
        return (phenotype_energy, phenotype_size)

    def _apply_fat_burning(self, bean_state: BeanState, fat_accumulation: float) -> Tuple[float, float]:
        """Apply fat burning from energy deficit.

        When energy < energy_baseline, burns fat (size) to gain energy:
        fat_burned = fat_burn_rate * FAT_ACCUMULATION * deficit
        energy_gain = fat_burned * fat_to_energy_ratio

        Args:
            bean: The bean to apply fat burning to.

        """
        deficit = self.config.energy_baseline - bean_state.energy
        if deficit <= 0:
            return bean_state.energy, bean_state.size

        fat_burned = self.config.fat_burn_rate * fat_accumulation * deficit
        # Do not burn below minimum bean size — only burn available fat
        available_fat = max(0.0, bean_state.size - self.config.min_bean_size)
        fat_burned = min(fat_burned, available_fat)
        energy_gain = fat_burned * self.config.fat_to_energy_ratio

        phenotype_size = bean_state.size - fat_burned
        phenotype_energy = bean_state.energy + energy_gain
        msg = (
            ">>>>> Bean %s apply_fat_burning: deficit=%0.2f, fat_burned=%0.2f, energy_gain=%0.2f, new_energy=%0.2f, "
            "old_size=%0.2f, new_size=%0.2f"
        )
        logger.debug(
            msg,
            bean_state.id,
            deficit,
            fat_burned,
            energy_gain,
            phenotype_energy,
            bean_state.size,
            phenotype_size,
        )
        return (phenotype_energy, phenotype_size)

    def _handle_negative_energy(self, bean_state: BeanState) -> Tuple[float, float]:
        """Handle negative energy by burning fat to compensate.

        When energy < 0, burns fat to bring energy back to 0:
        fat_burned = abs(energy) / fat_to_energy_ratio

        Args:
            bean: The bean to handle negative energy for.

        """
        if bean_state.energy >= 0:
            return (bean_state.energy, bean_state.size)

        # Only burn available fat above minimum size
        fat_needed = abs(bean_state.energy) / self.config.fat_to_energy_ratio
        available_fat = max(0.0, bean_state.size - self.config.min_bean_size)
        fat_burned = min(fat_needed, available_fat)

        phenotype_size = bean_state.size - fat_burned
        phenotype_energy = bean_state.energy + fat_burned * self.config.fat_to_energy_ratio

        logger.debug(
            ">>>>> Bean %s handle_negative_energy: negative_energy=%0.2f, fat_needed=%0.2f, fat_burned=%0.2f, new_energy=%0.2f",
            bean_state.id,
            bean_state.energy,
            fat_needed,
            fat_burned,
            phenotype_energy,
        )
        return (phenotype_energy, phenotype_size)

    def _clamp_size(self, bean_state: BeanState) -> float:
        """Clamp bean size to valid range.

        Ensures size stays within [min_bean_size, max_bean_size].

        Args:
            bean: The bean to clamp size for.

        """
        size = bean_state.size
        if bean_state.size < self.config.min_bean_size:
            size = self.config.min_bean_size
        elif bean_state.size > self.config.max_bean_size:
            size = self.config.max_bean_size

        logger.debug(
            ">>>>> Bean %s old_size=%0.2f clamp_size: clamped_size=%0.2f clamp_range=(%s, %s)",
            bean_state.id,
            bean_state.size,
            size,
            self.config.min_bean_size,
            self.config.max_bean_size,
        )
        return size

    def _size_speed_penalty(self, bean: Bean) -> float:
        # size-speed penalty belongs to BeanDynamics.calculate_speed
        # and is not part of the EnergySystem responsibilities.
        # This placeholder should not be used; raise if invoked to avoid
        # silent divergence of behavior.
        raise NotImplementedError("size-speed penalty is implemented in BeanDynamics")

    def _can_survive_starvation(self, bean: Bean) -> bool:
        """Check if bean survives starvation based on size.

        Bean dies of starvation when size reaches minimum (no more fat to burn).

        Args:
            bean: The bean to check.

        Returns:
            True if size > min_bean_size, False otherwise.

        """
        survives = bean.size > self.config.min_bean_size
        logger.debug(
            ">>>>> Bean %s can_survive_starvation: size=%0.2f, min_size=%0.2f, survives=%s",
            bean.id,
            bean.size,
            self.config.min_bean_size,
            survives,
        )
        return survives

    def _can_survive_health(self, bean: Bean) -> bool:
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
        logger.debug(
            ">>>>> Bean %s can_survive_health: size=%0.2f, obesity_threshold=%0.2f, death_prob=%0.2f, survives=%s",
            bean.id,
            bean.size,
            obesity_threshold,
            death_probability,
            survives,
        )
        return survives


def create_energy_system_from_name(name: str, config: BeansConfig) -> EnergySystem:
    """Factory function to create an EnergySystem from a name.

    Args:
        name: Name of the energy system to create ("standard" or empty).
        config: BeansConfig containing energy system parameters.

    Returns:
        An EnergySystem instance.

    Raises:
        ValueError: If the name is not recognized.

    """
    logger.info(f">>>> create_energy_system_from_name: name={name}")
    if not name or name.lower() == "standard":
        return StandardEnergySystem(config)
    raise ValueError(f"Unknown energy system: {name}")
