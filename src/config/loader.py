import json
import logging
import os
from dataclasses import dataclass
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class WorldConfig:
    male_sprite_color: str           # Color for male bean sprites.
    female_sprite_color: str         # Color for female bean sprites.
    male_female_ratio: float         # Ratio of males to females in population.
    width: int                      # World width in pixels.
    height: int                     # World height in pixels.
    population_density: float        # Number of beans per area unit.
    placement_strategy: str          # Algorithm for initial bean placement.
    population_estimator: str = "density"  # Method for estimating initial population.
    energy_system: str = "standard"        # Energy system type used in simulation.
    background_color: str = "white"        # Background color of the world.
    max_age_years: int = 100               # Maximum bean age in years.
    rounds_per_year: int = 12              # Simulation rounds per year.
    seed: Optional[int] = None             # Optional seed for deterministic world RNG


@dataclass
class BeansConfig:
    speed_min: float                      # Minimum allowed bean speed (units/step).
    speed_max: float                      # Maximum allowed bean speed (units/step).
    max_age_rounds: int = 1200            # Maximum bean age in simulation rounds (ticks).
    initial_energy: float = 100.0         # Starting energy for each bean.
    energy_gain_per_step: float = 1.0     # Energy gained per simulation step.
    energy_cost_per_speed: float = 0.1    # Energy cost per unit speed per step.
    min_energy_efficiency: float = 0.3    # Minimum energy efficiency at extreme ages (0-1).
    min_speed_factor: float = 0.07        # Minimum speed factor at extreme ages (0-1).
    initial_bean_size: int = 5            # Starting size for beans (arbitrary units).
    min_bean_size: float = 3.0            # Minimum bean size before starvation (units).
    base_bean_size: float = 6.0           # Normal healthy adult bean size (units).
    max_bean_size: float = 16.0           # Maximum possible bean size (units).
    energy_baseline: float = 50.0         # Neutral metabolism energy line (energy units).
    male_bean_color: str = "blue"         # Color for male beans (rendering).
    female_bean_color: str = "red"        # Color for female beans (rendering).
    fat_gain_rate: float = 0.02           # Rate of fat storage from surplus energy (fraction per step).
    fat_burn_rate: float = 0.02           # Rate of fat burning from energy deficit (fraction per step).
    # Survival system configuration
    starvation_base_depletion: float = 1.0           # Base size units consumed per starvation tick
    starvation_depletion_multiplier: float = 1.0     # Multiplier applied when energy is <= 0
    enable_obesity_death: bool = False                # Toggle probabilistic obesity death
    obesity_death_probability: float = 0.0            # Probability of death when above obesity threshold
    obesity_threshold_factor: float = 1.0             # Threshold relative to max_bean_size to consider obese
    metabolism_base_burn: float = 0.01    # Basal metabolism burn rate per tick (energy units).
    energy_to_fat_ratio: float = 1.0      # Energy units required to store 1 unit of fat.
    fat_to_energy_ratio: float = 0.9      # Energy units recovered per unit of fat burned.
    energy_max_storage: float = 200.0     # Maximum circulating energy storage (not fat).
    size_sigma_frac: float = 0.15         # Fraction of target size used as sigma for z-score.
    size_penalty_above_k: float = 0.20    # Speed penalty factor when bean is overweight (z > 0).
    size_penalty_below_k: float = 0.15    # Speed penalty factor when bean is underweight (z < 0).
    size_penalty_min_above: float = 0.3   # Minimum speed multiplier when overweight.
    size_penalty_min_below: float = 0.4   # Minimum speed multiplier when underweight.
    pixels_per_unit_speed: float = 1.0    # Rendering scale: pixels per unit speed.
    energy_loss_on_bounce: float = 2.0    # Energy lost when bean bounces off a wall or obstacle.
    # Collision/damage configuration
    collision_enable: bool = True
    collision_base_damage: float = 5.0
    collision_damage_speed_factor: float = 0.05
    collision_min_damage: float = 0.5
    collision_damage_size_exponent: float = 1.0
    collision_damage_sex_factors: Tuple[float, float] = (1.05, 1.0)  # (FEMALE, MALE)


