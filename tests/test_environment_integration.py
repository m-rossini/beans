from config.loader import load_config


class FakeEnv:
    def __init__(self) -> None:
        self.stepped = False
        self.energy = 3.14
        self.temp = 7.0

    def step(self) -> None:
        self.stepped = True

    def get_energy_intake(self) -> float:
        return self.energy

    def get_temperature(self) -> float:
        return self.temp


def test_world_calls_environment_step_and_delegates(tmp_path):
    world_cfg, beans_cfg, env_cfg = load_config("src/config/small.json")
    fake = FakeEnv()

    from beans.world import World

    w = World(world_cfg, beans_cfg, environment=fake)
    # Step should call environment.step()
    w.step(1.0)
    assert fake.stepped is True


def test_world_delegates_energy_and_temperature_to_environment(tmp_path):
    world_cfg, beans_cfg, env_cfg = load_config("src/config/small.json")
    fake = FakeEnv()

    from beans.world import World

    w = World(world_cfg, beans_cfg, environment=fake)
    assert w.get_energy_intake() == 3.14
    assert w.get_temperature() == 7.0
