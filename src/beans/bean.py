import random
import math
import logging
from config.loader import BeansConfig
from typing import Tuple, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class Sex(Enum):
    MALE = "male"
    FEMALE = "female"

class Bean:
    """Bean with mutable state, initialized from optional BeansConfig.

    Variables are expected to be set during construction. `update()` modifies the bean in place.
    """

    def __init__(
        self,
        config: BeansConfig,
        id: int,
        sex: Sex,
        direction: Optional[float] = None,
        speed: Optional[float] = None,) -> None:
        logger.debug(f">>>>> Bean.__init__: id={id}, sex={sex}, direction={direction}, speed={speed}")

        self.beans_config = config
        self.id = id
        self.sex = sex
        self.age = 0.0
        direction = random.uniform(0, 360) if direction is None else direction
        self.direction = direction % 360.0
        self.speed = random.uniform(config.speed_min, config.speed_max) if speed is None else speed
        self.energy = config.initial_energy
        self.size = config.initial_bean_size
        logger.debug(f">>>>> Bean {self.id} created: sex={self.sex.value}, direction={self.direction:.2f}, speed={self.speed:.2f}, energy={self.energy}")

    def update(self, dt: float = 1.0) -> dict[str, float]:
        """Update bean in-place and return outcome metrics."""
        self.age += 1.0
        energy = self._energy_tick(dt)
        logger.debug(f">>>>> Bean {self.id} after update: age={self.age}, energy={energy:.2f}, dt={dt}")
        return {"energy": energy}

    def _energy_tick(self, dt: float = 1.0) -> float:
        """Adjust energy based on per-step gains and movement costs."""
        gain = self.beans_config.energy_gain_per_step
        cost = abs(self.speed) * self.beans_config.energy_cost_per_speed
        old_energy = self.energy
        self.energy += gain - cost
        logger.debug(f">>>>> Bean {self.id} _energy_tick: gain={gain}, cost={cost:.2f}, old_energy={old_energy:.2f}, new_energy={self.energy:.2f}, speed={self.speed:.2f}, cost_per_speed={self.beans_config.energy_cost_per_speed}")
        return self.energy

    @property
    def is_male(self) -> bool:
        return self.sex == Sex.MALE

    @property
    def is_female(self) -> bool:
        return self.sex == Sex.FEMALE
