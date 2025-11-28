import arcade
import types
import pytest
import logging

from beans.placement import RandomPlacementStrategy
from beans.world import World
from config.loader import WorldConfig, BeansConfig
from reporting.report import SimulationReport

logger = logging.getLogger(__name__)


def _fake_arcade_init(self, width, height, title):
    # Bypass Pyglet internals and set minimal attributes used by our tests
    self._width = width
    self._height = height
    # do not set 'scale' property, avoid property set errors
    self._event_queue = []
    self._enable_event_queue = False
    self._allow_dispatch_event = True
    self.set_size = lambda w, h: (setattr(self, '_width', w), setattr(self, '_height', h))
    self.get_size = lambda: (self._width, self._height)

def test_world_window_esc_closes(monkeypatch):
    cfg = WorldConfig(male_sprite_color='blue', female_sprite_color='red', male_female_ratio=1.0, width=200, height=150, population_density=0.1, placement_strategy='random')
    bcfg = BeansConfig(max_bean_age=100, speed_min=-5, speed_max=5, initial_bean_size=10, male_bean_color='blue', female_bean_color='red')
    world = World(cfg, bcfg)

    closed = {'called': False}
    monkeypatch.setattr(arcade.Window, '__init__', _fake_arcade_init, raising=False)
    monkeypatch.setattr(arcade, 'close_window', lambda: closed.update({'called': True}), raising=False)
    from rendering.window import WorldWindow
    win = WorldWindow(world)
    win.on_key_press(arcade.key.ESCAPE, 0)
    assert closed['called'] is True


def test_world_window_calls_placement(monkeypatch):
    cfg = WorldConfig(male_sprite_color='blue', female_sprite_color='red', male_female_ratio=1.0, width=200, height=150, population_density=0.1, placement_strategy='random')
    bcfg = BeansConfig(max_bean_age=100, speed_min=-5, speed_max=5, initial_bean_size=10, male_bean_color='blue', female_bean_color='red')
    world = World(cfg, bcfg)

    called = {'count': 0}
    class SpyPlacement(RandomPlacementStrategy):
        def place(self, count, width, height, size):
            called['count'] += 1
            # Return non-overlapping positions within bounds
            positions = []
            cols = max(1, width // (size * 2))
            for i in range(count):
                col = i % cols
                row = i // cols
                x = col * size * 2 + size
                y = row * size * 2 + size
                if x < width and y < height:
                    positions.append((x, y))
            return positions

    world.placement_strategy = SpyPlacement()
    monkeypatch.setattr(arcade.Window, '__init__', _fake_arcade_init, raising=False)
    from rendering.window import WorldWindow
    win = WorldWindow(world)
    assert called['count'] == 1
    assert len(win.bean_sprites) == len(world.beans)


def test_world_window_sprite_colors(monkeypatch):
    cfg = WorldConfig(male_sprite_color='blue', female_sprite_color='red', male_female_ratio=1.0, width=200, height=150, population_density=0.1, placement_strategy='random')
    bcfg = BeansConfig(max_bean_age=100, speed_min=-5, speed_max=5, initial_bean_size=10, male_bean_color='green', female_bean_color='yellow')
    world = World(cfg, bcfg)

    monkeypatch.setattr(arcade.Window, '__init__', _fake_arcade_init, raising=False)
    from rendering.window import WorldWindow
    win = WorldWindow(world)
    for sprite in win.bean_sprites:
        if sprite.bean.is_male:
            expected_color = getattr(arcade.color, bcfg.male_bean_color.upper())
            assert sprite.color == expected_color
        else:
            expected_color = getattr(arcade.color, bcfg.female_bean_color.upper())
            assert sprite.color == expected_color
    assert len(win.bean_sprites) == len(world.beans)


def test_world_window_reports_when_empty(monkeypatch):
    cfg = WorldConfig(male_sprite_color='blue', female_sprite_color='red', male_female_ratio=1.0, width=200, height=150, population_density=0.0, placement_strategy='random')
    bcfg = BeansConfig(max_bean_age=100, speed_min=-5, speed_max=5, initial_bean_size=10, male_bean_color='blue', female_bean_color='red')
    world = World(cfg, bcfg)

    class SpyReporter(SimulationReport):
        def __init__(self) -> None:
            self.called = 0
        def generate(self, world_config, beans_config, world_arg, window_arg):
            self.called += 1

    reporter = SpyReporter()

    monkeypatch.setattr(arcade.Window, '__init__', _fake_arcade_init, raising=False)
    closed = {'called': False}
    monkeypatch.setattr(arcade, 'close_window', lambda: closed.update({'called': True}), raising=False)
    from rendering.window import WorldWindow
    win = WorldWindow(world, reporters=[reporter])
    win.on_update(0)
    assert win._prompt_active
    win.on_key_press(arcade.key.Y, 0)
    assert reporter.called == 1


def test_world_window_pauses_when_empty(monkeypatch):
    cfg = WorldConfig(male_sprite_color='blue', female_sprite_color='red', male_female_ratio=1.0, width=200, height=150, population_density=0.0, placement_strategy='random')
    bcfg = BeansConfig(max_bean_age=100, speed_min=-5, speed_max=5, initial_bean_size=10, male_bean_color='blue', female_bean_color='red')
    world = World(cfg, bcfg)
    world.beans = []

    step_calls = {'count': 0}
    def spy_step(dt: float):
        step_calls['count'] += 1
    world.step = spy_step

    monkeypatch.setattr(arcade.Window, '__init__', _fake_arcade_init, raising=False)
    from rendering.window import WorldWindow
    win = WorldWindow(world)
    win.on_update(0)

    assert step_calls['count'] == 0
    assert win._prompt_active
    assert win._paused
