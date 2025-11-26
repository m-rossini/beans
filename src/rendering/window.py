import arcade
import logging
from typing import List, Tuple, Optional
from beans.world import World
from beans.placement import PlacementStrategy, RandomPlacementStrategy
from .bean_sprite import BeanSprite

logger = logging.getLogger(__name__)


def _color_from_name(name: str):
    try:
        color = getattr(arcade.color, name.upper())
        logger.debug(f">>>>> _color_from_name: name={name} -> {color}")
        return color
    except Exception as e:
        logger.debug(f">>>>> _color_from_name: name={name} not found, defaulting to WHITE")
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
        logger.info(f"WorldWindow initialized with {len(self.bean_sprites)} bean sprites. title={title}, beans_count={len(world.beans)}")

    def on_draw(self):
        self.clear()
        self.sprite_list.draw()

    def on_update(self, delta_time: float):
        logger.debug(f">>>>> WorldWindow.on_update: delta_time={delta_time}")
        self.world.step(delta_time)
        self.title = f"Beans World - round: {self.world.round}"
        old_count = len(self.bean_sprites)
        self.bean_sprites = [sprite for sprite in self.bean_sprites if sprite.bean in self.world.beans]
        if len(self.bean_sprites) < old_count:
            logger.debug(f"WorldWindow.on_update: {old_count - len(self.bean_sprites)} sprites removed")
        self.sprite_list = arcade.SpriteList()
        for sprite in self.bean_sprites:
            self.sprite_list.append(sprite)
        logger.debug(f">>>>> WorldWindow.on_update: {len(self.bean_sprites)} sprites active")

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            logger.info(">>>>> ESC key pressed, closing window")
            arcade.close_window()
