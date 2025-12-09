import pytest
from src.beans.dynamics.bean_dynamics import BeanDynamics

# Dummy BeansConfig and BeanState for test scaffolding
class BeansConfig:
    def __init__(self, min_speed_factor=0.1):
        self.min_speed_factor = min_speed_factor

class BeanState:
    def __init__(self, age, position, direction):
        self.age = age
        self.position = position
        self.direction = direction



def test_bean_dynamics_speed_calculation():
    config = BeansConfig(min_speed_factor=0.2)
    bean_state = BeanState(age=5, position=(0, 0), direction=(1, 0))
    dynamics = BeanDynamics(config)
    speed = dynamics.calculate_speed(bean_state)
    # Expected: max(min_speed, 1.0 - age * 0.01)
    assert speed == max(0.2, 1.0 - 5 * 0.01)


def test_bean_dynamics_position_update():
    config = BeansConfig()
    bean_state = BeanState(age=2, position=(1, 1), direction=(0, 1))
    dynamics = BeanDynamics(config)
    new_position = dynamics.update_position(bean_state)
    expected_speed = dynamics.calculate_speed(bean_state)
    assert new_position == (1, 1 + expected_speed)


def test_bean_dynamics_direction_update():
    config = BeansConfig()
    bean_state = BeanState(age=2, position=(1, 1), direction=(0, 1))
    dynamics = BeanDynamics(config)
    new_direction = dynamics.update_direction(bean_state)
    assert new_direction == (0, 1)
