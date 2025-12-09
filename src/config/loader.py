import json
import os
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class WorldConfig:
    male_sprite_color: str
    female_sprite_color: str
    male_female_ratio: float
    width: int
    height: int
    population_density: float
    placement_strategy: str
    population_estimator: str = "density"
    energy_system: str = "standard"
    background_color: str = "white"
    max_age_years: int = 100
    rounds_per_year: int = 12


@dataclass
class BeansConfig:
    speed_min: float
    speed_max: float
    max_age_rounds: int = 1200       # computed from world.max_age_years * world.rounds_per_year
    initial_energy: float = 100.0
    energy_gain_per_step: float = 1.0
    energy_cost_per_speed: float = 0.1
    min_energy_efficiency: float = 0.3  # floor for age-based energy efficiency (0.3 = 30%)
    min_speed_factor: float = 0.07      # NEW: minimum speed factor for age_speed_factor
    initial_bean_size: int = 5
    min_bean_size: float = 3.0       # starvation death
    base_bean_size: float = 6.0      # normal healthy adult
    max_bean_size: float = 16.0      # absolute physical limit
    energy_baseline: float = 50.0    # neutral metabolism line
    male_bean_color: str = "blue"
    female_bean_color: str = "red"
    # Energy system configuration fields (from spec)
    fat_gain_rate: float = 0.02           # rate of fat storage from surplus energy
    fat_burn_rate: float = 0.02           # rate of fat burning from energy deficit
    metabolism_base_burn: float = 0.01    # basal metabolism burn rate per tick
    energy_to_fat_ratio: float = 1.0      # energy units consumed per fat unit stored
    fat_to_energy_ratio: float = 0.9      # energy units recovered per fat unit burned
    energy_max_storage: float = 200.0     # maximum circulating energy storage
    size_sigma_frac: float = 0.15         # sigma fraction for z-score calculation
    size_penalty_above_k: float = 0.20    # penalty factor when overweight
    size_penalty_below_k: float = 0.15    # penalty factor when underweight
    size_penalty_min_above: float = 0.3   # minimum speed multiplier when overweight
    size_penalty_min_below: float = 0.4   # minimum speed multiplier when underweight
    # Movement and bounce configuration (rendering layer)
    pixels_per_unit_speed: float = 1.0
    energy_loss_on_bounce: float = 2.0


DEFAULT_WORLD_CONFIG = WorldConfig(
    male_sprite_color="blue",
    female_sprite_color="red",
    male_female_ratio=1.0,
    width=800,
    height=600,
    population_density=0.1,
    placement_strategy="random",
    population_estimator="density",
    energy_system="standard",
    background_color="white",
    max_age_years=100,
    rounds_per_year=12,
)

DEFAULT_BEANS_CONFIG = BeansConfig(
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
    # Energy system configuration fields (from spec)
    fat_gain_rate=0.02,
    fat_burn_rate=0.02,
    metabolism_base_burn=0.01,
    energy_to_fat_ratio=1.0,
    fat_to_energy_ratio=0.9,
    energy_max_storage=200.0,
    size_sigma_frac=0.15,
    size_penalty_above_k=0.20,
    size_penalty_below_k=0.15,
    size_penalty_min_above=0.3,
    size_penalty_min_below=0.4,
    # Movement defaults
    pixels_per_unit_speed=1.0,
    energy_loss_on_bounce=2.0,
)

