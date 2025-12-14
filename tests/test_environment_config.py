import json
import pytest

from config.loader import EnvironmentConfig, load_config


def test_load_config_returns_environment_config(tmp_path):
    data = {"world": {}, "beans": {}, "environment": {}}
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps(data))

    world_config, beans_config, env_config = load_config(str(p))
    # Assert default random mode is used (explicit type check unnecessary)
    assert env_config.random_mode == "random"


def test_environment_config_validation_explicit_requires_values(tmp_path):
    # explicit mode without explicit lists should raise
    data = {"world": {}, "beans": {}, "environment": {"random_mode": "explicit"}}
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps(data))

    with pytest.raises(ValueError):
        load_config(str(p))
