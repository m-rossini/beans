import logging

from beans.bean import BeanState
from config.loader import BeansConfig

logger = logging.getLogger(__name__)

class BeanDynamics:
    def __init__(self, config : BeansConfig):
        self.config: BeansConfig = config

    def calculate_speed(self, bean_state: BeanState) -> float:
        # Example: speed based on age and config min_speed_factor
        min_speed : float = self.config.min_speed_factor
        ret_val =  max(min_speed, 1.0 - bean_state.age * 0.01 * bean_state.speed)
        logger.debug(f">>>>> BeanDynamics.calculate_speed: age={bean_state.age}, speed={bean_state.speed}, min_speed={min_speed}, return value={ret_val}")
        return ret_val

