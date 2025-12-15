import json
import logging

import pytest

from beans.genetics import (
    Gene,
    Genotype,
    age_speed_factor,
    apply_age_gene_curve,
    create_random_genotype,
    genetic_max_age,
)
from config.loader import BeansConfig, load_config

logger = logging.getLogger(__name__)


def test_age_speed_factor_respects_min_speed(monkeypatch):
    """age_speed_factor should never return less than config min_speed_factor (now uses config)."""

    class DummyConfig:
        min_speed_factor = 0.07

    min_speed = DummyConfig.min_speed_factor
    max_age = 100
    # Test for newborn (age=0) and very young (age=1)
    assert age_speed_factor(0, max_age, min_speed) >= min_speed
    assert age_speed_factor(1, max_age, min_speed) >= min_speed


def test_beans_config_min_speed_factor_validation_loader(tmp_path):
    """Config loader should raise ValueError if min_speed_factor is out of [0,1]."""
    # Valid config
    valid = {
        "world": {
            "width": 10,
            "height": 10,
            "population_density": 0.1,
            "male_female_ratio": 1.0,
            "max_age_years": 1,
            "rounds_per_year": 1,
        },
        "beans": {"speed_min": -5, "speed_max": 5, "min_speed_factor": 0.0},
    }
    path = tmp_path / "valid.json"
    path.write_text(json.dumps(valid))
    load_config(str(path))
    # Invalid low
    invalid_low = valid.copy()
    invalid_low["beans"] = dict(valid["beans"], min_speed_factor=-0.1)
    path_low = tmp_path / "low.json"
    path_low.write_text(json.dumps(invalid_low))
    with pytest.raises(ValueError):
        load_config(str(path_low))
    # Invalid high
    invalid_high = valid.copy()
    invalid_high["beans"] = dict(valid["beans"], min_speed_factor=1.1)
    path_high = tmp_path / "high.json"
    path_high.write_text(json.dumps(invalid_high))
    with pytest.raises(ValueError):
        load_config(str(path_high))


@pytest.fixture
def beans_config():
    return BeansConfig(speed_min=-5, speed_max=5, max_age_rounds=1200, initial_bean_size=10)


class TestApplyAgeGeneCurve:
    """Tests for the logarithmic age gene curve transformation."""

    def test_raw_value_1_gives_1(self):
        """Raw value 1.0 should give 1.0 (full lifespan)."""
        assert apply_age_gene_curve(1.0) == 1.0

    def test_raw_value_0_gives_minimum(self):
        """Raw value 0.0 should give 0.1 (minimum 10% lifespan)."""
        assert apply_age_gene_curve(0.0) == 0.1

    def test_raw_value_half_gives_more_than_half(self):
        """Raw value 0.5 should give >0.5 due to logarithmic curve favoring longevity."""
        result = apply_age_gene_curve(0.5)
        assert result > 0.5
        assert result < 0.9

    def test_curve_is_monotonic(self):
        """Higher raw values should give higher transformed values."""
        values = [apply_age_gene_curve(x) for x in [0.0, 0.25, 0.5, 0.75, 1.0]]
        for i in range(len(values) - 1):
            assert values[i] < values[i + 1]


class TestGeneticMaxAge:
    """Tests for genetic_max_age with pre-transformed gene values."""

    def test_gene_value_1_gives_max_age(self, beans_config):
        """Gene value 1.0 (pre-transformed) gives 100% of max_age_rounds."""
        genotype = Genotype(
            genes={
                Gene.METABOLISM_SPEED: 0.5,
                Gene.MAX_GENETIC_SPEED: 0.5,
                Gene.FAT_ACCUMULATION: 0.5,
                Gene.MAX_GENETIC_AGE: 1.0,  # Already transformed
            }
        )
        result = genetic_max_age(beans_config, genotype)
        assert result == beans_config.max_age_rounds

    def test_gene_value_minimum_gives_10_percent(self, beans_config):
        """Gene value 0.1 (minimum from curve) gives 10% of max_age_rounds."""
        genotype = Genotype(
            genes={
                Gene.METABOLISM_SPEED: 0.5,
                Gene.MAX_GENETIC_SPEED: 0.5,
                Gene.FAT_ACCUMULATION: 0.5,
                Gene.MAX_GENETIC_AGE: 0.1,  # Minimum from apply_age_gene_curve(0.0)
            }
        )
        result = genetic_max_age(beans_config, genotype)
        assert result == beans_config.max_age_rounds * 0.1


class TestCreateRandomGenotype:
    """Tests for create_random_genotype applying age curve."""

    def test_max_genetic_age_is_at_least_minimum(self):
        """MAX_GENETIC_AGE should be at least 0.1 due to curve transformation."""
        for _ in range(20):
            genotype = create_random_genotype()
            assert genotype.genes[Gene.MAX_GENETIC_AGE] >= 0.1

    def test_max_genetic_age_is_at_most_1(self):
        """MAX_GENETIC_AGE should be at most 1.0."""
        for _ in range(20):
            genotype = create_random_genotype()
            assert genotype.genes[Gene.MAX_GENETIC_AGE] <= 1.0
