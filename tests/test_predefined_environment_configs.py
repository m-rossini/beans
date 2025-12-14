from config.loader import load_config
import pytest


def test_small_config_parses_environment(tmp_path):
    cfg_path = "src/config/small.json"
    world_cfg, beans_cfg, env_cfg = load_config(cfg_path)
    assert env_cfg.random_mode == "random"
    assert env_cfg.food_density >= 0.0


def test_medium_config_parses_seeded(tmp_path):
    cfg_path = "src/config/medium.json"
    world_cfg, beans_cfg, env_cfg = load_config(cfg_path)
    assert env_cfg.random_mode == "seeded"
    assert env_cfg.environment_seed == 42


def test_large_config_parses_explicit_grid(tmp_path):
    cfg_path = "src/config/large.json"
    world_cfg, beans_cfg, env_cfg = load_config(cfg_path)
    assert env_cfg.random_mode == "explicit"
    assert isinstance(env_cfg.explicit_food, list)
    assert isinstance(env_cfg.explicit_temperature_grid, list)
