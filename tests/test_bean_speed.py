from beans.world import World
from config.loader import BeansConfig, EnvironmentConfig, WorldConfig


def test_bean_speed_nonzero_after_5_rounds():
    beans_config = BeansConfig(speed_min=-5, speed_max=5, max_age_rounds=1000)
    world_config = WorldConfig(
        width=100,
        height=100,
        population_density=0.01,  # 4 beans
        male_female_ratio=1.0,
        max_age_years=100,
        rounds_per_year=10,
        placement_strategy="random",
        population_estimator="density",
        energy_system="standard",
        male_sprite_color=(0, 0, 255),
        female_sprite_color=(255, 0, 0)
    )
    env_cfg = EnvironmentConfig()
    world = World(world_config, beans_config, env_config=env_cfg)
    for _ in range(5):
        world.step(1.0)
    assert len(world.beans) > 0, "All beans died before round 5."
    for bean in world.beans:
        assert bean.speed != 0, f"Bean {bean.id} speed is still zero after 5 rounds: {bean.speed}"
