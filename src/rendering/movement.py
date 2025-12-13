import logging
import math
from typing import List, Tuple, Dict

from .bean_sprite import BeanSprite

logger = logging.getLogger(__name__)

from beans.placement import SpatialHash


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
        logger.debug(f">>>>> MovementSystem.move_sprite: bean={bean.id}, speed={bean.speed:.2f}, dx={dx:.2f}, dy={dy:.2f}, target=({new_x:.2f},{new_y:.2f}), collisions={collisions}")
        # For each collision, deduct energy via DTO update
        if collisions > 0:
            loss = sprite.bean.beans_config.energy_loss_on_bounce
            for _ in range(collisions):
                state = sprite.bean.to_state()
                state.energy -= loss
                sprite.bean.update_from_state(state)

        return new_x, new_y, collisions

    def resolve_collisions(self, sprite_targets: List[Tuple[BeanSprite, float, float]], bounds_width: int, bounds_height: int) -> Tuple[Dict[BeanSprite, Tuple[float, float]], Dict[int, float]]:
        """Detect and resolve inter-bean collisions for a frame.

        Args:
            sprite_targets: list of (sprite, target_x, target_y) as produced by `move_sprite`.
            bounds_width: world width (unused currently, reserved for future use).
            bounds_height: world height.

        Returns:
            adjusted_targets: mapping sprite -> (new_x, new_y) after nudging
            damage_report: mapping bean.id -> total damage applied this frame

        """
        adjusted: Dict[BeanSprite, Tuple[float, float]] = {}
        damage_report: Dict[int, float] = {}

        if not sprite_targets:
            return adjusted, damage_report

        # Initialize adjusted targets with proposed positions
        for sprite, tx, ty in sprite_targets:
            adjusted[sprite] = (tx, ty)

        # Prepare spatial hash for neighbor queries if available
        positions_map: Dict[Tuple[float, float], BeanSprite] = {}
        sizes: Dict[BeanSprite, float] = {}
        pixels_per_unit = None
        for sprite, tx, ty in sprite_targets:
            positions_map[(tx, ty)] = sprite
            sizes[sprite] = sprite.bean.size
            if pixels_per_unit is None:
                pixels_per_unit = getattr(sprite.bean.beans_config, 'pixels_per_unit_speed', 1.0)

        avg_size = max(1, int(sum(sizes.values()) / len(sizes)))

        if SpatialHash is not None:
            spatial = SpatialHash(cell_size=avg_size, width=bounds_width, height=bounds_height)
            for (tx, ty), sprite in positions_map.items():
                spatial.insert(tx, ty)

        handled_pairs = set()

        def circle_intersection_area(r0: float, r1: float, d: float) -> float:
            if d >= r0 + r1:
                return 0.0
            if d <= abs(r0 - r1):
                # One circle is completely inside the other
                return math.pi * min(r0, r1) ** 2
            # standard formula
            try:
                a = r0 * r0 * math.acos((d * d + r0 * r0 - r1 * r1) / (2 * d * r0))
                b = r1 * r1 * math.acos((d * d + r1 * r1 - r0 * r0) / (2 * d * r1))
                c = 0.5 * math.sqrt(max(0.0, (-d + r0 + r1) * (d + r0 - r1) * (d - r0 + r1) * (d + r0 + r1)))
                return a + b - c
            except Exception:
                # Fallback in degenerate numeric cases
                return 0.0

        def vec_from_speed_dir(speed_units: float, direction_deg: float, pixels_per_unit: float) -> Tuple[float, float]:
            speed_px = speed_units * pixels_per_unit
            r = math.radians(direction_deg)
            return math.cos(r) * speed_px, math.sin(r) * speed_px

        # Iterate sprites and their neighbors
        for sprite, tx, ty in sprite_targets:
            # Query neighbors
            neighbor_positions = []
            if SpatialHash is not None:
                neighbor_positions = spatial.get_neighbors(tx, ty, radius=sprite.bean.size)
            else:
                neighbor_positions = [pos for pos in positions_map.keys()]

            for npos in neighbor_positions:
                if npos == (tx, ty):
                    continue
                other = positions_map.get(npos)
                if other is None:
                    continue

                pair_key = tuple(sorted((sprite.bean.id, other.bean.id)))
                if pair_key in handled_pairs:
                    continue

                # Compute radii and distance
                r0 = sprite.bean.size / 2.0
                r1 = other.bean.size / 2.0
                d = math.hypot(tx - npos[0], ty - npos[1])

                area = circle_intersection_area(r0, r1, d)
                if area < 2.0:
                    continue

                # Mark handled
                handled_pairs.add(pair_key)

                # Prepare config knobs with safe defaults
                cfg = sprite.bean.beans_config
                base = getattr(cfg, 'collision_base_damage', 5.0)
                speed_factor = getattr(cfg, 'collision_damage_speed_factor', 0.05)
                min_damage = getattr(cfg, 'collision_min_damage', 0.5)
                sex_tuple = getattr(cfg, 'collision_damage_sex_factors', None)
                sex_map = getattr(cfg, 'collision_damage_sex_map', None)
                if sex_map is None:
                    if sex_tuple and len(sex_tuple) >= 2:
                        sex_map = { 'FEMALE': sex_tuple[0], 'MALE': sex_tuple[1] }
                    else:
                        sex_map = { 'FEMALE': 1.0, 'MALE': 1.0 }

                # Velocities in pixels/tick
                pixels_per_unit = getattr(cfg, 'pixels_per_unit_speed', pixels_per_unit or 1.0)
                u1x, u1y = vec_from_speed_dir(sprite.bean.speed, sprite.direction, pixels_per_unit)
                u2x, u2y = vec_from_speed_dir(other.bean.speed, other.direction, pixels_per_unit)
                rel_vx = u1x - u2x
                rel_vy = u1y - u2y
                relative_speed = math.hypot(rel_vx, rel_vy)

                # Damage computation
                T_raw = base * (relative_speed * speed_factor)
                T = max(T_raw, min_damage)

                # Size split: smaller takes larger share
                s0 = sprite.bean.size
                s1 = other.bean.size
                if s0 <= s1:
                    damage_small = T * (s1 / (s0 + s1))
                    damage_large = T - damage_small
                    dmg_a = damage_small
                    dmg_b = damage_large
                    a_is_small = True
                else:
                    damage_small = T * (s0 / (s0 + s1))
                    damage_large = T - damage_small
                    dmg_a = damage_large
                    dmg_b = damage_small
                    a_is_small = False

                # Apply sex multipliers
                factor_a = sex_map.get(sprite.bean.sex.name, 1.0)
                factor_b = sex_map.get(other.bean.sex.name, 1.0)
                final_a = dmg_a * factor_a
                final_b = dmg_b * factor_b

                # Apply damage via DTO
                sstate = sprite.bean.to_state()
                sstate.energy -= final_a
                sprite.bean.update_from_state(sstate)
                damage_report[sprite.bean.id] = damage_report.get(sprite.bean.id, 0.0) + final_a

                ostate = other.bean.to_state()
                ostate.energy -= final_b
                other.bean.update_from_state(ostate)
                damage_report[other.bean.id] = damage_report.get(other.bean.id, 0.0) + final_b

                logger.debug(f">>>>> Collision: beans=({sprite.bean.id},{other.bean.id}), damage=({final_a:.3f},{final_b:.3f}), area={area:.3f}")

                # Elastic collision resolution (2D) with mass proportional to area (radius^2)
                m1 = r0 ** 2
                m2 = r1 ** 2
                # Positions at impact
                x1, y1 = tx, ty
                x2, y2 = npos
                nx = x1 - x2
                ny = y1 - y2
                nd = math.hypot(nx, ny)
                if nd == 0:
                    # choose arbitrary normal
                    unx, uny = 1.0, 0.0
                else:
                    unx, uny = nx / nd, ny / nd

                # relative velocity along normal
                relvx = u1x - u2x
                relvy = u1y - u2y
                p = 0.0
                denom = (m1 + m2)
                if denom != 0:
                    p = 2 * (relvx * unx + relvy * uny) / denom

                v1x = u1x - p * m2 * unx
                v1y = u1y - p * m2 * uny
                v2x = u2x + p * m1 * unx
                v2y = u2y + p * m1 * uny

                # Convert back to model speed units
                new_speed_a = math.hypot(v1x, v1y) / pixels_per_unit
                new_speed_b = math.hypot(v2x, v2y) / pixels_per_unit
                new_dir_a = math.degrees(math.atan2(v1y, v1x)) if (v1x != 0 or v1y != 0) else sprite.direction
                new_dir_b = math.degrees(math.atan2(v2y, v2x)) if (v2x != 0 or v2y != 0) else other.direction

                # Update bean speeds via DTO and sprite directions
                sstate2 = sprite.bean.to_state()
                sstate2.speed = new_speed_a
                sprite.bean.update_from_state(sstate2)
                sprite.direction = new_dir_a

                ostate2 = other.bean.to_state()
                ostate2.speed = new_speed_b
                other.bean.update_from_state(ostate2)
                other.direction = new_dir_b

                # Nudge targets to remove overlap
                overlap = (r0 + r1) - d
                if overlap > 0:
                    # shift each by half overlap along normal
                    shift_x = (unx * (overlap / 2.0))
                    shift_y = (uny * (overlap / 2.0))
                    ax, ay = adjusted[sprite]
                    bx, by = adjusted[other]
                    adjusted[sprite] = (ax + shift_x, ay + shift_y)
                    adjusted[other] = (bx - shift_x, by - shift_y)

        return adjusted, damage_report
