from src.beans.bean import Bean, Sex
from src.beans.environment.food_manager import FoodType, HybridFoodManager
from src.beans.genetics import create_phenotype, create_random_genotype
from src.config.loader import DEFAULT_BEANS_CONFIG, DEFAULT_ENVIRONMENT_CONFIG, DEFAULT_WORLD_CONFIG


class DummyCollisionSystem:
    def __init__(self, food_manager):
        self.food_manager = food_manager

    def bean_eats_food(self, bean, position):
        return self.food_manager.process_bean_food_collision(bean, position)

def make_bean(size=10.0, sex=Sex.MALE, id=1):
    beans_config = DEFAULT_BEANS_CONFIG
    genotype = create_random_genotype()
    phenotype = create_phenotype(beans_config, genotype)
    bean = Bean(beans_config, id, sex, genotype=genotype, phenotype=phenotype)
    state = bean.to_state()
    state.size = size
    state.target_size = size
    state.energy = 50.0
    bean.update_from_state(state)
    return bean

def test_bean_eats_food_increases_energy_and_decreases_food():
    # Setup food manager and bean
    food_manager = HybridFoodManager(DEFAULT_WORLD_CONFIG, DEFAULT_ENVIRONMENT_CONFIG)
    bean = make_bean(size=10.0, sex=Sex.MALE, id=1)
    position = (5, 5)
    # Place food at position
    food_manager.grid[position] = {'value': 20.0, 'type': FoodType.COMMON}
    # Simulate collision
    collision_system = DummyCollisionSystem(food_manager)
    gained = collision_system.bean_eats_food(bean, position)
    # Bean should gain energy, food should decrease
    assert gained > 0
    assert food_manager.grid[position]['value'] < 20.0
    # Bean's energy should increase by gained (simulate update)
    bean_state = bean.to_state()
    bean_state.energy += gained
    bean.update_from_state(bean_state)
    assert bean.to_state().energy > 50.0

def test_food_not_removed_immediately():
    food_manager = HybridFoodManager(DEFAULT_WORLD_CONFIG, DEFAULT_ENVIRONMENT_CONFIG)
    bean = make_bean(size=10.0, sex=Sex.MALE, id=2)
    position = (6, 6)
    food_manager.grid[position] = {'value': 5.0, 'type': FoodType.COMMON}
    collision_system = DummyCollisionSystem(food_manager)
    gained = collision_system.bean_eats_food(bean, position)
    # Even if food is depleted, it should not be removed until decay step
    food_manager.grid[position]['value'] = 0.0
    assert position in food_manager.grid
    # After decay step, food should be removed
    food_manager.step()
    assert position not in food_manager.grid
