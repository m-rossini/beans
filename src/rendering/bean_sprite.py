import arcade
import logging
import random
from typing import Optional

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

    def update_from_bean(self):
        """Update sprite based on bean state (placeholder for future features)."""
        logger.debug(f">>>>> BeanSprite.update_from_bean: bean_id={self.bean.id}")