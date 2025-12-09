## Rendering Movement & Bounce Implementation (2025-12-08)

Summary
-------
- Movement and bounce behavior for bean sprites is implemented in the rendering layer (UI-only). This preserves SOLID boundaries: Bean models do *not* include position or direction fields; the UI owns these concerns.
- The `SpriteMovementSystem` performs movement and edge-bounce detection using sprite visual bounds.
- Energy deductions resulting from bounces are applied to the model via the `BeanState` DTO (Pydantic), consistent with the energy system pattern.
- Negative speed is treated as reverse movement vector; sprite direction remains unchanged, but movement vector is reversed.
- `delta_time` is used only for visual animation smoothing when rendering sprites, not for movement magnitude or logic.

Design Decisions
----------------
- Keep position/direction UI-only: The model (`Bean`) does not track UI coordinates or visual direction; this avoids coupling the model to display concerns and simplifies future multi-view scenarios.
- Movement per tick: Movement is computed as pixels-per-tick using the `Bean` speed property and a configurable `pixels_per_unit_speed` factor (default 1.0), so speeds are 'per tick' values.
- Bounce reflection: We reflect the direction across the axis of collision (mirror angle), preserving physical angle-of-incidence behavior.
- Energy loss: Each collision (edge bounce) subtracts an absolute energy quantity `energy_loss_on_bounce` from the bean model. Multiple collisions in one move are counted and deducted per-collision.
- DTO updates for mutation: All changes to bean's energy happen via `BeanState` DTO (`bean.to_state()` and `bean.update_from_state(state)`), preserving a single responsibility and consistent mutation flow.

Files Added/Modified
---------------------
- `src/rendering/movement.py` — `SpriteMovementSystem` with movement and bounce logic.
- `src/rendering/bean_sprite.py` — `BeanSprite.update_from_bean()` now accepts `delta_time`, `movement_system`, and `bounds` and interpolates movement.
- `src/rendering/window.py` — `WorldWindow` now instantiates the movement system and passes to sprites during updates.
- `src/config/loader.py` — `BeansConfig` now includes `pixels_per_unit_speed` and `energy_loss_on_bounce` configuration options.
- `tests` — Tests for movement, bounce reflection, energy deduction, and visual interpolation are added.

Notes & Future Work
-------------------
- Multi-bounce per-tick exactness: currently we detect and reflect per movement call. If speed is extremely large and crosses multiple edges within a single tick, the movement may not perform exact multi-segment reflections; consider multi-seg motion for physics fidelity.
- Option to quantize bounce angles could be added if desired; the current behavior uses mirror reflection across axis.
- Consider exposing a pixel-per-speed conversion option in the UI or config if different coordinate systems are needed.

How to Run Tests
-----------------
Use the project's Makefile test targets so that `PYTHONPATH` is configured properly:

```sh
make test-specific TEST_SPECIFIC=tests/test_movement.py
make test  # run all tests
```

Outcome: All unit tests pass after the changes.

Contact
-------
If you need the multi-bounce physics, quantized bounce angles, or a configurable energy loss policy (fraction vs absolute), let me know and I'll implement these in follow-up commits.
