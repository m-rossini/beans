from beans.world import World
from src.config.loader import DEFAULT_BEANS_CONFIG, DEFAULT_ENVIRONMENT_CONFIG, DEFAULT_WORLD_CONFIG


def test_world_calls_real_environment_step():
    w = World(DEFAULT_WORLD_CONFIG, DEFAULT_BEANS_CONFIG, DEFAULT_ENVIRONMENT_CONFIG)
    w.step(1.0)
    env_state = w.environment_state
    assert env_state.food_manager_state.total_food_count >= 0
    assert env_state.food_manager_state.total_food_energy >= 0.0
