import logging
from typing import List, Sequence

import arcade
import arcade.key

from beans.world import World
from reporting.report import ConsoleSimulationReport, SimulationReport

from .bean_sprite import BeanSprite
from .movement import SpriteMovementSystem

logger = logging.getLogger(__name__)


def _color_from_name(name: str):
    try:
        color = getattr(arcade.color, name.upper())
        logger.debug(f">>>>> _color_from_name: name={name} -> {color}")
        return color
    except Exception:
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
        logger.info(f">>>> WorldWindow::__init__: Generated positions for beans with width={self.world.width}, height={self.world.height}, sprite_size={self.world.sprite_size}")
        for pos in positions:
            logger.debug(f">>>>> WorldWindow::__init__: Position: {pos}")

        self.bean_sprites: List[BeanSprite] = self._create_bean_sprites(positions)
        self.sprite_list = arcade.SpriteList()
        self.sprite_list.extend(self.bean_sprites)
        # Movement system for sprite animation and bouncing
        self._movement_system = SpriteMovementSystem()
        logger.info(f">>>> WorldWindow initialized with {len(self.bean_sprites)} bean sprites. title={title}, beans_count={len(world.beans)}")
        self._prompt_active = False
        self._paused = False
        self._reporters: List[SimulationReport] = list(reporters) if reporters is not None else [ConsoleSimulationReport()]
        self._help_active = False

    def _create_bean_sprites(self, positions) -> BeanSprite:
        return [ self._create_sprite(bean, positions[i]) for i, bean in enumerate(self.world.beans)]

    def _create_sprite(self, bean, position) -> BeanSprite:
        color_str = self.world.beans_config.male_bean_color if bean.is_male else self.world.beans_config.female_bean_color
        color = _color_from_name(color_str)
        return BeanSprite(bean, position, color)

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
        if self._help_active:
            self._draw_help_overlay()

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
            logger.debug(f">>>>> WorldWindow.on_update: {old_count - len(self.bean_sprites)} sprites removed")
        self.sprite_list = arcade.SpriteList()
        for sprite in self.bean_sprites:
            # Compute target position using movement system (fail fast if missing)
            tx, ty, _ = self._movement_system.move_sprite(sprite, self.width, self.height)
            target_position = (tx, ty)
            sprite.update_from_bean(delta_time, target_position=target_position)
            self.sprite_list.append(sprite)
        logger.debug(f">>>>> WorldWindow.on_update: {len(self.bean_sprites)} sprites active")
        self._pause_for_empty_world()

    def on_key_press(self, symbol: int, modifiers: int):
        if self._prompt_active:
            if symbol == arcade.key.Y:
                self._invoke_reports()
                arcade.close_window()
            elif symbol == arcade.key.N or symbol == arcade.key.ESCAPE:
                arcade.close_window()
            return
        if symbol == arcade.key.F1:
            self._help_active = not self._help_active
            return
        if symbol == arcade.key.ESCAPE:
            if self._help_active:
                self._help_active = False
                return
            logger.info(">>>> ESC key pressed, closing window")
            arcade.close_window()

    def _draw_zero_bean_prompt(self) -> None:
        overlay_width = self.width * 0.8
        overlay_height = self.height * 0.8
        if overlay_width <= 0 or overlay_height <= 0:
            return
        center_x = self.width / 2
        center_y = self.height / 2
        half_width = overlay_width / 2
        half_height = overlay_height / 2
        left = center_x - half_width
        right = center_x + half_width
        bottom = center_y - half_height
        top = center_y + half_height
        overlay_color = self._overlay_color_for_background()
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, overlay_color)
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, arcade.color.WHITE, border_width=2)
        prompt_text = "No Alive Beans left."
        action_text = "Do you want a report? Y or N?"
        margin = max(24, overlay_width * 0.05)
        text_width = overlay_width - margin * 2
        prompt_font = max(18, min(int(self.height * 0.06), 32))
        action_font = max(14, prompt_font - 4)
        prompt_y = center_y + overlay_height * 0.15
        text_color = self.background_color
        text_x = left + margin
        arcade.draw_text(
            prompt_text,
            text_x,
            prompt_y,
            text_color,
            font_size=prompt_font,
            width=text_width,
            align="left",
            anchor_x="left",
            anchor_y="center",
        )
        action_y = center_y
        arcade.draw_text(
            action_text,
            text_x,
            action_y,
            text_color,
            font_size=action_font,
            width=text_width,
            align="left",
            anchor_x="left",
            anchor_y="center",
        )

    def _invoke_reports(self) -> None:
        for reporter in self._reporters:
            reporter.generate(self.world_config, self.world.beans_config, self.world, self)

    def _draw_help_overlay(self) -> None:
        overlay_width = self.width * 0.8
        overlay_height = self.height * 0.8
        if overlay_width <= 0 or overlay_height <= 0:
            return
        center_x = self.width / 2
        center_y = self.height / 2
        half_width = overlay_width / 2
        half_height = overlay_height / 2
        left = center_x - half_width
        right = center_x + half_width
        bottom = center_y - half_height
        top = center_y + half_height
        overlay_color = self._overlay_color_for_background()
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, overlay_color)
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, arcade.color.WHITE, border_width=2)
        title_text = "Help"
        help_lines = [
            "F1 - Toggle this help",
            "ESC - Close window",
        ]
        margin = max(24, overlay_width * 0.05)
        text_width = overlay_width - margin * 2
        title_font = max(20, min(int(self.height * 0.07), 32))
        line_font = max(14, min(int(self.height * 0.05), 22))
        text_color = self.background_color
        text_x = left + margin
        title_y = top - margin - title_font
        arcade.draw_text(
            title_text,
            text_x,
            title_y,
            text_color,
            font_size=title_font,
            width=text_width,
            align="left",
            anchor_x="left",
            anchor_y="top",
        )
        line_y = title_y - title_font - 10
        for line in help_lines:
            arcade.draw_text(
                line,
                text_x,
                line_y,
                text_color,
                font_size=line_font,
                width=text_width,
                align="left",
                anchor_x="left",
                anchor_y="top",
            )
            line_y -= line_font + 6

    def _overlay_color_for_background(self) -> tuple[int, int, int, int]:
        color = self.background_color
        if len(color) == 4:
            base = color[:3]
        else:
            base = color
        r, g, b = base
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        if luminance > 180:
            return (20, 20, 20, 200)
        return (240, 240, 240, 200)
