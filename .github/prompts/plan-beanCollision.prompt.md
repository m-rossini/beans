Plan: Implement bean collisions inside `SpriteMovementSystem`

Goal
- Implement runtime bean-bean collisions inside `SpriteMovementSystem` so that when two bean sprites overlap by at least 2 pixels of circle intersection area:
  - Both beans take energy damage calculated from speed, size, and sex multipliers (ladies-first tuple mapped to enum names).
  - Energies are updated immediately via the Bean DTO (`to_state()` / `update_from_state()`).
  - Beans' directions and speeds are updated using elastic collisions (restitution = 1, mass ∝ radius²).
  - Target positions are nudged so the sprites will not visually overlap on the next frame.

High-level approach (child-simple)
1. Keep the existing `move_sprite` method exactly as it is. It computes the proposed new positions for each sprite and already applies wall-bounce energy loss.
2. Add a new method on `SpriteMovementSystem` named `resolve_collisions` that:
   - takes a list of `(sprite, target_x, target_y)` for all sprites this frame,
   - finds neighbor pairs that overlap by computing the exact circle intersection area,
   - if intersection_area >= 2 pixels then it's a clash,
   - compute damage T using collision config and relative pixel speed,
   - split T so the smaller bean takes the larger share (formula below), apply sex multipliers, and immediately subtract energy via bean DTO,
   - compute elastic collision outcome (new velocity vectors) and update both `bean.speed` (model) and `sprite.direction` (visual),
   - nudge the target positions along the collision normal so circles are separated by at least rA + rB,
   - return mapping `sprite -> (adjusted_x, adjusted_y)` and `damage_report` for logging.
3. In `WorldWindow.on_update` (or the update orchestrator), do the following each frame:
   - For each sprite call `tx, ty, _ = movement.move_sprite(sprite, width, height)` and collect targets.
   - Call `adjusted_targets, damage_report = movement.resolve_collisions(targets, width, height)`.
   - For each sprite call `sprite.update_from_bean(delta_time, adjusted_targets[sprite])` so visuals interpolate to non-overlapping targets.

Why inside movement?
- `move_sprite` already deducts energy on wall bounces using the Bean DTO pattern (to_state/update_from_state). Keeping collision energy logic inside the movement system keeps the behavior consistent and the orchestrator flow simple: movement → collisions (energy updates) → visuals.

Detailed step-by-step plan (very explicit)
PHASE 1 — Tests (TDD-first)
1. Create a branch for tests: `git checkout -b feat/collision-tests`.
2. Create `tests/test_collision.py` and add the following behavioral tests (they should only assert observable outcomes: bean.energy, sprite.direction or distances):
   - `test_no_damage_below_area_threshold`
     - Place two beans so circle intersection area = 1.9 pixels.
     - Run one frame: call `move_sprite` for each sprite, call `resolve_collisions`, call `sprite.update_from_bean`.
     - Assert: both `bean.energy` unchanged and `sprite.direction` unchanged.
   - `test_minimal_clash_causes_damage_and_nudge`
     - Place two equal beans so area = 2.1 px, moving slowly towards each other.
     - After one frame assert: both energies decreased (after sex multipliers) and final center distance ≥ rA + rB − 1e-3.
   - `test_speed_scaling_damage`
     - Two scenarios same geometry: low vs high relative speeds.
     - After one frame assert: total damage high_speed > total damage low_speed.
   - `test_size_asymmetry_damage_split`
     - Small vs large bean collision at same speeds.
     - After one frame assert: smaller bean lost a larger share of total damage per the formula.
   - `test_sex_multiplier_ladies_first_mapping`
     - Configure `collision_damage_sex_factors = (1.05, 1.0)` in a test config loader.
     - Collide female vs male with equal size and speed.
     - Assert: female energy lost > male energy lost (within tolerance consistent with mapping).
   - `test_direction_change_avoids_future_overlap`
     - Head-on collision then run next frame movement; assert that after second movement the sprites do not overlap.
3. Commit and push the tests:
   - `git add tests/test_collision.py`
   - `git commit -m "tests(collision): add behavioral tests for bean collisions"`
   - `git push --set-upstream origin feat/collision-tests`

PHASE 2 — Implement `resolve_collisions` inside `SpriteMovementSystem`
1. Create implementation branch: `git checkout -b feat/collision-impl`.
2. Edit `src/rendering/movement.py` and add method:
   - Signature: `def resolve_collisions(self, sprite_targets: list[tuple[BeanSprite, float, float]], bounds_width:int, bounds_height:int) -> tuple[dict, dict]:`
     - Returns `(adjusted_targets: dict[BeanSprite,(x,y)], damage_report: dict[bean_id,float])`.
3. Use `SpatialHash` from `src/beans/placement.py` for neighbor queries to avoid O(n²).
4. Detection (exact, per requirement):
   - For neighbor pair compute distance `d` and radii `r0`, `r1`.
   - If `d >= r0 + r1` → no intersection.
   - Else compute circle-circle intersection area (standard formula); declare clash if area >= 2.0.
