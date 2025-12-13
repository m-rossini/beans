import logging
import arcade
from beans.placement import RandomPlacementStrategy
from beans.world import World
from config.loader import BeansConfig, WorldConfig
from reporting.report import SimulationReport
from beans.dynamics.bean_dynamics import BeanDynamics

logger = logging.getLogger(__name__)

def test_sprite_position_updates_on_movement(monkeypatch):
    """
    TDD: Ensure WorldWindow.on_update updates sprite positions after movement.
    """
    cfg = WorldConfig(male_sprite_color="blue", female_sprite_color="red", male_female_ratio=1.0, width=200, height=150, population_density=0.1, placement_strategy="random")
    bcfg = BeansConfig(speed_min=10, speed_max=10, max_age_rounds=100, initial_bean_size=10, male_bean_color="blue", female_bean_color="red")
    world = World(cfg, bcfg)
    monkeypatch.setattr(arcade.Window, "__init__", _fake_arcade_init, raising=False)
    from rendering.window import WorldWindow
    win = WorldWindow(world)
    sprite = win.bean_sprites[0]
    # Patch bean_dynamics to use the test bean's genotype and max_age
    world.bean_dynamics = BeanDynamics(bcfg, sprite.bean.genotype, sprite.bean._max_age)
    # Set initial position and direction
    initial_x = sprite.center_x
    initial_y = sprite.center_y
    sprite.direction = 0.0  # Move right
    sprite.bean._phenotype.speed = 10.0
    win.on_update(0.1)
    # Assert position has changed after movement
    assert sprite.center_x != initial_x or sprite.center_y != initial_y
    
def test_sprite_creation_initialization(monkeypatch):
    """
    TDD: Ensure WorldWindow creates sprites for all beans with correct attributes.
    """
    cfg = WorldConfig(male_sprite_color="blue", female_sprite_color="red", male_female_ratio=0.5, width=100, height=100, population_density=0.2, placement_strategy="random")
    bcfg = BeansConfig(speed_min=1, speed_max=2, max_age_rounds=10, initial_bean_size=5, male_bean_color="blue", female_bean_color="red")
    world = World(cfg, bcfg)
    monkeypatch.setattr(arcade.Window, "__init__", _fake_arcade_init, raising=False)
    from rendering.window import WorldWindow
    win = WorldWindow(world)
    # Assert sprite count matches bean count
    assert len(win.bean_sprites) == len(world.beans)
    # Assert each sprite is initialized with correct bean reference and position
    for sprite, bean in zip(win.bean_sprites, world.beans):
        assert sprite.bean is bean
        assert isinstance(sprite.center_x, (int, float))
        assert isinstance(sprite.center_y, (int, float))
        # Allow for small floating-point differences in bean size
        assert abs(sprite.bean.size - bcfg.initial_bean_size) < 0.5
        assert sprite.color in [arcade.color.BLUE, arcade.color.RED]


def _fake_arcade_init(self, width, height, title):
    # Bypass Pyglet internals and set minimal attributes used by our tests
    self._width = width
    self._height = height
    # do not set 'scale' property, avoid property set errors
    self._event_queue = []
    self._enable_event_queue = False
    self._allow_dispatch_event = True
    self.set_size = lambda w, h: (setattr(self, "_width", w), setattr(self, "_height", h))
    self.get_size = lambda: (self._width, self._height)

def test_world_window_esc_closes(monkeypatch):
    cfg = WorldConfig(male_sprite_color="blue", female_sprite_color="red", male_female_ratio=1.0, width=200, height=150, population_density=0.1, placement_strategy="random")
    bcfg = BeansConfig(speed_min=-5, speed_max=5, max_age_rounds=100, initial_bean_size=10, male_bean_color="blue", female_bean_color="red")
    world = World(cfg, bcfg)

    closed = {"called": False}
    monkeypatch.setattr(arcade.Window, "__init__", _fake_arcade_init, raising=False)
    monkeypatch.setattr(arcade, "close_window", lambda: closed.update({"called": True}), raising=False)
    from rendering.window import WorldWindow
    win = WorldWindow(world)
    win.on_key_press(arcade.key.ESCAPE, 0)
    assert closed["called"] is True


