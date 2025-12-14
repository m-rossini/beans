import json
import logging
import os
import tempfile

import pytest

from config.loader import DEFAULT_BEANS_CONFIG, load_config

logger = logging.getLogger(__name__)


def test_load_config_with_valid_file():
    # Create a temporary config file
    config_data = {
        "world": {
            "male_sprite_color": "blue",
            "female_sprite_color": "pink",
            "male_female_ratio": 1.0,
            "population_density": 0.5,
            "placement_strategy": "random",
        },
        "beans": {
            "speed_min": -5,
            "speed_max": 5,
            "initial_bean_size": 10,
            "male_bean_color": "navy",
            "female_bean_color": "magenta",
        },
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name

    try:
        world_config, beans_config, env_config = load_config(temp_file)
        assert world_config.male_sprite_color == "blue"
        assert world_config.female_sprite_color == "pink"
        assert world_config.male_female_ratio == 1.0
        assert world_config.population_density == 0.5
        assert world_config.placement_strategy == "random"
        assert world_config.width == 800
        assert world_config.height == 600
        assert beans_config.speed_min == -5
        assert beans_config.speed_max == 5
        assert beans_config.initial_bean_size == 10
        assert beans_config.male_bean_color == "navy"
        assert beans_config.female_bean_color == "magenta"
    finally:
        os.unlink(temp_file)


def test_load_config_invalid_values_raise():
    # Negative width should raise
    config_data = {
        "world": {
            "width": -10,
            "height": 100,
            "sprite_bean_size": 5,
            "male_female_ratio": 1.0,
            "population_density": 0.1,
            "placement_strategy": "random",
        },
        "beans": {},
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)


# Duplicate test for zero speed values removed; comprehensive checks exist later.


def test_load_config_world_invalid_height_raises():
    # height <=0 should raise
    config_data = {"world": {"height": 0}, "beans": {}}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)


def test_load_config_beans_invalid_initial_bean_size_raises():
    # initial_bean_size <=0 should raise
    config_data = {"world": {}, "beans": {"initial_bean_size": -1}}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)


def test_load_config_world_invalid_population_density_raises():
    # population_density <=0 should raise
    config_data = {"world": {"population_density": 0}, "beans": {}}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)


def test_load_config_world_invalid_male_female_ratio_raises():
    # male_female_ratio <=0 should raise
    config_data = {"world": {"male_female_ratio": -1}, "beans": {}}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)


def test_load_config_beans_invalid_initial_energy_raises():
    # initial_energy <0 should raise
    config_data = {"world": {}, "beans": {"initial_energy": -10}}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)


def test_load_config_beans_invalid_energy_gain_raises():
    # energy_gain_per_step <0 should raise
    config_data = {"world": {}, "beans": {"energy_gain_per_step": -1}}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)


def test_load_config_beans_invalid_energy_cost_raises():
    # energy_cost_per_speed <0 should raise
    config_data = {"world": {}, "beans": {"energy_cost_per_speed": -0.1}}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)


def test_load_config_beans_invalid_speed_zero_raises():
    # speed_min equal to zero should raise
    config_data = {"world": {}, "beans": {"speed_min": 0, "speed_max": 5}}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)

    # speed_max equal to zero should raise
    config_data = {"world": {}, "beans": {"speed_min": -5, "speed_max": 0}}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)


class TestEnergySystemConfigFields:
    """Tests for energy system configuration fields from spec."""

    def test_beans_config_has_fat_gain_rate(self):
        """BeansConfig should have fat_gain_rate with default 0.02."""
        assert DEFAULT_BEANS_CONFIG.fat_gain_rate == 0.02

    def test_beans_config_has_fat_burn_rate(self):
        """BeansConfig should have fat_burn_rate with default 0.02."""
        assert DEFAULT_BEANS_CONFIG.fat_burn_rate == 0.02

    def test_beans_config_has_metabolism_base_burn(self):
        """BeansConfig should have metabolism_base_burn with default 0.01."""
        assert DEFAULT_BEANS_CONFIG.metabolism_base_burn == 0.01

    def test_beans_config_has_energy_to_fat_ratio(self):
        """BeansConfig should have energy_to_fat_ratio with default 1.0."""
        assert DEFAULT_BEANS_CONFIG.energy_to_fat_ratio == 1.0

    def test_beans_config_has_fat_to_energy_ratio(self):
        """BeansConfig should have fat_to_energy_ratio with default 0.9."""
        assert DEFAULT_BEANS_CONFIG.fat_to_energy_ratio == 0.9

    def test_beans_config_has_energy_max_storage(self):
        """BeansConfig should have energy_max_storage with default 200.0."""
        assert DEFAULT_BEANS_CONFIG.energy_max_storage == 200.0

    def test_beans_config_has_size_sigma_frac(self):
        """BeansConfig should have size_sigma_frac with default 0.15."""
        assert DEFAULT_BEANS_CONFIG.size_sigma_frac == 0.15

    def test_beans_config_has_size_penalty_above_k(self):
        """BeansConfig should have size_penalty_above_k with default 0.20."""
        assert DEFAULT_BEANS_CONFIG.size_penalty_above_k == 0.20

    def test_beans_config_has_size_penalty_below_k(self):
        """BeansConfig should have size_penalty_below_k with default 0.15."""
        assert DEFAULT_BEANS_CONFIG.size_penalty_below_k == 0.15

    def test_beans_config_has_size_penalty_min_above(self):
        """BeansConfig should have size_penalty_min_above with default 0.3."""
        assert DEFAULT_BEANS_CONFIG.size_penalty_min_above == 0.3

    def test_beans_config_has_size_penalty_min_below(self):
        """BeansConfig should have size_penalty_min_below with default 0.4."""
        assert DEFAULT_BEANS_CONFIG.size_penalty_min_below == 0.4
