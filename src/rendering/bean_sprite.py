import arcade
import logging

from beans.bean import Bean

logger = logging.getLogger(__name__)


class BeanSprite(arcade.Sprite):
    """Sprite representation of a Bean for rendering in the window."""

    def __init__(self, bean: Bean, position: tuple[float, float], color: tuple[int, int, int]):
        logger.info(f">>>>> BeanSprite.__init__: bean_id={bean.id}, position={position}, color={color}")
        self.diameter = bean.beans_config.initial_bean_size
        texture = arcade.make_circle_texture(self.diameter, color)
        super().__init__(texture, center_x=position[0], center_y=position[1])
        self.bean = bean
        self.color = color
        logger.debug(f">>>>> BeanSprite created for bean {bean.id}")

    def update_from_bean(self):
        """Update sprite based on bean state (placeholder for future features)."""
        logger.debug(f">>>>> BeanSprite.update_from_bean: bean_id={self.bean.id}")