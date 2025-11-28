import arcade
import arcade.key
import logging
from typing import List, Sequence

from beans.world import World
from .bean_sprite import BeanSprite
from reporting.report import ConsoleSimulationReport, SimulationReport

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
    def __init__(self, world: World, title: str = "Beans World", reporters: Sequence[SimulationReport] | None = None) -> None:
        self.world = world
        self.base_title = title
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
        logger.info(
            f"WorldWindow::__init__: Generated positions for beans with width={self.world.width}, height={self.world.height}, sprite_size={self.world.sprite_size}"
        )
        for pos in positions:
            logger.debug(f"WorldWindow::__init__: Position: {pos}")
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
        self._prompt_active = False
        self._paused = False
        self._reporters: List[SimulationReport] = list(reporters) if reporters is not None else [ConsoleSimulationReport()]

    def _pause_for_empty_world(self) -> bool:
        """Set pause/prompt state when no beans remain."""
        if self.world.beans:
            return False
        if not self._prompt_active:
            self._prompt_active = True
            self._paused = True
        return True

    def on_draw(self):
        self.clear()
        self.sprite_list.draw()
        if self._prompt_active:
            self._draw_zero_bean_prompt()

    def on_update(self, delta_time: float):
        logger.debug(f">>>>> WorldWindow.on_update: delta_time={delta_time}")
        if self._pause_for_empty_world():
            return
        if self._paused:
            return
        self.world.step(delta_time)
        self.title = f"{self.base_title} - round: {self.world.round}"
        old_count = len(self.bean_sprites)
        self.bean_sprites = [sprite for sprite in self.bean_sprites if sprite.bean in self.world.beans]
        if len(self.bean_sprites) < old_count:
            logger.debug(f"WorldWindow.on_update: {old_count - len(self.bean_sprites)} sprites removed")
        self.sprite_list = arcade.SpriteList()
        for sprite in self.bean_sprites:
            self.sprite_list.append(sprite)
        logger.debug(f">>>>> WorldWindow.on_update: {len(self.bean_sprites)} sprites active")
        self._pause_for_empty_world()

    def on_key_press(self, symbol: int, modifiers: int):
        if self._prompt_active:
            if symbol == arcade.key.Y:
                self._invoke_reports()
                arcade.close_window()
            elif symbol == arcade.key.N:
                arcade.close_window()
            return
        if symbol == arcade.key.ESCAPE:
            logger.info(">>>>> ESC key pressed, closing window")
            arcade.close_window()

    def _draw_zero_bean_prompt(self) -> None:
        overlay_width = self.width * 0.7
        overlay_height = self.height * 0.3
        center_x = self.width / 2
        center_y = self.height / 2
        left = center_x - overlay_width / 2
        right = center_x + overlay_width / 2
        bottom = center_y - overlay_height / 2
        top = center_y + overlay_height / 2
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, arcade.color.DARK_SLATE_GRAY)
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, arcade.color.WHITE, border_width=2)
        prompt = "No live beans remain. Press Y for report or N to exit."
        arcade.draw_text(
            prompt,
            center_x - overlay_width / 2 + 20,
            center_y + overlay_height / 4,
            arcade.color.WHITE,
            font_size=16,
            width=overlay_width - 40,
            align="left",
        )
        subtext = "The simulation is paused while awaiting your response."
        arcade.draw_text(
            subtext,
            center_x - overlay_width / 2 + 20,
            center_y - overlay_height / 8,
            arcade.color.LIGHT_GRAY,
            font_size=14,
            width=overlay_width - 40,
            align="left",
        )

    def _invoke_reports(self) -> None:
        for reporter in self._reporters:
            reporter.generate(self.world_config, self.world.beans_config, self.world, self)
