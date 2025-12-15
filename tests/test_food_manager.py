from beans.environment.food_manager import FoodManager
from config.loader import EnvironmentConfig


def test_food_manager_initial_population_and_spawn():
    env_cfg = EnvironmentConfig(cell_size=20, food_density=0.1, food_spawn_rate_per_round=0.05)

    fm = FoodManager(env_cfg, width=100, height=100)
    assert fm.food_count == int(25 * 0.1)

    fm.step()
    assert fm.food_count >= int(25 * 0.1) + 1


def test_food_consume_and_has():
    env_cfg = EnvironmentConfig(cell_size=10, food_density=0.2, food_spawn_rate_per_round=0.0)
    fm = FoodManager(env_cfg, width=40, height=20)
    assert fm.food_count == int(8 * 0.2)
    found = None
    for y in range(2):
        for x in range(4):
            if fm.has_food_at(x, y):
                found = (x, y)
                break
        if found:
            break

    assert found is not None
    x, y = found
    assert fm.consume(x, y) is True
    assert fm.has_food_at(x, y) is False
    assert fm.consume(x, y) is False
