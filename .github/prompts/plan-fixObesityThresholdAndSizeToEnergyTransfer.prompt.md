## Plan: Fix Obesity Threshold and Size-to-Energy Transfer

Check this is a fresh branch.
Ensure TDD is followed.
NEVER USE INTROSPECTION TO SOLVE ANY PROBLEM UNLESS EXPLICITLY ASKED TO DO SO IN THE INSTRUCTIONS.
NEVER USE CODE COMMENTS UNLESS EXPLICITLY ASKED TO DO SO IN THE INSTRUCTIONS.
NEVER USE LOCAL IMPORTS UNLESS EXPLICITLY ASKED TO DO SO IN THE INSTRUCTIONS.

The clamping logic is correct if we:
- Transfer any "lost" or "excess" size (from clamping) to energy.
- Fix the obesity threshold calculation so it can actually be reached before clamping.

### Steps
1. **Fix Obesity Threshold Calculation**
   - In `DefaultSurvivalChecker.check` (`src/beans/survival.py`), set the threshold to a value that can be reached before clamping, e.g.:
     - `threshold = config.max_bean_size * config.obesity_threshold_factor` (where factor < 1)
     - Or, `threshold = min(config.max_bean_size, config.initial_bean_size * config.obesity_threshold_factor)`
   - Ensure the threshold is always ≤ `max_bean_size`.

2. **Transfer Clamped Size to Energy**
   - In `StandardEnergySystem._clamp_size` (`src/beans/energy_system.py`), when clamping occurs:
     - Calculate the difference between attempted and clamped size.
     - Convert this difference to energy using the config ratio.
     - Adjust `bean_state.energy` accordingly.
   - Update the method to return both new size and updated energy.

3. **Update Call Sites**
   - Update `apply_energy_system` to use the new return signature and propagate the energy adjustment.

4. **Test**
   - Add/update tests to verify:
     - Beans can die from obesity at the correct threshold.
     - No energy is lost when clamping occurs.

### Further Considerations
- Validate config values at startup to ensure the threshold is always reachable.
- Document the new behavior for maintainers.
