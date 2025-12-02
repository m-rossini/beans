import logging
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
)

logger = logging.getLogger(__name__)


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
        
        logger.debug(
            f">>>>> Bean {self.id} created: sex={self.sex.value}, "
            f"genotype={self.genotype.to_compact_str()}, "
            f"phenotype={{age:{self._phenotype.age:.1f}, speed:{self._phenotype.speed:.2f}, "
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

    def update(self, dt: float = 1.0) -> dict[str, float]:
        """Update bean in-place and return outcome metrics."""
        self._phenotype.age += 1.0
        energy = self._update_energy(dt)
        self._phenotype.target_size = size_target(self.age, self.genotype, self.beans_config)
        self._update_speed()
        logger.debug(f">>>>> Bean {self.id} after update: dt={dt}, genotype={self.genotype.genes}, phenotype={self._phenotype.to_dict()}")
        return {"phenotype": self._phenotype.to_dict()}

    def _size_speed_penalty(self) -> float:
        """
        Compute speed penalty due to deviation from genetic target size.
        
        Uses z-score logic:
        - no penalty inside ±2σ
        - stronger penalty when overweight
        - slightly weaker when underweight
        """

        actual = self._phenotype.size
        target = self._phenotype.target_size
        if target <= 0:
            return 1.0

        z = size_z_score(actual, target)
        
        if z < -2:
            ret_val = max(0.4, 1 + z * 0.15)

        if z > 2:
            ret_val = max(0.2, 1 - z * 0.25)
        
        ret_val = 1.0

        logger.debug(f">>>>> Bean {self.id} _size_speed_penalty: size={actual:.2f}, target={target:.2f}, z={z:.2f}, return value={ret_val:.2f}")
        return ret_val 

    def _update_speed(self):
        vmax = genetic_max_speed(self.beans_config, self.genotype)

        life_factor = age_speed_factor(self.age, self._max_age)
        size_factor = self._size_speed_penalty()

        self._phenotype.speed = vmax * life_factor * size_factor
        logger.debug(f">>>>> Bean {self.id} _update_speed: max_age={self._max_age:.2f}, vmax={vmax:.2f}, life_factor={life_factor:.2f}, size_factor={size_factor:.2f}, new_speed={self._phenotype.speed:.2f}")    

    def _update_energy(self, dt: float = 1.0) -> float:
        """Adjust energy based on per-step gains and movement costs."""
        gain = self.beans_config.energy_gain_per_step
        cost = abs(self.speed) * self.beans_config.energy_cost_per_speed
        old_energy = self.energy
        self._phenotype.energy += gain - cost
        logger.debug(f">>>>> Bean {self.id} _update_energy: gain={gain}, cost={cost:.2f}, old_energy={old_energy:.2f}, new_energy={self.energy:.2f}, speed={self.speed:.2f}, cost_per_speed={self.beans_config.energy_cost_per_speed}, dt={dt}")

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

