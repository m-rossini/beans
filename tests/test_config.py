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
            "population_density": 0.5,
            "placement_strategy": "random"
        },
        "beans": {
            "max_bean_age": 100,
            "speed_min": -5,
            "speed_max": 5,
            "initial_bean_size": 10,
            "male_bean_color": "navy",
            "female_bean_color": "magenta"
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
        assert world_config.population_density == 0.5
        assert world_config.placement_strategy == "random"
        assert world_config.width == 800
        assert world_config.height == 600
        assert beans_config.max_bean_age == 100
        assert beans_config.speed_min == -5
        assert beans_config.speed_max == 5
        assert beans_config.initial_bean_size == 10
        assert beans_config.male_bean_color == "navy"
        assert beans_config.female_bean_color == "magenta"
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
        assert world_config.population_density == 0.1
        assert world_config.placement_strategy == "random"
        assert world_config.width == 800
        assert world_config.height == 600
        assert beans_config.max_bean_age == 1000
        assert beans_config.speed_min == -80.0
        assert beans_config.speed_max == 80.0
        assert beans_config.initial_bean_size == 5
        assert beans_config.male_bean_color == "blue"
        assert beans_config.female_bean_color == "red"
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


def test_load_config_beans_invalid_speed_zero_raises():
    # speed_min or speed_max zero should raise
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


def test_load_config_world_invalid_height_raises():
    # height <=0 should raise
    config_data = {"world": {"height": 0}, "beans": {}}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        import pytest
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)


def test_load_config_beans_invalid_initial_bean_size_raises():
    # initial_bean_size <=0 should raise
    config_data = {"world": {}, "beans": {"initial_bean_size": -1}}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        import pytest
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)


def test_load_config_world_invalid_population_density_raises():
    # population_density <=0 should raise
    config_data = {"world": {"population_density": 0}, "beans": {}}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        import pytest
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)


def test_load_config_world_invalid_male_female_ratio_raises():
    # male_female_ratio <=0 should raise
    config_data = {"world": {"male_female_ratio": -1}, "beans": {}}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        import pytest
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)


def test_load_config_beans_invalid_max_age_raises():
    # max_bean_age <0 should raise
    config_data = {"world": {}, "beans": {"max_bean_age": -1}}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        import pytest
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)


def test_load_config_beans_invalid_initial_energy_raises():
    # initial_energy <0 should raise
    config_data = {"world": {}, "beans": {"initial_energy": -10}}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        import pytest
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)


def test_load_config_beans_invalid_energy_gain_raises():
    # energy_gain_per_step <0 should raise
    config_data = {"world": {}, "beans": {"energy_gain_per_step": -1}}
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name
    try:
        import pytest
        with pytest.raises(ValueError):
            load_config(temp_file)
    finally:
        os.unlink(temp_file)


def test_load_config_beans_invalid_energy_cost_raises():
    # energy_cost_per_speed <0 should raise
    config_data = {"world": {}, "beans": {"energy_cost_per_speed": -0.1}}
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