import pytest
from config.loader import DEFAULT_BEANS_CONFIG, load_config, BeansConfig


def test_default_beans_config_has_movement_fields():
    cfg = DEFAULT_BEANS_CONFIG
    assert hasattr(cfg, 'pixels_per_unit_speed')
    assert hasattr(cfg, 'energy_loss_on_bounce')
    assert cfg.pixels_per_unit_speed == 1.0
    assert cfg.energy_loss_on_bounce == 2.0


def test_load_config_validates_pixels_and_bounce(tmp_path):
    # Create a minimal config
    cfg_data = {
        'world': {},
        'beans': {
            'speed_min': 10.0,
            'speed_max': 20.0,
            'pixels_per_unit_speed': 0.5,
            'energy_loss_on_bounce': 1.5,
        }
    }
    p = tmp_path / "cfg.json"
    p.write_text(str(cfg_data).replace("'", '"'))
    world_cfg, beans_cfg = load_config(str(p))
    assert beans_cfg.pixels_per_unit_speed == 0.5
    assert beans_cfg.energy_loss_on_bounce == 1.5


def test_load_config_rejects_negative_energy_loss(tmp_path):
    cfg_data = {'world': {}, 'beans': {'speed_min': 1.0, 'speed_max': 2.0, 'energy_loss_on_bounce': -5.0}}
    p = tmp_path / "cfg.json"
    p.write_text(str(cfg_data).replace("'", '"'))
    with pytest.raises(ValueError):
        load_config(str(p))


def test_load_config_rejects_zero_pixels_per_unit(tmp_path):
    cfg_data = {'world': {}, 'beans': {'speed_min': 1.0, 'speed_max': 2.0, 'pixels_per_unit_speed': 0.0}}
    p = tmp_path / "cfg.json"
    p.write_text(str(cfg_data).replace("'", '"'))
    with pytest.raises(ValueError):
        load_config(str(p))
