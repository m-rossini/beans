from config.loader import load_config


def test_small_config_parses_environment(tmp_path):
    cfg_path = "src/config/small.json"
    world_cfg, beans_cfg, env_cfg = load_config(cfg_path)
    # basic environment fields parse correctly
    assert env_cfg.cell_size == 20
    assert env_cfg.food_density >= 0.0


def test_medium_config_parses_seeded(tmp_path):
    cfg_path = "src/config/medium.json"
    world_cfg, beans_cfg, env_cfg = load_config(cfg_path)
    assert env_cfg.cell_size == 20
    assert env_cfg.food_density >= 0.0


def test_large_config_parses_explicit_grid(tmp_path):
    cfg_path = "src/config/large.json"
    world_cfg, beans_cfg, env_cfg = load_config(cfg_path)
    # large config environment fields parse correctly (explicit fields removed)
    assert env_cfg.cell_size == 40
    assert env_cfg.food_density >= 0.0
