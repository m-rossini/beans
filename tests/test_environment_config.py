import json

import pytest

from config.loader import load_config


def test_load_config_returns_environment_config(tmp_path):
    data = {"world": {}, "beans": {}, "environment": {}}
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps(data))

    world_config, beans_config, env_config = load_config(str(p))
    # Assert basic environment defaults are present
    assert env_config.cell_size == 20


def test_environment_config_validation_cell_size_must_be_positive(tmp_path):
    data = {"world": {}, "beans": {}, "environment": {"cell_size": 0}}
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps(data))

    with pytest.raises(ValueError):
        load_config(str(p))
