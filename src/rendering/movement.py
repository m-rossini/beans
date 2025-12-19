import logging
import math
from typing import Dict, List, Tuple

from beans.placement import SpatialHash
from config.loader import BeansConfig

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
        msg = (
            f">>>>> MovementSystem.move_sprite: bean={bean.id}, speed={bean.speed:.2f}, "
            f"dx={dx:.2f}, dy={dy:.2f}, target=({new_x:.2f},{new_y:.2f}), collisions={collisions}"
        )
        logger.debug(msg)
        # For each collision, deduct energy via DTO update
        if collisions > 0:
            loss = sprite.bean.beans_config.energy_loss_on_bounce
            for _ in range(collisions):
                state = sprite.bean.to_state()
                state.energy -= loss
                sprite.bean.update_from_state(state)

        return new_x, new_y, collisions

    def _circle_intersection_area(self, r0: float, r1: float, d: float) -> float:
        if d >= r0 + r1:
            return 0.0
        if d <= abs(r0 - r1):
            # One circle is completely inside the other
            return math.pi * min(r0, r1) ** 2

        denom_a = 2 * d * r0
        denom_b = 2 * d * r1
        if denom_a == 0 or denom_b == 0:
            return 0.0

        arg_a = (d * d + r0 * r0 - r1 * r1) / denom_a
        arg_b = (d * d + r1 * r1 - r0 * r0) / denom_b
        arg_a = max(-1.0, min(1.0, arg_a))
        arg_b = max(-1.0, min(1.0, arg_b))

        a = r0 * r0 * math.acos(arg_a)
        b = r1 * r1 * math.acos(arg_b)
        sqrt_arg = max(0.0, (-d + r0 + r1) * (d + r0 - r1) * (d - r0 + r1) * (d + r0 + r1))
        c = 0.5 * math.sqrt(sqrt_arg)
        return a + b - c

    def _vec_from_speed_dir(self, speed_units: float, direction_deg: float, pixels_per_unit: float) -> Tuple[float, float]:
        speed_px = speed_units * pixels_per_unit
        r = math.radians(direction_deg)
        return math.cos(r) * speed_px, math.sin(r) * speed_px

    def _initialize_collision_data(
        self,
        sprite_targets: List[Tuple[BeanSprite, float, float]],
        bounds_width: int,
        bounds_height: int,
    ) -> Tuple[Dict[Tuple[float, float], BeanSprite], Dict[BeanSprite, float], SpatialHash]:
        """Prepare data structures for collision detection: positions map, sizes, and spatial hash."""
        positions_map = {(tx, ty): sprite for sprite, tx, ty in sprite_targets}
        sizes = {sprite: sprite.bean.size for sprite, tx, ty in sprite_targets}
        avg_size = max(1, int(sum(sizes.values()) / len(sizes)))
        spatial = SpatialHash(cell_size=avg_size, width=bounds_width, height=bounds_height)
        for (tx, ty), sprite in positions_map.items():
            spatial.insert(tx, ty)
        return positions_map, sizes, spatial

    def _detect_collision(
        self,
        sprite_a: BeanSprite,
        sprite_b: BeanSprite,
        pos_a: Tuple[float, float],
        pos_b: Tuple[float, float],
    ) -> bool:
        """Check if two sprites are colliding based on intersection area."""
        r0 = sprite_a.bean.size / 2.0
        r1 = sprite_b.bean.size / 2.0
        d = math.hypot(pos_a[0] - pos_b[0], pos_a[1] - pos_b[1])
        area = self._circle_intersection_area(r0, r1, d)
        return area >= 2.0

    def _compute_collision_damage(
        self,
        sprite_a: BeanSprite,
        sprite_b: BeanSprite,
        pos_a: Tuple[float, float],
        pos_b: Tuple[float, float],
        cfg: BeansConfig,
    ) -> Tuple[float, float]:
        """Compute damage for colliding sprites, including base, speed, size split, and sex multipliers."""
        base = cfg.collision_base_damage
        speed_factor = cfg.collision_damage_speed_factor
        min_damage = cfg.collision_min_damage
        female_factor, male_factor = cfg.collision_damage_sex_factors

        # Relative speed
        u1x, u1y = self._vec_from_speed_dir(sprite_a.bean.speed, sprite_a.direction, cfg.pixels_per_unit_speed)
        u2x, u2y = self._vec_from_speed_dir(sprite_b.bean.speed, sprite_b.direction, cfg.pixels_per_unit_speed)
        relative_speed = math.hypot(u1x - u2x, u1y - u2y)

        T = max(base * (relative_speed * speed_factor), min_damage)

        # Size split
        s0, s1 = sprite_a.bean.size, sprite_b.bean.size
        if s0 <= s1:
            dmg_a = T * (s1 / (s0 + s1))
            dmg_b = T - dmg_a
        else:
            dmg_a = T * (s0 / (s0 + s1))
            dmg_b = T - dmg_a

        # Sex multipliers
        factor_a = female_factor if sprite_a.bean.sex.name == "FEMALE" else male_factor
        factor_b = female_factor if sprite_b.bean.sex.name == "FEMALE" else male_factor
        return dmg_a * factor_a, dmg_b * factor_b

    def _apply_damage(
        self,
        sprite_a: BeanSprite,
        sprite_b: BeanSprite,
        damage_a: float,
        damage_b: float,
        damage_report: Dict[int, float],
    ) -> None:
        """Apply damage to beans via DTO and update damage report."""
        state_a = sprite_a.bean.to_state()
        state_a.energy -= damage_a
        sprite_a.bean.update_from_state(state_a)
        damage_report[sprite_a.bean.id] = damage_report.get(sprite_a.bean.id, 0.0) + damage_a

        state_b = sprite_b.bean.to_state()
        state_b.energy -= damage_b
        sprite_b.bean.update_from_state(state_b)
        damage_report[sprite_b.bean.id] = damage_report.get(sprite_b.bean.id, 0.0) + damage_b

        logger.debug(f">>>>> Collision damage: beans=({sprite_a.bean.id},{sprite_b.bean.id}), damage=({damage_a:.3f},{damage_b:.3f})")

    def _resolve_elastic_collision(
        self,
        sprite_a: BeanSprite,
        sprite_b: BeanSprite,
        pos_a: Tuple[float, float],
        pos_b: Tuple[float, float],
        cfg: BeansConfig,
    ) -> Tuple[float, float, float, float]:
        """Compute new speeds and directions for elastic collision resolution."""
        r0 = sprite_a.bean.size / 2.0
        r1 = sprite_b.bean.size / 2.0
        m1 = r0**2
        m2 = r1**2

        u1x, u1y = self._vec_from_speed_dir(sprite_a.bean.speed, sprite_a.direction, cfg.pixels_per_unit_speed)
        u2x, u2y = self._vec_from_speed_dir(sprite_b.bean.speed, sprite_b.direction, cfg.pixels_per_unit_speed)

        nx, ny = pos_a[0] - pos_b[0], pos_a[1] - pos_b[1]
        nd = math.hypot(nx, ny)
        unx, uny = (nx / nd, ny / nd) if nd > 0 else (1.0, 0.0)

        relvx, relvy = u1x - u2x, u1y - u2y
        p = 2 * (relvx * unx + relvy * uny) / (m1 + m2) if (m1 + m2) != 0 else 0.0

        v1x = u1x - p * m2 * unx
        v1y = u1y - p * m2 * uny
        v2x = u2x + p * m1 * unx
        v2y = u2y + p * m1 * uny

        new_speed_a = math.hypot(v1x, v1y) / cfg.pixels_per_unit_speed
        new_dir_a = math.degrees(math.atan2(v1y, v1x)) if (v1x or v1y) else sprite_a.direction
        new_speed_b = math.hypot(v2x, v2y) / cfg.pixels_per_unit_speed
        new_dir_b = math.degrees(math.atan2(v2y, v2x)) if (v2x or v2y) else sprite_b.direction

        return new_speed_a, new_dir_a, new_speed_b, new_dir_b

    def _nudge_positions(
        self,
        sprite_a: BeanSprite,
        sprite_b: BeanSprite,
        pos_a: Tuple[float, float],
        pos_b: Tuple[float, float],
        adjusted: Dict[BeanSprite, Tuple[float, float]],
    ) -> None:
        """Adjust positions to remove overlap after collision."""
        r0 = sprite_a.bean.size / 2.0
        r1 = sprite_b.bean.size / 2.0
        d = math.hypot(pos_a[0] - pos_b[0], pos_a[1] - pos_b[1])
        overlap = (r0 + r1) - d
        if overlap > 0:
            nx, ny = pos_a[0] - pos_b[0], pos_a[1] - pos_b[1]
            nd = math.hypot(nx, ny)
            unx, uny = (nx / nd, ny / nd) if nd > 0 else (1.0, 0.0)
            shift_x = unx * (overlap / 2.0)
            shift_y = uny * (overlap / 2.0)
            ax, ay = adjusted[sprite_a]
            bx, by = adjusted[sprite_b]
            adjusted[sprite_a] = (ax + shift_x, ay + shift_y)
            adjusted[sprite_b] = (bx - shift_x, by - shift_y)

    def _update_sprite_state(self: BeanSprite, other: BeanSprite, new_speed, new_dir):
        state = other.bean.to_state()
        state.speed = new_speed
        other.bean.update_from_state(state)
        other.direction = new_dir

    def resolve_collisions(
        self,
        sprite_targets: List[Tuple[BeanSprite, float, float]],
        bounds_width: int,
        bounds_height: int,
    ) -> Tuple[Dict[BeanSprite, Tuple[float, float]], Dict[int, float]]:
        """Detect and resolve inter-bean collisions for a frame.

        Args:
            sprite_targets: list of (sprite, target_x, target_y) as produced by `move_sprite`.
            bounds_width: world width (unused currently, reserved for future use).
            bounds_height: world height.

        Returns:
            adjusted_targets: mapping sprite -> (new_x, new_y) after nudging
            damage_report: mapping bean.id -> total damage applied this frame

        """
        adjusted: Dict[BeanSprite, Tuple[float, float]] = {sprite: (tx, ty) for sprite, tx, ty in sprite_targets}
        damage_report: Dict[int, float] = {}
        if not sprite_targets:
            return adjusted, damage_report

        # Check if collisions are enabled
        cfg = sprite_targets[0][0].bean.beans_config
        if not cfg.collision_enable:
            return adjusted, damage_report

        positions_map, sizes, spatial = self._initialize_collision_data(sprite_targets, bounds_width, bounds_height)
        handled_pairs = set()

        for sprite, tx, ty in sprite_targets:
            neighbors = spatial.get_neighbors(tx, ty, radius=sprite.bean.size)
            for npos in neighbors:
                if npos == (tx, ty):
                    continue
                other = positions_map.get(npos)
                if not other or tuple(sorted((sprite.bean.id, other.bean.id))) in handled_pairs:
                    continue
                if self._detect_collision(sprite, other, (tx, ty), npos):
                    handled_pairs.add(tuple(sorted((sprite.bean.id, other.bean.id))))
                    cfg = sprite.bean.beans_config
                    damage_a, damage_b = self._compute_collision_damage(sprite, other, (tx, ty), npos, cfg)
                    self._apply_damage(sprite, other, damage_a, damage_b, damage_report)
                    new_speed_a, new_dir_a, new_speed_b, new_dir_b = self._resolve_elastic_collision(sprite, other, (tx, ty), npos, cfg)
                    # Update via DTO
                    self._update_sprite_state(sprite, new_speed_a, new_dir_a)
                    self._update_sprite_state(other, new_speed_b, new_dir_b)

                    self._nudge_positions(sprite, other, (tx, ty), npos, adjusted)
                    logger.debug(f">>>>> Collision detected between "
                                 f"bean A:{sprite.bean.id} "
                                 f"bean B:{other.bean.id}"
                                 f" at positions A:{(tx, ty)} B:{npos}"
                                 f" applied damage ({damage_a:.2f}, {damage_b:.2f})"
                                 f" old energies ({sprite.bean.energy + damage_a:.2f}, {other.bean.energy + damage_b:.2f})"
                                 f" new energies ({sprite.bean.energy:.2f}, {other.bean.energy:.2f})"
                                 f" new speeds ({new_speed_a:.2f}, {new_speed_b:.2f})"
                                 f" new directions ({new_dir_a:.2f}, {new_dir_b:.2f})"
                    )

        return adjusted, damage_report
