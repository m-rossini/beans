import logging
import random
from typing import Optional


import arcade
from beans.bean import Bean

logger = logging.getLogger(__name__)


class BeanSprite(arcade.Sprite):
    """Sprite representation of a Bean for rendering in the window."""

    def __init__(self, bean: Bean, position: tuple[float, float], color: tuple[int, int, int], direction: Optional[float] = None):
        direction = random.uniform(0, 360) if direction is None else direction
        self.direction = direction % 360.0
        logger.debug(f">>>>> BeanSprite.__init__: bean_id={bean.id}, position={position}, color={color}, direction={self.direction:.2f}")
        self.diameter = bean.beans_config.initial_bean_size
        texture = arcade.make_circle_texture(self.diameter, color)
        super().__init__(texture, center_x=position[0], center_y=position[1])
        self.bean = bean
        self.color = color

    def update_from_bean(self,
                         delta_time: float = 1.0,
                         target_position: Optional[tuple[float, float]] = None):
        """Update sprite based on bean state (size changes and optional movement).
        delta_time is used for visual interpolation only. If target_position is provided,
        the sprite interpolates towards it for smoother animation.
        """
        # Save previous visual center for interpolation
        prev_x = self.center_x
        prev_y = self.center_y

        # Update visual scale from bean size
        scale_factor = self.bean.size / self.diameter
        self.scale = scale_factor


        target_x = self.center_x
        target_y = self.center_y
        if target_position is not None:
            target_x, target_y = target_position

        # Interpolate for visual smoothing; dt controls fraction (constant multiplier)
        lerp = min(1.0, delta_time * 6.0)
        self.center_x = prev_x + (target_x - prev_x) * lerp
        self.center_y = prev_y + (target_y - prev_y) * lerp

        # Orient sprite visually to the direction
        self.angle = self.direction
        logger.debug(f">>>>> BeanSprite.update_from_bean: bean_id={self.bean.id}, prev=({prev_x:.2f},{prev_y:.2f}), target=({target_x:.2f},{target_y:.2f}), lerp={lerp:.2f}, new=({self.center_x:.2f},{self.center_y:.2f}), direction={self.direction:.2f}, scale={scale_factor:.2f}")
