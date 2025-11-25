from beans.population import (
    DensityPopulationEstimator,
    SoftLogPopulationEstimator,
    create_population_estimator_from_name,
)
from beans.world import World
from config.loader import WorldConfig, BeansConfig
import pytest


@pytest.mark.parametrize(
    "width,height,sprite_size,population_density,male_female_ratio",
    [
        (20, 20, 10, 1.0, 1.0),
        (1000, 1000, 5, 0.1, 1.0),
        (500, 500, 10, 0.01, 1.0),
    ],
)
def test_density_population_estimates_total_counts(
    width, height, sprite_size, population_density, male_female_ratio
):
    estimator = DensityPopulationEstimator()
    male, female = estimator.estimate(
        width=width,
        height=height,
        sprite_size=sprite_size,
        population_density=population_density,
        male_female_ratio=male_female_ratio,
    )
    total = int(width * height * population_density / max(1, sprite_size ** 2))
    assert male + female == total
    assert male == total // 2 or male == total - total // 2


@pytest.mark.parametrize(
    "ratio,expected_fraction",
    [
        (3.0, 3.0 / 4.0),
        (9.0, 9.0 / 10.0),
        (0.5, 0.5 / 1.5),
    ],
)
def test_density_population_handles_unbalanced_ratios(ratio, expected_fraction):
    estimator = DensityPopulationEstimator()
    male, female = estimator.estimate(
        width=100,
        height=100,
        sprite_size=5,
        population_density=0.1,
        male_female_ratio=ratio,
    )
    total = int(100 * 100 * 0.1 / (5 ** 2))
    assert male + female == total
    assert abs(male - int(total * expected_fraction)) <= 1


def test_population_estimator_factory_defaults_to_density():
    estimator = create_population_estimator_from_name('')
    assert isinstance(estimator, DensityPopulationEstimator)


def test_world_initialization_respects_density_and_ratio():
    cfg = WorldConfig(
        male_sprite_color='blue',
        female_sprite_color='red',
        male_female_ratio=3.0,
        width=20,
        height=20,
        population_density=1.0,
        placement_strategy='random',
    )
    bcfg = BeansConfig(max_bean_age=100, speed_min=-5, speed_max=5, initial_bean_size=10)
    world = World(config=cfg, beans_config=bcfg)
    total = 4
    assert len(world.beans) == total
    male_count = sum(1 for bean in world.beans if bean.is_male)
    female_count = total - male_count
    assert male_count == 3
    assert female_count == 1


def test_soft_log_estimator_never_exceeds_density():
    density = DensityPopulationEstimator()
    soft_log = SoftLogPopulationEstimator()
    params = dict(width=500, height=500, sprite_size=5, population_density=0.2, male_female_ratio=1.0)
    male_d, female_d = density.estimate(**params)
    male_s, female_s = soft_log.estimate(**params)

    assert male_s + female_s <= male_d + female_d
    assert male_s + female_s >= 1


def test_soft_log_estimator_reaches_density_maximum():
    density = DensityPopulationEstimator()
    soft_log = SoftLogPopulationEstimator()
    params = dict(width=5000, height=5000, sprite_size=1, population_density=1.0, male_female_ratio=2.0)
    male_d, female_d = density.estimate(**params)
    male_s, female_s = soft_log.estimate(**params)

    assert male_s + female_s == male_d + female_d


def test_population_estimator_factory_soft_log():
    estimator = create_population_estimator_from_name('soft_log')
    assert isinstance(estimator, SoftLogPopulationEstimator)


@pytest.mark.parametrize(
    "params",
    [
        dict(width=0, height=100, sprite_size=5, population_density=1.0, male_female_ratio=1.0),
        dict(width=100, height=100, sprite_size=5, population_density=0.0, male_female_ratio=1.0),
        dict(width=100, height=100, sprite_size=1000, population_density=0.0001, male_female_ratio=1.0),
    ],
)
def test_soft_log_estimator_handles_zero_capacity(params):
    estimator = SoftLogPopulationEstimator()
    male, female = estimator.estimate(**params)
    assert male == 0 and female == 0
