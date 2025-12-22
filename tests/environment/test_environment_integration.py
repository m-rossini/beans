from beans.world import World
from config.loader import load_config


class FakeEnv:
    def __init__(self) -> None:
        self.stepped = False
        self.energy = 3.14
        self.temp = 7.0

        class _FM:
            def __init__(self):
                self.stepped = False

            def step(self):
                self.stepped = True

        self.food_manager = _FM()

    def step(self) -> None:
        self.stepped = True

    # get_energy_intake method removed from World
        return self.energy

    def get_temperature(self) -> float:
        return self.temp


def test_world_calls_environment_step_and_delegates(tmp_path):
    world_cfg, beans_cfg, env_cfg = load_config("src/config/small.json")
    fake = FakeEnv()

    w = World(world_cfg, beans_cfg, env_cfg)
    w.environment = fake
    w.step(1.0)
    assert fake.stepped is True
