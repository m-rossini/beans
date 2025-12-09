
import pytest
from src.beans.dynamics.bean_dynamics import BeanDynamics
from src.beans.bean import BeanState
from config.loader import BeansConfig



def test_bean_dynamics_speed_calculation():
    config = BeansConfig(speed_min=0.1, speed_max=1.0, min_speed_factor=0.2)
    bean_state = BeanState(id=1, age=5, speed=1.0, energy=10.0, size=10.0, target_size=10.0, alive=True)
    dynamics = BeanDynamics(config)
    speed = dynamics.calculate_speed(bean_state)
    # Expected: max(min_speed, 1.0 - age * 0.01)
    assert speed == max(0.2, 1.0 - 5 * 0.01)
