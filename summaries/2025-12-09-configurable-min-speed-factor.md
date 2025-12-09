# 2025-12-09-configurable-min-speed-factor.md

## Context

The simulation previously used a hardcoded minimum speed factor in the bean movement lifecycle, causing beans to remain static for too long at early ages. This limited animation and realism, and made tuning difficult. The project requires all such parameters to be configurable and validated through the standard configuration system.

## Decision

- Introduced a new `min_speed_factor` field in `BeansConfig`, loaded from all config files and validated in the loader.
- Refactored `age_speed_factor` to accept and use this configurable minimum, ensuring beans always move at least at the configured minimum speed factor.
- Updated all config files (`small.json`, `medium.json`, `large.json`) to include the new field.
- Added and updated tests to ensure:
  - The minimum is respected in speed calculations.
  - Loader validation fails for out-of-bounds values.
- Fixed a rendering bug in `BeanSprite` interpolation so that visual movement matches test expectations.
- All changes were made following TDD and project coding standards.

## Consequences

- Bean movement is now fully configurable and testable.
- All tests pass, including movement and rendering.
- Future phases must be implemented on feature branches, not main.

## How to Test

- Run `make test` to verify all tests pass.
- Adjust `min_speed_factor` in any config and observe the effect on bean movement at low ages.

## Diagram

See [2025-12-09-configurable-min-speed-factor-diagram.md](2025-12-09-configurable-min-speed-factor-diagram.md)
