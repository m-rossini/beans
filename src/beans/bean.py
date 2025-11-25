import random
import math
from config.loader import BeansConfig
from typing import Tuple, Optional
from enum import Enum

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

        self.beans_config = config
        self.id = id
        self.sex = sex
        self.age = 0.0
        direction = random.uniform(0, 360) if direction is None else direction
        self.direction = direction % 360.0
        self.speed = random.uniform(config.speed_min, config.speed_max) if speed is None else speed
        self.energy = config.initial_energy

    def update(self, dt: float = 1.0) -> dict[str, float]:
        """Update bean in-place and return outcome metrics."""
        self.age += 1.0
        energy = self._energy_tick(dt)
        return {"energy": energy}

    def _energy_tick(self, dt: float = 1.0) -> float:
        """Adjust energy based on per-step gains and movement costs."""
        gain = self.beans_config.energy_gain_per_step * dt
        cost = abs(self.speed) * self.beans_config.energy_cost_per_speed * dt
        self.energy += gain - cost
        return self.energy

    @property
    def is_male(self) -> bool:
        return self.sex == Sex.MALE

    @property
    def is_female(self) -> bool:
        return self.sex == Sex.FEMALE
