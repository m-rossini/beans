# 2025-11-25 Energy System

## Context
Beans need an energy budget so they can survive (or die) independently of movement; energy should grow slowly each round while movement consumes it, and Worlds must track why beans die.

## Decision
- Extended `BeansConfig` with `initial_energy`, `energy_gain_per_step`, and `energy_cost_per_speed` while validating them via `config.loader` so defaults are centralized and future tuning is easy.
- Added explicit `Bean.energy` bookkeeping and restructured `update(dt)` to return outcome metrics (energy) backed by a private `_energy_tick` helper, keeping the energy math inside the bean and letting callers react to the returned values.
- Introduced `DeadBeanRecord` and `World.dead_beans` so the world can safely remove depleted beans, keep them out of the active pool, and remember they died because energy hit zero.

## Consequences
- The beans still age normally, but now life expectancy meshes with energy budgets; configuration adjustments are safe thanks to the new validation guards.
- Energy-depleted beans are recorded with a readable reason, enabling observability and future gameplay paths like respawning or statistics.

## Testing
- `make test-specific TEST_SPECIFIC=tests/test_energy.py`
- `make test`

## Diagram
- [Energy System Overview](2025-11-25-energy-system-diagram.md)
