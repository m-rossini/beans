# 2025-12-09-bean-dynamics-speed-isolation.md

## Context
A refactor was performed to strictly decouple bean logic from sprite/rendering logic, and to ensure that only speed logic is handled by `BeanDynamics`. The `target_size` attribute is now managed by the energy system and is recalculated every world step. All usages and tests were updated to reflect these changes.

## Problem
- `BeanState` previously included or was expected to include `position` and `direction`, which are sprite/rendering concerns, not bean logic.
- `BeanDynamics` contained methods for updating position and direction, which violated the separation of concerns.
- The `target_size` field was not consistently set in all `BeanState` instantiations, causing validation errors.

## Solution
- Removed all position and direction logic from `BeanDynamics` and `BeanState`.
- `BeanDynamics` now only provides speed calculation logic.
- All instantiations of `BeanState` (in beans, tests, and DTOs) were updated to include the required `target_size` field.
- The energy system is now the sole owner of `target_size` calculation, and it is set each world step.
- All tests were updated and now pass, confirming the correctness of the refactor.

## Design Decisions
- Strict separation of bean logic (state, speed, energy, size) from sprite/rendering logic (position, direction).
- `BeanDynamics` is responsible only for speed-related calculations.
- `target_size` is managed by the energy system, not by the bean or movement logic.

## Challenges
- Ensuring all usages of `BeanState` included the new `target_size` field.
- Refactoring tests and code to remove all dependencies on position/direction in bean logic.

## How to Run
- Run `make test` to execute all tests and verify correctness.
- All tests should pass with the new structure.

## Diagram
See [2025-12-09-bean-dynamics-speed-isolation-diagram.md](2025-12-09-bean-dynamics-speed-isolation-diagram.md) for a mermaid diagram of the updated architecture.
