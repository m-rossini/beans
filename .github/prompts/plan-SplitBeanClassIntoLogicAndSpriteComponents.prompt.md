## Plan: Split Bean Class into Logic and Sprite Components

Separate Bean into pure logic (Bean) and screen representation (BeanSprite) for modularity, enabling dynamic visuals like color changes based on state. Add male/female bean colors to config, render beans as circles with diameter = initial bean size, and handle interactions via sprites.

### Steps
1. Create `BeanSprite` class in `src/rendering/bean_sprite.py` inheriting from `arcade.Sprite`, associating with a `Bean` instance, setting circle shape, position, and sex-based color from config.
2. Extend `BeansConfig` in `src/config/loader.py` with `male_bean_color` and `female_bean_color` fields, update defaults and validation.
3. Update `WorldWindow` in `src/rendering/window.py` to create `BeanSprite` instances for each bean on init, replace circle drawing with sprite rendering, and sync sprites on updates/removals.
4. Add `tests/test_bean_sprite.py` for sprite creation, color assignment, and updates; update `tests/test_rendering_window.py` to verify sprite list and properties.
5. Run `make test` and `make test-cov` to validate changes, then test rendering with `run_window.py`.

### Further Considerations
1. Should sprites update positions dynamically if beans gain movement logic, or keep static as now?
2. Consider adding energy-based color states (e.g., low_energy_color) for future visuals?
