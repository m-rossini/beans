import logging

from beans.bean import BeanState
from config.loader import BeansConfig

logger = logging.getLogger(__name__)


from beans.genetics import genetic_max_speed, age_speed_factor, size_z_score

class BeanDynamics:
    def __init__(self, config: BeansConfig, genotype=None, max_age=None):
        self.config: BeansConfig = config
        self.genotype = genotype
        self.max_age = max_age

    def calculate_speed(self, bean_state: BeanState, genotype=None, max_age=None) -> float:
        # Use provided genotype/max_age or fallback to instance
        genotype = genotype or self.genotype
        max_age = max_age or self.max_age
        # If genotype or max_age is not available, use default speed logic (legacy behavior)
        if genotype is None or max_age is None:
            # Fallback: just return bean_state.speed (legacy behavior)
            return bean_state.speed

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

