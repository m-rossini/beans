import arcade
from typing import List, Tuple, Optional
from beans.world import World
from beans.placement import PlacementStrategy, RandomPlacementStrategy


def _color_from_name(name: str):
    try:
        return getattr(arcade.color, name.upper())
    except Exception:
        return arcade.color.WHITE


class WorldWindow(arcade.Window):
    def __init__(self, world: World, title: str = "Beans World") -> None:
        self.world = world
        self.world_config = world.world_config
        width = self.world_config.width
        height = self.world_config.height
        super().__init__(width, height, title)
        try:
            arcade.set_background_color(arcade.color.BLACK)
        except RuntimeError:
            pass
        self.placement_strategy = world.placement_strategy
        # compute positions for rendering only
        self.positions: List[Tuple[float, float]] = self.placement_strategy.place(
            len(self.world.beans), self.world.width, self.world.height, self.world.sprite_size
        )
        self.male_color = _color_from_name(self.world_config.male_sprite_color)
        self.female_color = _color_from_name(self.world_config.female_sprite_color)

    def on_draw(self):
        arcade.start_render()
        for i, bean in enumerate(self.world.beans):
            x, y = self.positions[i]
            radius = max(1, self.world.sprite_size / 2)
            color = self.male_color if bean.is_male else self.female_color
            arcade.draw_circle_filled(x, y, radius, color)

    def on_update(self, delta_time: float):
        self.world.step(delta_time)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()
