import arcade
from typing import List, Tuple, Optional
from beans.world import World
from beans.placement import PlacementStrategy, RandomPlacementStrategy
from .bean_sprite import BeanSprite


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
        bg_color = _color_from_name(self.world_config.background_color)
        self.background_color = bg_color
        self.placement_strategy = world.placement_strategy
        # Create sprites for each bean
        positions = self.placement_strategy.place(
            len(self.world.beans), self.world.width, self.world.height, self.world.sprite_size
        )
        self.bean_sprites: List[BeanSprite] = []
        self.sprite_list = arcade.SpriteList()
        for i, bean in enumerate(self.world.beans):
            pos = positions[i]
            color_str = self.world.beans_config.male_bean_color if bean.is_male else self.world.beans_config.female_bean_color
            color = _color_from_name(color_str)
            sprite = BeanSprite(bean, pos, color)
            self.bean_sprites.append(sprite)
            self.sprite_list.append(sprite)

    def on_draw(self):
        self.clear()
        self.sprite_list.draw()

    def on_update(self, delta_time: float):
        self.world.step(delta_time)
        # Sync sprites with alive beans
        self.bean_sprites = [sprite for sprite in self.bean_sprites if sprite.bean in self.world.beans]
        self.sprite_list = arcade.SpriteList()
        for sprite in self.bean_sprites:
            self.sprite_list.append(sprite)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()
