import json
import tempfile
import pytest

from config.loader import load_config


def test_load_config_returns_environment_config():
    data = {"world": {}, "beans": {}, "environment": {}}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        p = f.name

    try:
        world_config, beans_config, env_config = load_config(p)
        assert hasattr(env_config, "random_mode")
        assert env_config.random_mode in ("random", "seeded", "explicit")
    finally:
        import os

        os.unlink(p)


def test_environment_config_validation_explicit_requires_values(tmp_path):
    # explicit mode without explicit lists should raise
    data = {"world": {}, "beans": {}, "environment": {"random_mode": "explicit"}}
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps(data))

    with pytest.raises(ValueError):
        load_config(str(p))
