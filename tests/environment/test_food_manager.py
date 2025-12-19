
import math

from beans.environment.food_manager import FoodType, HybridFoodManager
from config.loader import EnvironmentConfig, WorldConfig


def make_env_config():
    return EnvironmentConfig(food_quality="medium")


def make_world_config():
    return WorldConfig(
        male_sprite_color="blue",
        female_sprite_color="red",
        male_female_ratio=1.0,
        width=10,
        height=10,
        population_density=0.1,
        placement_strategy="random",
        population_estimator="density",
        energy_system="standard",
        environment="default",
        background_color="white",
        max_age_years=10,
        rounds_per_year=12,
        seed=None,
    )



def test_dead_bean_food_decay():
    fm = HybridFoodManager(make_world_config(), make_env_config())
    pos = (2, 2)
    size = 10.0
    fm.add_dead_bean_as_food(pos, size)
    # After 1st step: 50% left
    fm.step()
    food1 = fm.get_food_at(pos)
    assert math.isclose(food1.get(FoodType.DEAD_BEAN, 0.0), 5.0), f"Expected 5.0, got {food1.get(FoodType.DEAD_BEAN, 0.0)}"
    # After 2nd step: 50% of 5.0 left
    fm.step()
    food2 = fm.get_food_at(pos)
    assert math.isclose(food2.get(FoodType.DEAD_BEAN, 0.0), 2.5), f"Expected 2.5, got {food2.get(FoodType.DEAD_BEAN, 0.0)}"
    # After 3rd step: 50% of 2.5 left, then removed
    fm.step()
    food3 = fm.get_food_at(pos)
    assert food3.get(FoodType.DEAD_BEAN, 0.0) == 0.0, f"Expected 0.0, got {food3.get(FoodType.DEAD_BEAN, 0.0)}"

def test_grid_food_decay():
    fm = HybridFoodManager(make_world_config(), make_env_config())
    pos = (1, 1)
    # Directly manipulate grid for test (assume grid is public or provide a method for test)
    fm.grid[(1, 1)] = 20.0
    orig = 20.0
    fm.step()
    after1 = fm.get_food_at(pos)
    assert math.isclose(after1.get(FoodType.COMMON, 0.0), orig * 0.9), f"Expected {orig * 0.9}, got {after1.get(FoodType.COMMON, 0.0)}"
    fm.step()
    after2 = fm.get_food_at(pos)
    assert math.isclose(after2.get(FoodType.COMMON, 0.0), orig * 0.9 * 0.9), f"Expected {orig * 0.9 * 0.9}, got {after2.get(FoodType.COMMON, 0.0)}"

def test_initial_food_spawning_respects_occupied_positions_and_config():
    world_cfg = make_world_config()
    env_cfg = make_env_config()
    env_cfg.food_spawn_rate_per_round = 5
    env_cfg.food_max_energy = 10.0
    env_cfg.food_spawn_distribution = "random"
    fm = HybridFoodManager(world_cfg, env_cfg)
    occupied = {(2, 2), (3, 3), (4, 4)}
    fm.spawn_food(occupied)
    # Ensure no food spawned on occupied positions
    for pos in occupied:
        assert fm.get_food_at(pos).get(FoodType.COMMON, 0.0) == 0.0, f"Food spawned on occupied position {pos}"
    # Ensure correct number of food spawned
    spawned_positions = [pos for pos in fm.grid.keys() if pos not in occupied]
    assert len(spawned_positions) == env_cfg.food_spawn_rate_per_round, f"Expected {env_cfg.food_spawn_rate_per_round} food, got {len(spawned_positions)}"
    # Ensure food energy does not exceed max
    for pos in spawned_positions:
        assert fm.grid[pos] <= env_cfg.food_max_energy, f"Food energy at {pos} exceeds max energy"