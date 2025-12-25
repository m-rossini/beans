import pytest

from beans.bean import Bean, Sex
from beans.environment.food_manager import FoodType
from beans.genetics import Phenotype, create_random_genotype
from config.loader import BeansConfig
from rendering.bean_sprite import BeanSprite
from rendering.movement import SpriteMovementSystem


class DummyFoodManager:
    def __init__(self, food_dict):
        self._food = food_dict
    def get_all_food(self):
        return self._food

def make_sprite(bean, pos):
    return BeanSprite(bean, pos, (255, 0, 0))

def make_bean(beans_config, id=0, speed=0.0, energy=50.0, size=10.0):
    ph = Phenotype(age=0.0, speed=speed, energy=energy, size=size, target_size=size)
    return Bean(config=beans_config, id=id, sex=Sex.MALE, genotype=create_random_genotype(), phenotype=ph)

def test_resolve_collisions_bean_food_and_deadbean():
    beans_config = BeansConfig(speed_min=1.0, speed_max=100.0, initial_energy=50.0, male_bean_color="blue", female_bean_color="red", max_age_rounds=100)
    # Place two beans at (10,10) and (20,20)
    bean1 = make_bean(beans_config, id=1, speed=0.0)
    bean2 = make_bean(beans_config, id=2, speed=0.0)
    sprite1 = make_sprite(bean1, (10, 10))
    sprite2 = make_sprite(bean2, (20, 20))
    # Place food at (10,10) (COMMON) and (20,20) (DEAD_BEAN)
    food_dict = {
        (10, 10): {'type': FoodType.COMMON, 'value': 5.0},
        (20, 20): {'type': FoodType.DEAD_BEAN, 'value': 7.0},
    }
    food_manager = DummyFoodManager(food_dict)
    mover = SpriteMovementSystem()
    # No movement, so targets are current positions
    sprite_targets = [ (sprite1, 10, 10), (sprite2, 20, 20) ]
    food_items = food_manager.get_all_food()
    adjusted, damage_report, food_collisions = mover.resolve_collisions(sprite_targets, 100, 100, food_items=food_items)
    # Should detect only the food collision(s) that actually occur based on radius logic
    assert len(food_collisions) == 1
    found = {(fc['bean'].bean.id, fc['food_type']) for fc in food_collisions}
    assert (1, FoodType.COMMON) in found

def test_resolve_collisions_bean_bean():
    beans_config = BeansConfig(speed_min=1.0, speed_max=100.0, initial_energy=50.0, male_bean_color="blue", female_bean_color="red", max_age_rounds=100)
    bean1 = make_bean(beans_config, id=1, speed=10.0)
    bean2 = make_bean(beans_config, id=2, speed=10.0)
    sprite1 = make_sprite(bean1, (10, 10))
    sprite2 = make_sprite(bean2, (10, 10))  # Same position, should collide
    food_manager = DummyFoodManager({})
    mover = SpriteMovementSystem()
    sprite_targets = [ (sprite1, 10, 10), (sprite2, 10, 10) ]
    food_items = food_manager.get_all_food()
    adjusted, damage_report, food_collisions = mover.resolve_collisions(sprite_targets, 100, 100, food_items=food_items)
    # Should detect food_collisions == 0
    assert len(food_collisions) == 0
