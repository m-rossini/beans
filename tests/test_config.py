import pytest
import json
import tempfile
import os
from config.loader import load_config, WorldConfig, BeansConfig


def test_load_config_with_valid_file():
    # Create a temporary config file
    config_data = {
        "world": {
            "male_sprite_color": "blue",
            "female_sprite_color": "pink",
            "male_female_ratio": 1.0,
            "sprite_bean_size": 10,
            "population_density": 0.5,
            "placement_strategy": "random"
        },
        "beans": {
            "max_bean_age": 100,
            "speed_min": -5,
            "speed_max": 5
        }
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name

    try:
        world_config, beans_config = load_config(temp_file)
        assert world_config.male_sprite_color == "blue"
        assert world_config.female_sprite_color == "pink"
        assert world_config.male_female_ratio == 1.0
        assert world_config.sprite_bean_size == 10
        assert world_config.population_density == 0.5
        assert world_config.placement_strategy == "random"
        assert world_config.width == 800
        assert world_config.height == 600
        assert beans_config.max_bean_age == 100
        assert beans_config.speed_min == -5
        assert beans_config.speed_max == 5
    finally:
        os.unlink(temp_file)


def test_load_config_with_missing_keys_uses_defaults():
    config_data = {
        "world": {},
        "beans": {}
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name

    try:
        world_config, beans_config = load_config(temp_file)
        # Assert defaults
        assert world_config.male_sprite_color == "blue"
        assert world_config.female_sprite_color == "red"
        assert world_config.male_female_ratio == 1.0
        assert world_config.sprite_bean_size == 5
        assert world_config.population_density == 0.1
        assert world_config.placement_strategy == "random"
        assert world_config.width == 800
        assert world_config.height == 600
        assert beans_config.max_bean_age == 1000
        assert beans_config.speed_min == -80.0
        assert beans_config.speed_max == 80.0
    finally:
        os.unlink(temp_file)


def test_load_config_invalid_values_raise():
    # Negative width should raise
    config_data = {"world": {"width": -10, "height": 100, "sprite_bean_size": 5, "male_female_ratio": 1.0, "population_density": 0.1, "placement_strategy": "random"}, "beans": {}}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        import pytest
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)


def test_load_config_beans_invalid_speed_range_raises():
    # speed_min greater than speed_max should raise
    config_data = {"world": {}, "beans": {"max_bean_age": 100, "speed_min": 10, "speed_max": 5}}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        import pytest
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)


def test_load_config_beans_invalid_speed_zero_raises():
    # speed_min equal to zero should raise
    config_data = {"world": {}, "beans": {"max_bean_age": 100, "speed_min": 0, "speed_max": 5}}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        import pytest
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)

    # speed_max equal to zero should raise
    config_data = {"world": {}, "beans": {"max_bean_age": 100, "speed_min": -5, "speed_max": 0}}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        import pytest
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)