import logging
import random
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from config.loader import BeansConfig

from .genetics import Genotype, Phenotype, extract_phenotype_values, genetic_max_age

logger = logging.getLogger(__name__)

class BeanContext(BaseModel):
    """Runtime context for spawning beans.

    Holds creation counts and an optional RNG used to create deterministic
    genotypes/phenotypes for testing or reproducible runs.
    """

    bean_count: int
    male_count: int
    rng: Optional[random.Random] = None

    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    def validate_counts(cls, bean_count: int, male_count: int) -> None:
        if bean_count < 0:
            raise ValueError("bean_count must be >= 0")
        if male_count < 0:
            raise ValueError("male_count must be >= 0")
        if male_count > bean_count:
            raise ValueError("male_count cannot be greater than bean_count")

    def __init__(self, **data):
        bean_count = data.get("bean_count")
        male_count = data.get("male_count")
        self.validate_counts(bean_count, male_count)
        super().__init__(**data)

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
    target_size: float
    alive: bool

    def __setattr__(self, name, value):
        # Prevent id from being changed after initialization
        if name == "id" and "id" in self.__dict__:
            raise AttributeError("id is read-only and cannot be modified after creation")
        super().__setattr__(name, value)

    def store(
        self,
        *,
        age: float | None = None,
        speed: float | None = None,
        energy: float | None = None,
        size: float | None = None,
        target_size: float | None = None,
    ) -> None:
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
        if target_size is not None:
            self.target_size = target_size
        # 'alive' is not set via store; use Bean.die() to change alive state.


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
        # import already at top
        self.beans_config: BeansConfig = config
        self.id = id
        self.sex = sex
        self.genotype = genotype
        self._phenotype = phenotype
        self._max_age = genetic_max_age(config, genotype)
        self.alive = True
        self._dto = BeanState(
            id=self.id,
            age=self.age,
            speed=self.speed,
            energy=self.energy,
            size=self.size,
            target_size=self._phenotype.target_size,
            alive=self.alive,
        )

        phenotype_str = (
            f"age:{self._phenotype.age:.1f}, speed:{self._phenotype.speed:.2f}, "
            f"alive:{self.alive}, energy:{self._phenotype.energy:.1f}, "
            f"size:{self._phenotype.size:.2f}, target_size:{self._phenotype.target_size:.2f}"
        )
        logger.debug(
            ">>>>> Bean %s created: sex=%s, genotype=%s, phenotype=%s",
            self.id,
            self.sex.value,
            self.genotype.to_compact_str(),
            phenotype_str,
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

    @property
    def is_male(self) -> bool:
        return self.sex == Sex.MALE

    @property
    def is_female(self) -> bool:
        return self.sex == Sex.FEMALE

    def die(self) -> None:
        """Mark the bean as dead."""
        self.alive = False

    def _is_dead(self) -> bool:
        """Check if the bean is dead."""
        return not self.alive

    def age_bean(self, dt: float = 1.0) -> float:
        """Update bean in-place and return outcome metrics.

        Note: Energy system methods (basal metabolism, movement cost, etc.)
        are called by World, not by Bean itself.
        """
        if self._is_dead():
            logger.warning(f">>> Bean {self.id} update called on dead bean. No update performed.")
            return {"phenotype": extract_phenotype_values(self._phenotype)}

        return self._phenotype.age + 1

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
            logger.warning(f">>> Bean {self.id} update_from_state called on dead bean. No update performed.")
            return

        logger.debug(
            f">>>>> Bean {self.id} update_from_state: before update"
            f" phenotype={extract_phenotype_values(self._phenotype)},"
            f" state={{age:{state.age}"
            f" speed:{state.speed:.2f}"
            f" energy:{state.energy:.2f}"
            f" size:{state.size:.2f}}}"
        )
        self._phenotype.age = state.age
        self._phenotype.speed = state.speed
        self._phenotype.energy = state.energy
        self._phenotype.size = state.size

        return self.to_state()
