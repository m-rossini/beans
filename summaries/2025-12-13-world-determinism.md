# 2025-12-13 World Determinism: BeanContext & Seed

Short summary
-------------
This change introduces deterministic bean creation and speed calculation using a world-local random number generator (RNG) seeded by `WorldConfig.seed`. The solution keeps default behavior unchanged and provides deterministic factory helpers to construct genotypes and phenotypes directly for tests.

Key changes
-----------
- Added `seed: Optional[int]` in `WorldConfig` so deterministic runs can be configured in JSON.
- Added `src/beans/context.py` containing a `BeanContext` Pydantic model, which includes `bean_count`, `male_count`, and an (internal) RNG.
- Updated `World` to own a private RNG (`self._rng`) created from `WorldConfig.seed` and to build a `BeanContext` that is passed into `_create_beans`.
- Modified `_create_beans` signature to accept `BeanContext` and to pass the `bean_context.rng` into the genetics factory functions.
- Updated `src/beans/genetics.py` to accept an optional RNG for `create_random_genotype` and `create_phenotype`.
- Added deterministic helpers:
  - `create_genotype_from_values(genes)`
  - `create_phenotype_from_values(config, genotype, age, speed, energy, size, target_size)`

Testing & validation
--------------------
- Added tests for RNG reproducibility in `tests/test_genetics_rng.py`.
- Replaced implementation-level `BeanContext` tests with public API world-level deterministic tests in `tests/test_world_seed_deterministic.py` that assert:
  - Two `World` instances with the same `WorldConfig.seed` create identical genotypes and phenotypes.
  - Two seeded worlds compute the same `bean.speed` after `World.step()` given the same initial `BeanState`.
- Modified `tests/test_bean_dynamics.py` to include a deterministic `World.step()` speed test and a min-speed-floor test.
- Ran full test suite; all tests passed.

Notes & next steps
------------------
- `BeanContext` is intended to be runtime-only; it uses `random.Random` which is supported in the Pydantic model via `arbitrary_types_allowed`.
- The `seed` field is optional and defaults to `null` (no seed) for backward compatibility.
- `World._rng` is private and is not exposed to avoid external mutation; tests use `WorldConfig.seed` or `create_*_from_values` helper methods.

How to use
----------
- To create a deterministic world from config JSON, set the `seed` field under `world` to a number in your config file. Example:
  ```json
  {
    "world": {
      "width": 800,
      "height": 600,
      "seed": 42,
      ...
    },
    "beans": { ... }
  }
  ```
- For tests or situations where you need precise gene values, use the factory helpers `create_genotype_from_values` and `create_phenotype_from_values` to construct deterministic beans.

PR & Code review tips
---------------------
- Prefers small incremental PRs. The branch created for this work is `feat/deterministic-bean-context`.
- Tests use only public APIs. Avoid introducing new test-only hooks — use helpers instead.

Change log
----------
- `src/config/loader.py` — add `seed` field parsing.
- `src/beans/context.py` — new model.
- `src/beans/world.py` — create RNG, use `BeanContext`, inject RNG into factory calls.
- `src/beans/genetics.py` — RNG-aware factories and deterministic helpers.
- `tests/` — deterministic and reproducibility tests added and modified.

Maintenance
-----------
- Reviewers should verify no private attributes are used in tests and that the seed path is robust.
- Consider adding `World.create_with_seed` in a future PR if additional helper is desired.