def test_world_window_calls_placement(monkeypatch):
    cfg = WorldConfig(male_sprite_color="blue", female_sprite_color="red", male_female_ratio=1.0, width=200, height=150, population_density=0.1, placement_strategy="random")
    bcfg = BeansConfig(speed_min=-5, speed_max=5, max_age_rounds=100, initial_bean_size=10, male_bean_color="blue", female_bean_color="red")
    world = World(cfg, bcfg)

    called = {"count": 0}
    class SpyPlacement(RandomPlacementStrategy):
        def place(self, count, width, height, size):
            called["count"] += 1
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
    monkeypatch.setattr(arcade.Window, "__init__", _fake_arcade_init, raising=False)
    from rendering.window import WorldWindow
    win = WorldWindow(world)
    assert called["count"] == 1
    assert len(win.bean_sprites) == len(world.beans)


def test_world_window_sprite_colors(monkeypatch):
    cfg = WorldConfig(male_sprite_color="blue", female_sprite_color="red", male_female_ratio=1.0, width=200, height=150, population_density=0.1, placement_strategy="random")
    bcfg = BeansConfig(speed_min=-5, speed_max=5, max_age_rounds=100, initial_bean_size=10, male_bean_color="green", female_bean_color="yellow")
    world = World(cfg, bcfg)

    monkeypatch.setattr(arcade.Window, "__init__", _fake_arcade_init, raising=False)
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
    cfg = WorldConfig(male_sprite_color="blue", female_sprite_color="red", male_female_ratio=1.0, width=200, height=150, population_density=0.0, placement_strategy="random")
    bcfg = BeansConfig(speed_min=-5, speed_max=5, max_age_rounds=100, initial_bean_size=10, male_bean_color="blue", female_bean_color="red")
    world = World(cfg, bcfg)

    class SpyReporter(SimulationReport):
        def __init__(self) -> None:
            self.called = 0
        def generate(self, world_config, beans_config, world_arg, window_arg):
            self.called += 1

    reporter = SpyReporter()

    monkeypatch.setattr(arcade.Window, "__init__", _fake_arcade_init, raising=False)
    closed = {"called": False}
    monkeypatch.setattr(arcade, "close_window", lambda: closed.update({"called": True}), raising=False)
    from rendering.window import WorldWindow
    win = WorldWindow(world, reporters=[reporter])
    win.on_update(0)
    assert win._prompt_active
    win.on_key_press(arcade.key.Y, 0)
    assert reporter.called == 1


def test_world_window_pauses_when_empty(monkeypatch):
    cfg = WorldConfig(male_sprite_color="blue", female_sprite_color="red", male_female_ratio=1.0, width=200, height=150, population_density=0.0, placement_strategy="random")
    bcfg = BeansConfig(speed_min=-5, speed_max=5, max_age_rounds=100, initial_bean_size=10, male_bean_color="blue", female_bean_color="red")
    world = World(cfg, bcfg)
    world.beans = []

    step_calls = {"count": 0}
    def spy_step(dt: float):
        step_calls["count"] += 1
    world.step = spy_step

    monkeypatch.setattr(arcade.Window, "__init__", _fake_arcade_init, raising=False)
    from rendering.window import WorldWindow
    win = WorldWindow(world)
    win.on_update(0)

    assert step_calls["count"] == 0
    assert win._prompt_active
    assert win._paused


def test_window_bounce_deducts_energy(monkeypatch):
    cfg = WorldConfig(male_sprite_color="blue", female_sprite_color="red", male_female_ratio=1.0, width=200, height=150, population_density=0.1, placement_strategy="random")
    bcfg = BeansConfig(speed_min=1.0, speed_max=200.0, max_age_rounds=100, initial_bean_size=10, male_bean_color="blue", female_bean_color="red")
    world = World(cfg, bcfg)

    monkeypatch.setattr(arcade.Window, "__init__", _fake_arcade_init, raising=False)
    from rendering.window import WorldWindow
    win = WorldWindow(world)
    sprite = win.bean_sprites[0]
    # Patch bean_dynamics to use the test bean's genotype and max_age
    world.bean_dynamics = BeanDynamics(bcfg, sprite.bean.genotype, sprite.bean._max_age)
    # set sprite near the right edge with direction toward the edge
    sprite.center_x = win.width - (sprite.bean.size / 2.0) - 1
    sprite.center_y = win.height / 2
    sprite.direction = 0.0
    sprite.bean._phenotype.speed = 50.0
    initial_energy = sprite.bean.energy
    # call on_update which will cause movement and bounce in the rendering layer
    win.on_update(0.1)
    # energy should be reduced by at least one bounce deduction
    assert sprite.bean.energy < initial_energy
