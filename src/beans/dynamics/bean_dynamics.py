from typing import Tuple

class BeanDynamics:
    def __init__(self, config):
        self.config = config

    def calculate_speed(self, bean_state) -> float:
        # Example: speed based on age and config min_speed_factor
        age = bean_state.age
        min_speed = self.config.min_speed_factor
        # Placeholder logic, to be refined
        return max(min_speed, 1.0 - age * 0.01)

    def update_position(self, bean_state) -> Tuple[float, float]:
        speed = self.calculate_speed(bean_state)
        x, y = bean_state.position
        dx, dy = bean_state.direction
        # Simple movement: position += direction * speed
        new_x = x + dx * speed
        new_y = y + dy * speed
        return (new_x, new_y)

    def update_direction(self, bean_state) -> Tuple[float, float]:
        # Placeholder: keep direction unchanged
        return bean_state.direction
