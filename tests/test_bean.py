import math
import random
import logging

from beans.bean import Bean
# Keep BeansConfig import; no FrozenInstanceError expected
from config.loader import BeansConfig
from beans.bean import Sex
from beans.placement import RandomPlacementStrategy

logger = logging.getLogger(__name__)


def test_create_bean_default_values():
    b = Bean(config=BeansConfig(max_bean_age=100, speed_min=-5, speed_max=5), id=1, sex=Sex.MALE)
    assert b.age == 0.0


def test_bean_update_increments_age():
    b = Bean(config=BeansConfig(max_bean_age=100, speed_min=-5, speed_max=5), id=2, sex=Sex.FEMALE, speed=10.0)
    initial_age = b.age
    b.update(dt=1.0)
    assert b.age == initial_age + 1.0


def test_bean_mutable_fields():
    b = Bean(config=BeansConfig(max_bean_age=100, speed_min=-5, speed_max=5), id=3, sex=Sex.FEMALE)
    # Should be able to change attributes after creation
    b.age = 1.0
    assert b.age == 1.0


def test_random_placement_within_bounds():
    strategy = RandomPlacementStrategy()
    positions = strategy.place(5, width=100, height=100, size=10)
    assert len(positions) == 5
    for x, y in positions:
        assert 0.0 <= x <= 100.0
        assert 0.0 <= y <= 100.0
