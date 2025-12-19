## Plan: Testable, Encapsulated Food Visualization in WorldWindow

Implement food and dead bean food visualization in `WorldWindow` using testable, encapsulated logic. Only necessary methods/functions will be exposed, following high cohesion and low coupling.

### Steps
1. Add a private method in `WorldWindow` to retrieve all food positions and quantities/types from the world's food manager, using a generic interface.
2. Create a private helper method (e.g., `_draw_food_square`) to handle drawing a food square at a given position, with color and size scaling by quantity and type.
3. In `on_draw`, before drawing beans, iterate over food positions and call the helper to draw each food square.
4. Ensure all new logic is testable by exposing only what is needed (e.g., helper methods for rendering can be tested via dependency injection or by extracting pure functions if required).
5. Add/adjust tests to verify correct food rendering, color/size scaling, and that only required methods are public.

### Further Considerations
1. Keep all new helpers/methods private unless public access is required for testing or integration.
2. If pure functions are needed for testability, place them in a dedicated module (e.g., `rendering/food_render_utils.py`).
3. Document the interface expected from the food manager for future extensibility.