def load_config(config_file_path: str) -> tuple[WorldConfig, BeansConfig]:
    logger.info(f">>>>> load_config called with config_file_path={config_file_path}")
    if not config_file_path or not os.path.exists(config_file_path):
        logger.error(f"Configuration file not found: {config_file_path}")
        raise FileNotFoundError(f"Configuration file not found: {config_file_path}")

    with open(config_file_path, 'r') as f:
        data = json.load(f)

    world_data = data.get('world', {})
    beans_data = data.get('beans', {})

    world_config = WorldConfig(
        male_sprite_color=world_data.get('male_sprite_color', DEFAULT_WORLD_CONFIG.male_sprite_color),
        female_sprite_color=world_data.get('female_sprite_color', DEFAULT_WORLD_CONFIG.female_sprite_color),
        male_female_ratio=world_data.get('male_female_ratio', DEFAULT_WORLD_CONFIG.male_female_ratio),
        width=world_data.get('width', DEFAULT_WORLD_CONFIG.width),
        height=world_data.get('height', DEFAULT_WORLD_CONFIG.height),
        population_density=world_data.get('population_density', DEFAULT_WORLD_CONFIG.population_density),
        placement_strategy=world_data.get('placement_strategy', DEFAULT_WORLD_CONFIG.placement_strategy),
        population_estimator=world_data.get('population_estimator', DEFAULT_WORLD_CONFIG.population_estimator),
        background_color=world_data.get('background_color', DEFAULT_WORLD_CONFIG.background_color),
        max_age_years=world_data.get('max_age_years', DEFAULT_WORLD_CONFIG.max_age_years),
        rounds_per_year=world_data.get('rounds_per_year', DEFAULT_WORLD_CONFIG.rounds_per_year),
    )

    # Compute max_age_rounds from world config
    max_age_rounds = world_config.max_age_years * world_config.rounds_per_year

    beans_config = BeansConfig(
        speed_min=beans_data.get('speed_min', DEFAULT_BEANS_CONFIG.speed_min),
        speed_max=beans_data.get('speed_max', DEFAULT_BEANS_CONFIG.speed_max),
        max_age_rounds=max_age_rounds,
        initial_energy=beans_data.get('initial_energy', DEFAULT_BEANS_CONFIG.initial_energy),
        energy_gain_per_step=beans_data.get('energy_gain_per_step', DEFAULT_BEANS_CONFIG.energy_gain_per_step),
        energy_cost_per_speed=beans_data.get('energy_cost_per_speed', DEFAULT_BEANS_CONFIG.energy_cost_per_speed),
        min_energy_efficiency=beans_data.get('min_energy_efficiency', DEFAULT_BEANS_CONFIG.min_energy_efficiency),
        min_speed_factor=beans_data.get('min_speed_factor', DEFAULT_BEANS_CONFIG.min_speed_factor),
        initial_bean_size=beans_data.get('initial_bean_size', DEFAULT_BEANS_CONFIG.initial_bean_size),
        min_bean_size=beans_data.get('min_bean_size', DEFAULT_BEANS_CONFIG.min_bean_size),
        base_bean_size=beans_data.get('base_bean_size', DEFAULT_BEANS_CONFIG.base_bean_size),
        max_bean_size=beans_data.get('max_bean_size', DEFAULT_BEANS_CONFIG.max_bean_size),
        energy_baseline=beans_data.get('energy_baseline', DEFAULT_BEANS_CONFIG.energy_baseline),
        male_bean_color=beans_data.get('male_bean_color', DEFAULT_BEANS_CONFIG.male_bean_color),
        female_bean_color=beans_data.get('female_bean_color', DEFAULT_BEANS_CONFIG.female_bean_color),
        fat_gain_rate=beans_data.get('fat_gain_rate', DEFAULT_BEANS_CONFIG.fat_gain_rate),
        fat_burn_rate=beans_data.get('fat_burn_rate', DEFAULT_BEANS_CONFIG.fat_burn_rate),
        metabolism_base_burn=beans_data.get('metabolism_base_burn', DEFAULT_BEANS_CONFIG.metabolism_base_burn),
        energy_to_fat_ratio=beans_data.get('energy_to_fat_ratio', DEFAULT_BEANS_CONFIG.energy_to_fat_ratio),
        fat_to_energy_ratio=beans_data.get('fat_to_energy_ratio', DEFAULT_BEANS_CONFIG.fat_to_energy_ratio),
        energy_max_storage=beans_data.get('energy_max_storage', DEFAULT_BEANS_CONFIG.energy_max_storage),
        size_sigma_frac=beans_data.get('size_sigma_frac', DEFAULT_BEANS_CONFIG.size_sigma_frac),
        size_penalty_above_k=beans_data.get('size_penalty_above_k', DEFAULT_BEANS_CONFIG.size_penalty_above_k),
        size_penalty_below_k=beans_data.get('size_penalty_below_k', DEFAULT_BEANS_CONFIG.size_penalty_below_k),
        size_penalty_min_above=beans_data.get('size_penalty_min_above', DEFAULT_BEANS_CONFIG.size_penalty_min_above),
        size_penalty_min_below=beans_data.get('size_penalty_min_below', DEFAULT_BEANS_CONFIG.size_penalty_min_below),
        pixels_per_unit_speed=beans_data.get('pixels_per_unit_speed', DEFAULT_BEANS_CONFIG.pixels_per_unit_speed),
        energy_loss_on_bounce=beans_data.get('energy_loss_on_bounce', DEFAULT_BEANS_CONFIG.energy_loss_on_bounce),
    )

    # Validate values — if invalid config values are present, fail fast (raise ValueError)
    def validate_world(cfg: WorldConfig) -> None:
        if cfg.width <= 0:
            raise ValueError(f"World width must be > 0, got {cfg.width}")
        if cfg.height <= 0:
            raise ValueError(f"World height must be > 0, got {cfg.height}")
        if cfg.population_density <= 0:
            raise ValueError(f"Population density must be >= 0, got {cfg.population_density}")
        if cfg.male_female_ratio <= 0:
            raise ValueError(f"Male/female ratio must be > 0, got {cfg.male_female_ratio}")
        if cfg.max_age_years <= 0:
            raise ValueError(f"max_age_years must be > 0, got {cfg.max_age_years}")
        if cfg.rounds_per_year <= 0:
            raise ValueError(f"rounds_per_year must be > 0, got {cfg.rounds_per_year}")

    def validate_beans(cfg: BeansConfig) -> None:
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
        if cfg.initial_bean_size <= 0:
            raise ValueError(f"initial_bean_size must be > 0, got {cfg.initial_bean_size}")
        if cfg.pixels_per_unit_speed <= 0:
            raise ValueError(f"pixels_per_unit_speed must be > 0, got {cfg.pixels_per_unit_speed}")
        if cfg.energy_loss_on_bounce < 0:
            raise ValueError(f"energy_loss_on_bounce must be >= 0, got {cfg.energy_loss_on_bounce}")
        if not (0.0 <= cfg.min_speed_factor <= 1.0):
            raise ValueError(f"min_speed_factor must be between 0.0 and 1.0, got {cfg.min_speed_factor}")

    logger.debug(">>>>> Validating world config")
    validate_world(world_config)
    logger.debug(f">>>>> World config validation passed, WorldConfig: {world_config}")
    
    logger.debug(">>>>> Validating beans config")
    validate_beans(beans_config)
    logger.debug(f">>>>> Beans config validation passed, BeansConfig: {beans_config}")

    return world_config, beans_config