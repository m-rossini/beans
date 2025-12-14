from beans.world import World
from config.loader import EnvironmentConfig, WorldConfig
from tests.test_energy import make_beans_config


def test_world_records_dead_bean_and_marks_bean_dead():
    world_cfg = WorldConfig(
        male_sprite_color="blue",
        female_sprite_color="red",
        male_female_ratio=1.0,
        width=100,
        height=100,
        population_density=0.01,
        placement_strategy="random",
        population_estimator="density",
    )
    beans_cfg = make_beans_config(
        initial_energy=1.0,
        energy_gain_per_step=0.0,
        energy_cost_per_speed=10.0,
        initial_bean_size=5,
    )

    env_cfg = EnvironmentConfig()
    world = World(config=world_cfg, beans_config=beans_cfg, env_config=env_cfg)
    for _ in range(10):
        world.step(dt=1.0)

    assert len(world.dead_beans) > 0
    assert all(not rec.bean.alive for rec in world.dead_beans)
