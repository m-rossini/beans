## Plan: Hybrid Food Manager for Environment

Implement a hybrid food management system: use a grid for general food and discrete objects for special cases (e.g., dead beans as food). Food manager will handle food spawning, decay, and dead bean conversion, using `WorldConfig` for world size. Food manager will be instantiated outside and injected by name.

### Steps
1. Define a `FoodManager` interface in a new module (e.g., `src/beans/environment/food_manager.py`).
2. Implement `HybridFoodManager`:
   - Use a grid for general food.
   - Track special food objects (e.g., dead beans) in a list.
   - Add a method like `add_dead_bean_as_food(position, size)` to register dead beans as food.
   - General food decays at 10% of original value per tick.
   - Dead beans decay for 3 rounds, losing 50% of their current value per round; value is measured in size.
3. Update the `Environment` interface and `DefaultEnvironment` to accept a `FoodManager` instance.
4. Refactor environment logic to delegate all food-related operations to the injected `FoodManager`.
5. Add or update tests for both grid-based and object-based food management, including decay logic.

### Further Considerations
1. Specify grid resolution and object structure for special food.
2. Ensure clear API for beans/environment to interact with both food types.
3. Document decay rules for both food types in code and tests.
