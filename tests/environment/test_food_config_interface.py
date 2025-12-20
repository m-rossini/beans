
from beans.environment.food_manager import HybridFoodManager
from config.loader import EnvironmentConfig, WorldConfig


def make_env_config():
    return EnvironmentConfig(
        name="testenv",
        cell_size=10,
        food_density=0.05,
        hazard_density=0.01,
        food_spawn_rate_per_round=0.2,
        hazard_spawn_rate_per_round=0.1,
        decomposition_rounds=2,
        decomposition_fraction_to_food=0.6,
        temp_min=5.0,
        temp_max=50.0,
        temperature_diffusion_rate=0.2,
        temperature_migration_vector=(1.0, 1.0),
        temperature_variability=0.1,
        temp_to_food_factor=0.3,
        temp_to_metabolic_penalty=0.2,
        hazard_decay_rate_per_hit=0.5,
        food_manager="hybrid",
        food_quality=2.0,
        food_max_energy=15.0,
        food_spawn_distribution="uniform",
        food_decay_rate=0.05
    )

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
        environment="testenv",
        background_color="white",
        max_age_years=10,
        rounds_per_year=12,
        seed=None,
    )

def test_environment_config_fields():
    cfg = make_env_config()
    assert cfg.food_quality == 2.0
    assert cfg.food_max_energy == 15.0
    assert cfg.food_spawn_distribution == "uniform"
    assert cfg.food_decay_rate == 0.05

