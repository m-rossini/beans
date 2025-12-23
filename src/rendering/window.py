import logging
from typing import List, Sequence

import arcade
import arcade.key
from beans.environment.food_manager import FoodType

from beans.world import World, WorldState
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

    def __init__(
        self,
        world: World,
        title: str = "Beans World",
        reporters: Sequence[SimulationReport] | None = None,
    ) -> None:
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
            len(self.world.beans),
            self.world.width,
            self.world.height,
            self.world.sprite_size,
        )
        logger.info(
            ">>>> WorldWindow::__init__: Generated positions for beans with width=%d, height=%d, sprite_size=%d",
            self.world.width,
            self.world.height,
            self.world.sprite_size,
        )
        for pos in positions:
            logger.debug(f">>>>> WorldWindow::__init__: Position: {pos}")

        self.bean_sprites = self._create_bean_sprites(positions)  # type: List[BeanSprite]
        self.sprite_list = arcade.SpriteList()
        self.sprite_list.extend(self.bean_sprites)
        # Movement system for sprite animation and bouncing
        self._movement_system = SpriteMovementSystem()
        logger.info(
            ">>>> WorldWindow initialized with %d bean sprites. title=%s, beans_count=%d",
            len(self.bean_sprites),
            title,
            len(world.beans),
        )
        self._prompt_active = False
        self._paused = False
        self._reporters: List[SimulationReport] = list(reporters) if reporters is not None else [ConsoleSimulationReport()]
        self._help_active = False

    def _all_food_positions(self):
        fm = self.world.food_manager
        # Only works for HybridFoodManager for now, as per test
        for pos, entry in getattr(fm, 'grid', {}).items():
            if entry['value'] > 0:
                food_type = entry.get('type', None)
                if hasattr(food_type, 'name'):
                    type_name = food_type.name
                else:
                    type_name = str(food_type)
                yield (pos[0], type_name, entry['value'])

    def _create_bean_sprites(self, positions) -> BeanSprite:
        return [self._create_sprite(bean, positions[i]) for i, bean in enumerate(self.world.beans)]

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
        self._draw_food_items()
        if self._prompt_active:
            self._draw_zero_bean_prompt()
        if self._help_active:
            self._draw_help_overlay()

    def _draw_food_items(self):
        """Draw food and dead bean food items on the screen."""
        food_manager = self.world.environment.food_manager
        for (x, y), entry in food_manager.grid.items():
            if entry.get('value', 0) > 0:
                color = arcade.color.GREEN
                if entry.get('type', None) == FoodType.DEAD_BEAN:
                    color = arcade.color.BROWN
                size = entry.get('size', 3)
                arcade.draw_circle_filled(x, y, size, color)

    def on_update(self, delta_time: float):
        logger.debug(">>>>> WorldWindow.on_update: delta_time=%0.3f", delta_time)
        if self._pause_for_empty_world() or self._paused:
            return
        world_state = self._advance_world(delta_time)
        self._update_window_title(world_state)
        self._add_dead_bean_food(world_state)
        self._refresh_bean_sprites()
        self._move_and_update_sprites(delta_time)
        logger.debug(">>>>> WorldWindow.on_update: %d sprites active", len(self.bean_sprites))
        self._handle_empty_world()

    def _advance_world(self, delta_time: float) -> WorldState:
        world_state = self.world.step(delta_time)
        return world_state

    def _update_window_title(self, world_state: WorldState) -> None:
        self.title = (
            f"{self.base_title} - round: {world_state.current_round} "
            f"- alive beans: {len(world_state.alive_beans)} "
            f"- dead beans: {len(world_state.dead_beans)}"
        )

    def _refresh_bean_sprites(self) -> None:
        old_count = len(self.bean_sprites)
        self.bean_sprites = [sprite for sprite in self.bean_sprites if sprite.bean in self.world.beans]
        if len(self.bean_sprites) < old_count:
            logger.debug(">>>>> WorldWindow.on_update: %d sprites removed", (old_count - len(self.bean_sprites)))

    def _move_and_update_sprites(self, delta_time: float) -> None:
        targets = [
            (sprite, *self._movement_system.move_sprite(sprite, self.width, self.height)[:2])
            for sprite in self.bean_sprites
        ]
        adjusted_targets, _ = self._movement_system.resolve_collisions(targets, self.width, self.height)
        self.sprite_list = arcade.SpriteList()
        for sprite in self.bean_sprites:
            sprite.update_from_bean(delta_time, adjusted_targets[sprite])
            self.sprite_list.append(sprite)

    def _handle_empty_world(self) -> None:
        if self._pause_for_empty_world():
            logger.info(">>>> WorldWindow.on_update: No alive beans left, pausing simulation. Here are the death reasons:")
            for survival_result in self.world.dead_beans:
                bean = survival_result.bean
                logger.info(f">>>> Bean id={bean.id} died due to: {survival_result.reason}")

    def _add_dead_bean_food(self, world_state: WorldState) -> None:
        """Add dead bean food at sprite position for each dead bean."""
        for dead_bean in world_state.dead_beans:
            sprite = next((s for s in self.bean_sprites if s.bean.id == dead_bean.id), None)
            if sprite is not None:
                pos = (int(sprite.center_x), int(sprite.center_y))
                size = int(dead_bean.size *  self.world.env_config.dead_bean_initial_food_size_factor)
                self.world.food_manager.add_dead_bean_as_food(pos, size)

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
