import logging

from beans.bean import BeanState
from config.loader import BeansConfig

logger = logging.getLogger(__name__)


from beans.genetics import age_speed_factor, genetic_max_speed, size_z_score


class BeanDynamics:
    def __init__(self, config: BeansConfig):
        self.config: BeansConfig = config

    def calculate_speed(self, bean_state: BeanState, genotype, max_age: float) -> float:
        """Calculate speed using the provided bean_state and per-bean genotype/max_age.

        This lets the world keep a single BeanDynamics instance while supplying
        per-bean genetic parameters at calculation time.
        """
        vmax = genetic_max_speed(self.config, genotype)
        min_speed = self.config.min_speed_factor
        age_factor = age_speed_factor(bean_state.age, max_age, min_speed)
        size_penalty = self._size_speed_penalty(bean_state)
        speed = vmax * age_factor * size_penalty
        logger.debug(f">>>>> BeanDynamics.calculate_speed: vmax={vmax:.2f}, age_factor={age_factor:.2f}, size_penalty={size_penalty:.2f}, min_speed={min_speed:.2f}, result={speed:.2f}")
        return max(min_speed, speed)

    def _size_speed_penalty(self, bean_state: BeanState) -> float:
        actual = bean_state.size
        target = bean_state.target_size
        if target <= 0:
            return 1.0
        z = size_z_score(actual, target)
        if z < -2:
            return max(0.4, 1 + z * 0.15)
        elif z > 2:
            return max(0.2, 1 - z * 0.25)
        else:
            return 1.0

