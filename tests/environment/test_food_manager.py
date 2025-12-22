
import math
import pytest
from beans.environment.food_manager import FoodType
from beans.environment.environment import create_environment_from_name
from beans.environment.food_manager import create_food_manager_from_name
from config.loader import EnvironmentConfig, WorldConfig, BeansConfig


def make_env_config():
    return EnvironmentConfig(food_quality=5)


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

def make_beans_config():
    return BeansConfig(
        speed_min=-80.0,
        speed_max=80.0,
        max_age_rounds=1200,
        initial_energy=100.0,
        energy_gain_per_step=1.0,
        energy_cost_per_speed=0.1,
        min_energy_efficiency=0.3,
        min_speed_factor=0.07,
        initial_bean_size=5,
        min_bean_size=3.0,
        base_bean_size=6.0,
        max_bean_size=16.0,
        energy_baseline=50.0,
        male_bean_color="blue",
        female_bean_color="red",
        fat_gain_rate=0.02,
        fat_burn_rate=0.02,
        starvation_base_depletion=1.0,
        starvation_depletion_multiplier=1.0,
    )



def test_dead_bean_food_decay():
    world_cfg = make_world_config()
    env_cfg = make_env_config()
    beans_cfg = make_beans_config()
    food_manager = create_food_manager_from_name(env_config=env_cfg, world_config=world_cfg)
    env = create_environment_from_name(world_cfg, env_cfg, beans_cfg, food_manager)
    pos = (2, 2)
    size = 10.0
    env.food_manager.add_dead_bean_as_food(pos, size)
    # After 1st step: 50% left
    env.step()
    food1 = env.food_manager.get_food_at(pos)
    assert math.isclose(food1.get(FoodType.DEAD_BEAN, 0.0), 5.0), f"Expected 5.0, got {food1.get(FoodType.DEAD_BEAN, 0.0)}"
    # After 2nd step: 50% of 5.0 left
    env.step()
    food2 = env.food_manager.get_food_at(pos)
    assert math.isclose(food2.get(FoodType.DEAD_BEAN, 0.0), 2.5), f"Expected 2.5, got {food2.get(FoodType.DEAD_BEAN, 0.0)}"
    # After 3rd step: 50% of 2.5 left, then removed
    env.step()
    food3 = env.food_manager.get_food_at(pos)
    assert food3.get(FoodType.DEAD_BEAN, 0.0) == 0.0, f"Expected 0.0, got {food3.get(FoodType.DEAD_BEAN, 0.0)}"

def test_grid_food_decay():
    world_cfg = make_world_config()
    env_cfg = make_env_config()
    beans_cfg = make_beans_config()
    food_manager = create_food_manager_from_name(env_config=env_cfg, world_config=world_cfg)
    env = create_environment_from_name(world_cfg, env_cfg, beans_cfg, food_manager)
    pos = (1, 1)
    # Directly manipulate grid for test (assume grid is public or provide a method for test)
    env.food_manager.grid[(1, 1)] = {'value': 20.0, 'type': FoodType.COMMON}
    orig = 20.0
    env.step()
    after1 = env.food_manager.get_food_at(pos)
    assert math.isclose(after1.get(FoodType.COMMON, 0.0), orig * 0.9), f"Expected {orig * 0.9}, got {after1.get(FoodType.COMMON, 0.0)}"
    env.step()
    after2 = env.food_manager.get_food_at(pos)
    assert math.isclose(after2.get(FoodType.COMMON, 0.0), orig * 0.9 * 0.9), f"Expected {orig * 0.9 * 0.9}, got {after2.get(FoodType.COMMON, 0.0)}"



@pytest.mark.parametrize("distribution", ["random", "clustered"])
def test_food_spawning_interface_only(distribution):
    world_cfg = make_world_config()
    env_cfg = make_env_config()
    env_cfg.food_density = 0.005
    env_cfg.food_quality = 5
    env_cfg.food_max_energy = 10.0
    env_cfg.food_spawn_distribution = distribution
    beans_cfg = make_beans_config()
    food_manager = create_food_manager_from_name(env_config=env_cfg, world_config=world_cfg)
    env = create_environment_from_name(world_cfg, env_cfg, beans_cfg, food_manager)
    # Simulate a step to trigger food spawning
    env.step()
    # Ensure no food spawned on occupied positions (simulate with empty occupied set)
    occupied = {(2, 2), (3, 3), (4, 4)}
    for pos in occupied:
        assert env.food_manager.get_food_at(pos).get(FoodType.COMMON, 0.0) == 0.0, f"Food spawned on occupied position {pos}"
    # Count total food pixels and energy via public interface
    total_pixels = 0
    total_energy = 0.0
    for x in range(world_cfg.width):
        for y in range(world_cfg.height):
            food = env.food_manager.get_food_at((x, y)).get(FoodType.COMMON, 0.0)
            if food > 0:
                total_pixels += 1
                total_energy += food
    # Expected food count and pixels
    food_count = int(env_cfg.food_density * world_cfg.width * world_cfg.height)
    expected_pixels = food_count * 4
    assert total_pixels == expected_pixels, f"Expected {expected_pixels} food pixels, got {total_pixels}"
    # Ensure food energy does not exceed max
    for x in range(world_cfg.width):
        for y in range(world_cfg.height):
            food = env.food_manager.get_food_at((x, y)).get(FoodType.COMMON, 0.0)
            assert food <= env_cfg.food_max_energy


@pytest.mark.parametrize("distribution", ["random", "clustered"])
@pytest.mark.parametrize("steps", [1, 2, 3])
def test_food_spawning_stepwise_decay(distribution, steps):
    world_cfg = make_world_config()
    env_cfg = make_env_config()
    env_cfg.food_density = 0.005
    env_cfg.food_quality = 5
    env_cfg.food_max_energy = 10.0
    env_cfg.food_spawn_distribution = distribution
    beans_cfg = make_beans_config()
    food_manager = create_food_manager_from_name(env_config=env_cfg, world_config=world_cfg)
    env = create_environment_from_name(world_cfg, env_cfg, beans_cfg, food_manager)
    # Simulate a step to trigger food spawning
    env.step()
    # Record initial food map
    initial_map = {}
    for x in range(world_cfg.width):
        for y in range(world_cfg.height):
            val = env.food_manager.get_food_at((x, y)).get(FoodType.COMMON, 0.0)
            if val > 0:
                initial_map[(x, y)] = val
    # Step simulation and check decay
    for _ in range(steps):
        env.step()
    for pos, initial_val in initial_map.items():
        val = env.food_manager.get_food_at(pos).get(FoodType.COMMON, 0.0)
        # Decay is 0.9 per step
        expected = initial_val * (0.9 ** steps)
        assert math.isclose(val, expected, rel_tol=1e-5), f"At {pos}: expected {expected}, got {val}"