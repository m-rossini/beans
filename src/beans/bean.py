import logging
from pydantic import BaseModel
from enum import Enum

from config.loader import BeansConfig
from .genetics import (
    Gene,
    Genotype,
    Phenotype,
    size_z_score,
    size_target,
    genetic_max_age,
    genetic_max_speed,
    age_speed_factor,
    age_energy_efficiency,
)

logger = logging.getLogger(__name__)

class BeanState(BaseModel):
    """Pydantic-based DTO for Bean mutable state.

    This DTO represents a snapshot of mutable bean properties that
    systems operate on. It is intentionally lightweight and
    supports a reusable `load()` method for reuse to avoid repeated allocation
    in tight simulation loops.
    """

    id: int
    age: float
    speed: float
    energy: float
    size: float
    alive: bool

    def __setattr__(self, name, value):
        # Prevent id from being changed after initialization
        if name == "id" and "id" in self.__dict__:
            raise AttributeError("id is read-only and cannot be modified after creation")
        super().__setattr__(name, value)

    def store(self, *, age: float | None = None, speed: float | None = None, energy: float | None = None, size: float | None = None) -> None:
        """Update only provided fields in-place for efficient reuse.

        Example::
            state.store(age=1.0)  # update only age
        """
        # Assign only values that were provided
        if age is not None:
            self.age = age
        if speed is not None:
            self.speed = speed
        if energy is not None:
            self.energy = energy
        if size is not None:
            self.size = size

class Sex(Enum):
    MALE = "male"
    FEMALE = "female"

class Bean:
    """Bean with mutable state, initialized from BeansConfig.

    Variables are expected to be set during construction. `update()` modifies the bean in place.
    Phenotype contains the mutable traits (age, speed, energy, size) that change over time.
    """

    def __init__(
        self,
        config: BeansConfig,
        id: int,
        sex: Sex,
        genotype: Genotype,
        phenotype: Phenotype,
    ) -> None:

        self.beans_config = config
        self.id = id
        self.sex = sex
        self.genotype = genotype
        self._phenotype = phenotype
        self._max_age = genetic_max_age(config, genotype)
        self.alive = True
        self._dto = BeanState(id=self.id, age=self.age, speed=self.speed, energy=self.energy, size=self.size, alive=self.alive)

        logger.debug(
            f">>>>> Bean {self.id} created: sex={self.sex.value}, "
            f"genotype={self.genotype.to_compact_str()}, "
            f"phenotype={{age:{self._phenotype.age:.1f}, speed:{self._phenotype.speed:.2f}, "
            f"alive:{self.alive}, "
            f"energy:{self._phenotype.energy:.1f}, size:{self._phenotype.size:.2f}, target_size:{self._phenotype.target_size:.2f}}}"
        )

    @property
    def age(self) -> float:
        return self._phenotype.age

    @property
    def speed(self) -> float:
        return self._phenotype.speed

    @property
    def energy(self) -> float:
        return self._phenotype.energy

    @property
    def size(self) -> float:
        return self._phenotype.size
    
    def die(self) -> None:
        """Mark the bean as dead."""
        self._alive = False

    def _is_dead(self) -> bool:
        """Check if the bean is dead."""
        return not self.alive
    
    def update(self, dt: float = 1.0) -> dict[str, float]:
        """Update bean in-place and return outcome metrics.
        
        Note: Energy system methods (basal metabolism, movement cost, etc.)
        are called by World, not by Bean itself.
        """
        if self._is_dead():
            logger.warning(f">>>>> Bean {self.id} update called on dead bean. No update performed.")
            return {"phenotype": self._phenotype.to_dict()}
        
        self._phenotype.age += 1.0
        self._phenotype.target_size = size_target(self.age, self.genotype, self.beans_config)
        self._update_speed()
        logger.debug(f">>>>> Bean {self.id} after update: phenotype={self._phenotype.to_dict()}, genotype={self.genotype.to_compact_str()},  dt={dt}")
        return {"phenotype": self._phenotype.to_dict()}

    def to_state(self) -> BeanState:
        """Return a `BeanState` DTO representing the current mutable bean state.

        Reuses a single DTO instance per Bean to minimize allocation in tight loops.
        """
        self._dto.store(
            age=self.age,
            speed=self.speed,
            energy=self.energy,
            size=self.size,
        )
        return self._dto

    def update_from_state(self, state: BeanState) -> BeanState:
        """Apply values from a `BeanState` DTO to this bean's phenotype.

        Raises:
            ValueError: if the DTO `id` doesn't match this bean's id.
        """
        if state.id != self.id:
            raise ValueError(f"BeanState id {state.id} does not match Bean id {self.id}")
        
        if self._is_dead():
            logger.warning(f">>>>> Bean {self.id} update_from_state called on dead bean. No update performed.")
            return
        
        self._phenotype.age = state.age
        self._phenotype.speed = state.speed
        self._phenotype.energy = state.energy
        self._phenotype.size = state.size

        return self.to_state()

    def _size_speed_penalty(self) -> float:
        """
        Compute speed penalty due to deviation from genetic target size.
        
        Uses z-score logic:
        - no penalty inside ±2σ
        - stronger penalty when overweight
        - slightly weaker when underweight
        """
        if self._is_dead():
            logger.warning(f">>>>> Bean {self.id} _size_speed_penalty called on dead bean. Returning penalty of 0.0.")
            return 0.0
        
        actual = self._phenotype.size
        target = self._phenotype.target_size
        if target <= 0:
            return 1.0

        z = size_z_score(actual, target)
        
        if z < -2:
            ret_val = max(0.4, 1 + z * 0.15)
        elif z > 2:
            ret_val = max(0.2, 1 - z * 0.25)
        else:
            ret_val = 1.0

        logger.debug(f">>>>> Bean {self.id} _size_speed_penalty: size={actual:.2f}, target={target:.2f}, z={z:.2f}, return value={ret_val:.2f}")
        return ret_val 

    def _update_speed(self):
        if self._is_dead():
            logger.warning(f">>>>> Bean {self.id} _update_speed called on dead bean. No update performed.")
            return

        vmax = genetic_max_speed(self.beans_config, self.genotype)
        old_speed = self._phenotype.speed
        life_factor = age_speed_factor(self.age, self._max_age)
        size_factor = self._size_speed_penalty()

        self._phenotype.speed = vmax * life_factor * size_factor
        logger.debug(f">>>>> Bean {self.id} _update_speed: max_age={self._max_age:.2f}, vmax={vmax:.2f}, life_factor={life_factor:.2f}, size_factor={size_factor:.2f},old_speed={old_speed:.2f}, new_speed={self._phenotype.speed:.2f}")    

    @property
    def is_male(self) -> bool:
        return self.sex == Sex.MALE

    @property
    def is_female(self) -> bool:
        return self.sex == Sex.FEMALE

    def can_survive_age(self) -> bool:
        """Check if bean can survive based on age vs genetic max age."""
        return self.age < self._max_age

    def survive(self) -> tuple[bool, str | None]:
        """Check if bean survives this step.
        
        Returns:
            (alive, reason): alive is True if bean survives, False otherwise.
                            reason is None if alive, otherwise the death reason.
        """
        if not self.can_survive_age():
            return False, "max_age_reached"

        if self.energy <= 0:
            return False, "energy_depleted"

        return True, None

