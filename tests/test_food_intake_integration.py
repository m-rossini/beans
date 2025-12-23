import pytest

from src.beans.bean import Bean, Sex
from src.beans.environment.food_manager import FoodType, HybridFoodManager
from src.beans.genetics import create_phenotype, create_random_genotype
from src.config.loader import DEFAULT_BEANS_CONFIG, DEFAULT_ENVIRONMENT_CONFIG, DEFAULT_WORLD_CONFIG
from src.rendering.bean_sprite import BeanSprite
from src.rendering.movement import SpriteMovementSystem

# Integration test: movement system detects bean-food collision, world/subsystem applies energy

def make_bean_sprite(size=10.0, sex=Sex.MALE, id=1, x=5.0, y=5.0):
    beans_config = DEFAULT_BEANS_CONFIG
    genotype = create_random_genotype()
    phenotype = create_phenotype(beans_config, genotype)
    bean = Bean(beans_config, id, sex, genotype=genotype, phenotype=phenotype)
    state = bean.to_state()
    state.size = size
    state.target_size = size
    state.energy = 50.0
    bean.update_from_state(state)
    sprite = BeanSprite(bean=bean, position=(x, y), color=(0, 255, 0), direction=0.0)
    return sprite

def test_sprite_movement_detects_and_reports_food_collision(monkeypatch):
    # Setup food manager and sprite
    food_manager = HybridFoodManager(DEFAULT_WORLD_CONFIG, DEFAULT_ENVIRONMENT_CONFIG)
    sprite = make_bean_sprite(x=10.0, y=10.0)
    position = (10, 10)
    food_manager.grid[position] = {'value': 20.0, 'type': FoodType.COMMON}
    movement = SpriteMovementSystem()


    # Patch movement system to collect collision events
    collision_events = []
    def fake_report_collision(bean_id, food_pos):
        collision_events.append((bean_id, food_pos))
    movement.report_food_collision = fake_report_collision

    # Simulate movement tick: check for food collision
    movement.check_food_collision(sprite, food_manager.grid)

    # World/subsystem applies business logic
    for bean_id, food_pos in collision_events:
        energy = food_manager.consume_food_at_position(None, food_pos)
        sprite.bean._phenotype.energy += energy

    # Assert bean's energy increased and food's value decreased
    assert sprite.bean.energy > 50.0
    assert food_manager.grid[position]['value'] < 20.0
    # Assert food is not removed immediately
    assert position in food_manager.grid
    # After decay step, food should be removed
    food_manager.grid[position]['value'] = 0.0
    food_manager.step()
    assert position not in food_manager.grid
