import logging
import math

from .bean_sprite import BeanSprite

logger = logging.getLogger(__name__)


def _normalize_angle(angle: float) -> float:
    angle = angle % 360.0
    if angle < 0:
        angle += 360.0
    return angle


class SpriteMovementSystem:
    """Movement system that updates sprite positions and handles wall bounces.

    Movement is purely visual/UI-level so no model position is stored; energy
    deduction messages are applied through the Bean DTO by the caller.
    """

    def move_sprite(self, sprite: BeanSprite, bounds_width: int, bounds_height: int) -> tuple[float, float, int]:
        """Move sprite by bean speed units and apply bounces if bounds crossed.

        Returns the number of edge collisions detected (0, 1, or 2).
        """
        bean = sprite.bean
        # Use bean's speed directly as pixels per tick, scaled by config factor
        pixels_factor = bean.beans_config.pixels_per_unit_speed
        speed_px = bean.speed * pixels_factor
        # Convert direction to radians; direction is degrees
        rads = math.radians(sprite.direction)
        dx = math.cos(rads) * speed_px
        dy = math.sin(rads) * speed_px

        new_x = sprite.center_x + dx
        new_y = sprite.center_y + dy

        radius = bean.size / 2.0
        collisions = 0

        # Horizontal collisions
        if new_x - radius < 0:
            new_x = radius
            sprite.direction = _normalize_angle(180.0 - sprite.direction)
            collisions += 1
        elif new_x + radius > bounds_width:
            new_x = bounds_width - radius
            sprite.direction = _normalize_angle(180.0 - sprite.direction)
            collisions += 1

        # Vertical collisions
        if new_y - radius < 0:
            new_y = radius
            sprite.direction = _normalize_angle(-sprite.direction)
            collisions += 1
        elif new_y + radius > bounds_height:
            new_y = bounds_height - radius
            sprite.direction = _normalize_angle(-sprite.direction)
            collisions += 1

        # Do not update sprite positions directly here; return target coords so the
        # caller (sprite) can interpolate visually.
        logger.debug(f">>>>> MovementSystem.move_sprite: bean={getattr(bean, 'id', None)}, speed={bean.speed:.2f}, dx={dx:.2f}, dy={dy:.2f}, target=({new_x:.2f},{new_y:.2f}), collisions={collisions}")
        # For each collision, deduct energy via DTO update
        if collisions > 0:
            loss = sprite.bean.beans_config.energy_loss_on_bounce
            for _ in range(collisions):
                state = sprite.bean.to_state()
                state.energy -= loss
                sprite.bean.update_from_state(state)

        return new_x, new_y, collisions