5. Damage calculation:
   - Use pixel velocities (convert `bean.speed` to pixels_per_unit_speed).
   - Compute u1, u2 velocity vectors in pixels/tick.
   - relative_speed = norm(u1 - u2)
   - T_raw = collision_base_damage * (relative_speed * collision_damage_speed_factor)
   - T = max(T_raw, collision_min_damage)
   - size split: let small_size, large_size be diameters
     - damage_small = T * (large_size / (small_size + large_size))
     - damage_large = T - damage_small
   - sex factor: loader provides `collision_damage_sex_factors` tuple `(female, male)` mapped to a dict `{ 'FEMALE': female, 'MALE': male }` — final damage = damage_before * sex_factor[bean.sex.name]
6. Apply damage immediately via DTO:
   - `s = bean.to_state(); s.energy -= damage; bean.update_from_state(s)`
   - Accumulate in `damage_report[bean.id]`.
7. Elastic collision physics (restitution=1):
   - Mass m = radius**2 (area proportional)
   - Use vector formula:
     - unorm = (x1 - x2)/|x1 - x2|
     - p = 2 * dot(u1 - u2, unorm) / (m1 + m2)
     - v1 = u1 - p * m2 * unorm
     - v2 = u2 + p * m1 * unorm
   - Convert v back to speed magnitude in model units: `new_speed = norm(v) / pixels_per_unit_speed`
   - New direction: `degrees(atan2(v_y, v_x))`
   - Update bean.speed and sprite.direction via DTO and property set respectively:
     - `s = bean.to_state(); s.speed = new_speed; bean.update_from_state(s)`
     - `sprite.direction = new_dir`
8. Nudge targets:
   - After computing new velocities, shift `tx,ty` along normal so distance >= r0 + r1.
9. Logging: use `logger.debug` with concise messages about collisions and damage per bean.
10. Commit and push implementation changes.

PHASE 3 — Integrate in `WorldWindow.on_update`
1. Create branch: `git checkout -b feat/collision-integration`.
2. Change update flow in `src/rendering/window.py`:
   - Collect `targets = []`
   - For each sprite: `tx, ty, _ = movement.move_sprite(sprite, width, height); targets.append((sprite, tx, ty))`
   - `adjusted_targets, damage_report = movement.resolve_collisions(targets, width, height)`
   - For each sprite: `sprite.update_from_bean(delta_time, adjusted_targets[sprite])`
3. Commit and push.

PHASE 4 — Config knobs and mapping
1. Create branch: `git checkout -b feat/collision-config`.
2. Edit `src/config/loader.py` `BeansConfig` to add defaults:
   - `collision_enable: bool = True`
   - `collision_base_damage: float = 5.0`
   - `collision_min_damage: float = 0.5`
   - `collision_damage_speed_factor: float = 0.05`
   - `collision_damage_size_exponent: float = 1.0` (optional)
   - `collision_damage_sex_factors: tuple[float, float] = (1.05, 1.0)  # (FEMALE, MALE)`
3. In loader map tuple to dict: `collision_damage_sex_map = { Sex.FEMALE.name: tuple[0], Sex.MALE.name: tuple[1] }` and attach to `beans_config`.
4. Commit and push.

PHASE 5 — Run tests, profiling & PR
1. Run the tests you created:
   - `make test` (if available) or `pytest tests/test_collision.py`
2. If failures, fix smallest failing units and re-run.
3. Profile intersection-area code; if too slow, switch to an epsilon distance check.
4. Open PR(s) per branch and request reviews.

Exact short formulas (copy/paste friendly)
- Circle intersection area (when d < r0 + r1):
  - a = r0*r0*acos((d*d + r0*r0 - r1*r1) / (2*d*r0))
  - b = r1*r1*acos((d*d + r1*r1 - r0*r0) / (2*d*r1))
  - c = 0.5 * sqrt((-d + r0 + r1)*(d + r0 - r1)*(d - r0 + r1)*(d + r0 + r1))
  - area = a + b - c
- Elastic collision vector update (restitution = 1):
  - m1 = r0**2; m2 = r1**2
  - unorm = (x1 - x2) / |x1 - x2|
  - p = 2 * dot(u1 - u2, unorm) / (m1 + m2)
  - v1 = u1 - p * m2 * unorm
  - v2 = u2 + p * m1 * unorm
- Damage calculation:
  - relative_speed = norm(u1 - u2)  # pixels/tick
  - T_raw = collision_base_damage * (relative_speed * collision_damage_speed_factor)
  - T = max(T_raw, collision_min_damage)
  - damage_small = T * (large_size / (small_size + large_size))
  - damage_large = T - damage_small
  - final_damage = damage_before * sex_factor_map[bean.sex.name]

Notes & confirmations
- Collisions implemented inside `SpriteMovementSystem` (per user instruction).
- Physics: elastic collisions with restitution = 1.
- `bean.speed` WILL be updated after collisions (user confirmed).
- Sex-factor config: ladies-first tuple `(female, male)` mapped to `{ 'FEMALE':..., 'MALE':... }`.
- Clash threshold: exact intersection area ≥ 2 pixels.

If you want me to start creating the Phase 1 test file (`tests/test_collision.py`) now, say "Go" and I will create the file on a new branch and push the tests. If you want changes to names or numeric defaults, tell me what to change before I create tests.