@dataclass
class EnvironmentConfig:
    cell_size: int = 20
    food_density: float = 0.0
    hazard_density: float = 0.0
    food_spawn_rate_per_round: float = 0.0
    hazard_spawn_rate_per_round: float = 0.0
    decomposition_rounds: int = 3
    decomposition_fraction_to_food: float = 0.5
    temp_min: float = 0.0
    temp_max: float = 100.0
    temperature_diffusion_rate: float = 0.1
    temperature_migration_vector: Tuple[float, float] = (0.0, 0.0)
    temperature_variability: float = 0.0
    temp_to_food_factor: float = 0.0
    temp_to_metabolic_penalty: float = 0.0
    hazard_decay_rate_per_hit: float = 1.0


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
    seed=None,
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
    # Survival defaults
    starvation_base_depletion=1.0,
    starvation_depletion_multiplier=1.0,
    enable_obesity_death=False,
    obesity_death_probability=0.0,
    obesity_threshold_factor=1.0,
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
    # Collision defaults
    collision_base_damage=5.0,
    collision_damage_speed_factor=0.05,
    collision_min_damage=0.5,
    collision_damage_sex_factors=(1.0, 1.0),
)

def load_config(config_file_path: str) -> tuple[WorldConfig, BeansConfig, EnvironmentConfig]:
    logger.info(f">>>> load_config called with config_file_path={config_file_path}")
    if not config_file_path or not os.path.exists(config_file_path):
        logger.error(f">> Configuration file not found: {config_file_path}")
        raise FileNotFoundError(f"Configuration file not found: {config_file_path}")

    with open(config_file_path, "r") as f:
        data = json.load(f)

    world_data = data.get("world", {})
    beans_data = data.get("beans", {})

    world_config = WorldConfig(
        male_sprite_color=world_data.get("male_sprite_color", DEFAULT_WORLD_CONFIG.male_sprite_color),
        female_sprite_color=world_data.get("female_sprite_color", DEFAULT_WORLD_CONFIG.female_sprite_color),
        male_female_ratio=world_data.get("male_female_ratio", DEFAULT_WORLD_CONFIG.male_female_ratio),
        width=world_data.get("width", DEFAULT_WORLD_CONFIG.width),
        height=world_data.get("height", DEFAULT_WORLD_CONFIG.height),
        population_density=world_data.get("population_density", DEFAULT_WORLD_CONFIG.population_density),
        placement_strategy=world_data.get("placement_strategy", DEFAULT_WORLD_CONFIG.placement_strategy),
        population_estimator=world_data.get("population_estimator", DEFAULT_WORLD_CONFIG.population_estimator),
        background_color=world_data.get("background_color", DEFAULT_WORLD_CONFIG.background_color),
        max_age_years=world_data.get("max_age_years", DEFAULT_WORLD_CONFIG.max_age_years),
        rounds_per_year=world_data.get("rounds_per_year", DEFAULT_WORLD_CONFIG.rounds_per_year),
        seed=world_data.get("seed", DEFAULT_WORLD_CONFIG.seed),
    )

    # Compute max_age_rounds from world config
    max_age_rounds = world_config.max_age_years * world_config.rounds_per_year

    beans_config = BeansConfig(
        speed_min=beans_data.get("speed_min", DEFAULT_BEANS_CONFIG.speed_min),
        speed_max=beans_data.get("speed_max", DEFAULT_BEANS_CONFIG.speed_max),
        max_age_rounds=max_age_rounds,
        initial_energy=beans_data.get("initial_energy", DEFAULT_BEANS_CONFIG.initial_energy),
        energy_gain_per_step=beans_data.get("energy_gain_per_step", DEFAULT_BEANS_CONFIG.energy_gain_per_step),
        energy_cost_per_speed=beans_data.get("energy_cost_per_speed", DEFAULT_BEANS_CONFIG.energy_cost_per_speed),
        min_energy_efficiency=beans_data.get("min_energy_efficiency", DEFAULT_BEANS_CONFIG.min_energy_efficiency),
        min_speed_factor=beans_data.get("min_speed_factor", DEFAULT_BEANS_CONFIG.min_speed_factor),
        initial_bean_size=beans_data.get("initial_bean_size", DEFAULT_BEANS_CONFIG.initial_bean_size),
        min_bean_size=beans_data.get("min_bean_size", DEFAULT_BEANS_CONFIG.min_bean_size),
        base_bean_size=beans_data.get("base_bean_size", DEFAULT_BEANS_CONFIG.base_bean_size),
        max_bean_size=beans_data.get("max_bean_size", DEFAULT_BEANS_CONFIG.max_bean_size),
        energy_baseline=beans_data.get("energy_baseline", DEFAULT_BEANS_CONFIG.energy_baseline),
        male_bean_color=beans_data.get("male_bean_color", DEFAULT_BEANS_CONFIG.male_bean_color),
        female_bean_color=beans_data.get("female_bean_color", DEFAULT_BEANS_CONFIG.female_bean_color),
        fat_gain_rate=beans_data.get("fat_gain_rate", DEFAULT_BEANS_CONFIG.fat_gain_rate),
        fat_burn_rate=beans_data.get("fat_burn_rate", DEFAULT_BEANS_CONFIG.fat_burn_rate),
        # Survival system fields
        starvation_base_depletion=beans_data.get("starvation_base_depletion", DEFAULT_BEANS_CONFIG.starvation_base_depletion),
        starvation_depletion_multiplier=beans_data.get("starvation_depletion_multiplier", DEFAULT_BEANS_CONFIG.starvation_depletion_multiplier),
        enable_obesity_death=beans_data.get("enable_obesity_death", DEFAULT_BEANS_CONFIG.enable_obesity_death),
        obesity_death_probability=beans_data.get("obesity_death_probability", DEFAULT_BEANS_CONFIG.obesity_death_probability),
        obesity_threshold_factor=beans_data.get("obesity_threshold_factor", DEFAULT_BEANS_CONFIG.obesity_threshold_factor),
        metabolism_base_burn=beans_data.get("metabolism_base_burn", DEFAULT_BEANS_CONFIG.metabolism_base_burn),
        energy_to_fat_ratio=beans_data.get("energy_to_fat_ratio", DEFAULT_BEANS_CONFIG.energy_to_fat_ratio),
        fat_to_energy_ratio=beans_data.get("fat_to_energy_ratio", DEFAULT_BEANS_CONFIG.fat_to_energy_ratio),
        energy_max_storage=beans_data.get("energy_max_storage", DEFAULT_BEANS_CONFIG.energy_max_storage),
        size_sigma_frac=beans_data.get("size_sigma_frac", DEFAULT_BEANS_CONFIG.size_sigma_frac),
        size_penalty_above_k=beans_data.get("size_penalty_above_k", DEFAULT_BEANS_CONFIG.size_penalty_above_k),
        size_penalty_below_k=beans_data.get("size_penalty_below_k", DEFAULT_BEANS_CONFIG.size_penalty_below_k),
        size_penalty_min_above=beans_data.get("size_penalty_min_above", DEFAULT_BEANS_CONFIG.size_penalty_min_above),
        size_penalty_min_below=beans_data.get("size_penalty_min_below", DEFAULT_BEANS_CONFIG.size_penalty_min_below),
        pixels_per_unit_speed=beans_data.get("pixels_per_unit_speed", DEFAULT_BEANS_CONFIG.pixels_per_unit_speed),
        collision_enable=beans_data.get("collision_enable", DEFAULT_BEANS_CONFIG.collision_enable),
        collision_base_damage=beans_data.get("collision_base_damage", DEFAULT_BEANS_CONFIG.collision_base_damage),
        collision_damage_speed_factor=beans_data.get("collision_damage_speed_factor", DEFAULT_BEANS_CONFIG.collision_damage_speed_factor),
        collision_min_damage=beans_data.get("collision_min_damage", DEFAULT_BEANS_CONFIG.collision_min_damage),
        collision_damage_size_exponent=beans_data.get("collision_damage_size_exponent", DEFAULT_BEANS_CONFIG.collision_damage_size_exponent),
        collision_damage_sex_factors=tuple(beans_data.get("collision_damage_sex_factors", DEFAULT_BEANS_CONFIG.collision_damage_sex_factors)),
        energy_loss_on_bounce=beans_data.get("energy_loss_on_bounce", DEFAULT_BEANS_CONFIG.energy_loss_on_bounce),
    )

    # Environment config
    env_data = data.get("environment", {})
    environment_config: EnvironmentConfig = EnvironmentConfig(
        cell_size=env_data.get("cell_size", 20),
        food_density=env_data.get("food_density", 0.0),
        hazard_density=env_data.get("hazard_density", 0.0),
        food_spawn_rate_per_round=env_data.get("food_spawn_rate_per_round", 0.0),
        hazard_spawn_rate_per_round=env_data.get("hazard_spawn_rate_per_round", 0.0),
        decomposition_rounds=env_data.get("decomposition_rounds", 3),
        decomposition_fraction_to_food=env_data.get("decomposition_fraction_to_food", 0.5),
        temp_min=env_data.get("temp_min", 0.0),
        temp_max=env_data.get("temp_max", 100.0),
        temperature_diffusion_rate=env_data.get("temperature_diffusion_rate", 0.1),
        temperature_migration_vector=tuple(env_data.get("temperature_migration_vector", (0.0, 0.0))),
        temperature_variability=env_data.get("temperature_variability", 0.0),
        temp_to_food_factor=env_data.get("temp_to_food_factor", 0.0),
        temp_to_metabolic_penalty=env_data.get("temp_to_metabolic_penalty", 0.0),
        hazard_decay_rate_per_hit=env_data.get("hazard_decay_rate_per_hit", 1.0),
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
        # Validate survival configuration
        if cfg.starvation_base_depletion < 0.0:
            raise ValueError(f"starvation_base_depletion must be >= 0.0, got {cfg.starvation_base_depletion}")
        if cfg.starvation_depletion_multiplier < 0.0:
            raise ValueError(f"starvation_depletion_multiplier must be >= 0.0, got {cfg.starvation_depletion_multiplier}")
        if not (0.0 <= cfg.obesity_death_probability <= 1.0):
            raise ValueError(f"obesity_death_probability must be between 0.0 and 1.0, got {cfg.obesity_death_probability}")
        if cfg.obesity_threshold_factor <= 0.0:
            raise ValueError(f"obesity_threshold_factor must be > 0.0, got {cfg.obesity_threshold_factor}")
        # Validate collision sex factors: must be a sequence of two numeric values (female, male)
        try:
            factors = tuple(cfg.collision_damage_sex_factors)
        except Exception:
            raise ValueError(f"collision_damage_sex_factors must be a sequence of two numbers, got {cfg.collision_damage_sex_factors}")
        if len(factors) != 2:
            raise ValueError(f"collision_damage_sex_factors must contain exactly two values (female, male), got {factors}")
        for v in factors:
            if not isinstance(v, (int, float)):
                raise ValueError(f"collision_damage_sex_factors values must be numeric, got {factors}")
            if v < 0.0:
                raise ValueError(f"collision_damage_sex_factors values must be >= 0.0, got {factors}")

    def validate_environment(cfg: EnvironmentConfig) -> None:
        if cfg.cell_size <= 0:
            raise ValueError(f"cell_size must be > 0, got {cfg.cell_size}")
        if cfg.food_density < 0.0:
            raise ValueError(f"food_density must be >= 0.0, got {cfg.food_density}")
        if cfg.hazard_density < 0.0:
            raise ValueError(f"hazard_density must be >= 0.0, got {cfg.hazard_density}")
        if not (0.0 <= cfg.decomposition_fraction_to_food <= 1.0):
            raise ValueError(f"decomposition_fraction_to_food must be between 0.0 and 1.0, got {cfg.decomposition_fraction_to_food}")
        # randomness control removed from environment config — handled at world creation

    logger.debug(">>>>> Validating world config")
    validate_world(world_config)
    logger.debug(f">>>>> World config validation passed, WorldConfig: {world_config}")

    logger.debug(">>>>> Validating beans config")
    validate_beans(beans_config)
    logger.debug(f">>>>> Beans config validation passed, BeansConfig: {beans_config}")

    logger.debug(">>>>> Validating environment config")
    validate_environment(environment_config)
    logger.debug(f">>>>> Environment config validation passed, EnvironmentConfig: {environment_config}")

    return world_config, beans_config, environment_config
