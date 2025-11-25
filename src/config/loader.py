import json
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class WorldConfig:
    male_sprite_color: str
    female_sprite_color: str
    male_female_ratio: float
    sprite_bean_size: int
    width: int
    height: int
    population_density: float
    placement_strategy: str
    population_estimator: str = "density"


@dataclass
class BeansConfig:
    max_bean_age: int
    speed_min: float
    speed_max: float
    initial_energy: float = 100.0
    energy_gain_per_step: float = 1.0
    energy_cost_per_speed: float = 0.1


DEFAULT_WORLD_CONFIG = WorldConfig(
    male_sprite_color="blue",
    female_sprite_color="red",
    male_female_ratio=1.0,
    sprite_bean_size=5,
    width=800,
    height=600,
    population_density=0.1,
    placement_strategy="random",
    population_estimator="density"
)

DEFAULT_BEANS_CONFIG = BeansConfig(
    max_bean_age=1000,
    speed_min=-80.0,
    speed_max=80.0,
    initial_energy=100.0,
    energy_gain_per_step=1.0,
    energy_cost_per_speed=0.1,
)

def load_config(config_file_path: str) -> tuple[WorldConfig, BeansConfig]:
    if not config_file_path or not os.path.exists(config_file_path):
        raise FileNotFoundError(f"Configuration file not found: {config_file_path}")

    with open(config_file_path, 'r') as f:
        data = json.load(f)

    world_data = data.get('world', {})
    beans_data = data.get('beans', {})

    world_config = WorldConfig(
        male_sprite_color=world_data.get('male_sprite_color', DEFAULT_WORLD_CONFIG.male_sprite_color),
        female_sprite_color=world_data.get('female_sprite_color', DEFAULT_WORLD_CONFIG.female_sprite_color),
        male_female_ratio=world_data.get('male_female_ratio', DEFAULT_WORLD_CONFIG.male_female_ratio),
        sprite_bean_size=world_data.get('sprite_bean_size', DEFAULT_WORLD_CONFIG.sprite_bean_size),
        width=world_data.get('width', DEFAULT_WORLD_CONFIG.width),
        height=world_data.get('height', DEFAULT_WORLD_CONFIG.height),
        population_density=world_data.get('population_density', DEFAULT_WORLD_CONFIG.population_density),
        placement_strategy=world_data.get('placement_strategy', DEFAULT_WORLD_CONFIG.placement_strategy),
        population_estimator=world_data.get('population_estimator', DEFAULT_WORLD_CONFIG.population_estimator)
    )

    beans_config = BeansConfig(
        max_bean_age=beans_data.get('max_bean_age', DEFAULT_BEANS_CONFIG.max_bean_age),
        speed_min=beans_data.get('speed_min', DEFAULT_BEANS_CONFIG.speed_min),
        speed_max=beans_data.get('speed_max', DEFAULT_BEANS_CONFIG.speed_max),
        initial_energy=beans_data.get('initial_energy', DEFAULT_BEANS_CONFIG.initial_energy),
        energy_gain_per_step=beans_data.get('energy_gain_per_step', DEFAULT_BEANS_CONFIG.energy_gain_per_step),
        energy_cost_per_speed=beans_data.get('energy_cost_per_speed', DEFAULT_BEANS_CONFIG.energy_cost_per_speed),
    )

    # Validate values — if invalid config values are present, fail fast (raise ValueError)
    def validate_world(cfg: WorldConfig) -> None:
        if cfg.width <= 0:
            raise ValueError(f"World width must be > 0, got {cfg.width}")
        if cfg.height <= 0:
            raise ValueError(f"World height must be > 0, got {cfg.height}")
        if cfg.sprite_bean_size <= 0:
            raise ValueError(f"Sprite size must be > 0, got {cfg.sprite_bean_size}")
        if cfg.population_density <= 0:
            raise ValueError(f"Population density must be >= 0, got {cfg.population_density}")
        if cfg.male_female_ratio <= 0:
            raise ValueError(f"Male/female ratio must be > 0, got {cfg.male_female_ratio}")

    def validate_beans(cfg: BeansConfig) -> None:
        if cfg.max_bean_age < 0:
            raise ValueError(f"Max bean age must be >= 0, got {cfg.max_bean_age}")
        if cfg.speed_min > cfg.speed_max:
            raise ValueError(f"speed_min ({cfg.speed_min}) cannot be greater than speed_max ({cfg.speed_max})")
        # Speeds cannot be zero, as zero speed is not allowed
        if cfg.speed_min == 0 or cfg.speed_max == 0:
            raise ValueError(f"speed_min and speed_max must be non-zero, got speed_min={cfg.speed_min}, speed_max={cfg.speed_max}")
        if cfg.initial_energy < 0:
            raise ValueError(f"initial_energy must be >= 0, got {cfg.initial_energy}")
        if cfg.energy_gain_per_step < 0:
            raise ValueError(f"energy_gain_per_step must be >= 0, got {cfg.energy_gain_per_step}")
        if cfg.energy_cost_per_speed < 0:
            raise ValueError(f"energy_cost_per_speed must be >= 0, got {cfg.energy_cost_per_speed}")

    validate_world(world_config)
    validate_beans(beans_config)

    return world_config, beans_config