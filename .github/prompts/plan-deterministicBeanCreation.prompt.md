Plan: Deterministic Bean Creation & World Seed (BeanContext)

Overview
========
This plan implements deterministic bean creation and deterministic speed evaluation via the public World API.
Goal: allow deterministic RPG independent of global RNG state by having the World own a private RNG seeded from `WorldConfig.seed`. Expose RNG-aware deterministic factory options as public APIs while keeping default behavior unchanged.

High-level objectives
---------------------
- Introduce a `BeanContext` model (Pydantic) for bean creation context (bean_count, male_count, rng).
- Add `WorldConfig.seed` to allow deterministic `World` creation and `World` owning a private RNG (no external mutation).
- Modify `_create_beans` to accept `BeanContext` (Option B: change signature directly), and use RNG-aware factories for `genotype` and `phenotype` generation.
- Make `create_random_genotype` and `create_phenotype` optionally accept an RNG.
- Add deterministic factory helpers for direct genotype/phenotype creation: `create_genotype_from_values` and `create_phenotype_from_values`.
- Add deterministic unit tests and ensure tests use only public APIs: `World`, `World.step()`, `Bean.to_state()`, `Bean.update_from_state()`, `create_genotype_from_values`, `create_phenotype_from_values`, `genetic_max_age`, `genetic_max_speed`, `age_speed_factor`.

Phases & Steps (TDD & Branching)
--------------------------------
Phase 1 - Initial tests & plan file (fail-first)
- Create a new branch: `feat/deterministic-bean-context`.
- Add failing tests for `BeanContext` validation and placeholders for RNG-aware factories.
- Run the tests with `make test-specific` to validate failing state.
- Commit the failing tests.

Phase 2 - `BeanContext`, `WorldConfig.seed`, & private RNG
- Create `src/beans/context.py` with `BeanContext` (Pydantic model).
  - Fields: `bean_count: int`, `male_count: int`, `rng: Optional[random.Random] = None`.
  - Pydantic config: `arbitrary_types_allowed = True`.
  - Handle validation: `bean_count >= 0`, `0 <= male_count <= bean_count`.
- Update `src/config/loader.py`: `WorldConfig(seed: Optional[int] = None)`.
- Update `src/beans/world.py`: `self._rng = random.Random(config.seed) if config.seed is not None else None`.
- Update `_initialize()` to construct `BeanContext` and pass to `_create_beans`.
- Add tests for `WorldConfig.seed` placeholders (will pass once factories are RNG aware).
- Commit changes.

Phase 3 - RNG aware genetics factories & helpers
- Modify `src/beans/genetics.py`:
  - `create_random_genotype(rng: Optional[random.Random] = None)` — use `rng` when provided (calls to `rng.uniform`, `rng.choice`), otherwise fall back to module `random`.
  - `create_phenotype(config, genotype, rng: Optional[random.Random] = None)` — same pattern.
  - Provide helpers: `create_genotype_from_values(genes: dict[Gene, float])` and `create_phenotype_from_values(config, genotype, age, speed, energy, size, target_size)`.
- Add tests in `tests/test_genetics_rng.py`:
  - `test_create_random_genotype_reproducible_with_rng`
  - `test_create_phenotype_reproducible_with_rng`
  - `test_create_genotype_from_values_validation`
  - `test_create_phenotype_from_values_preserves_values`
- Run specific tests.
- Commit changes.

Phase 4 - Wire RNG into World._create_beans and add deterministic speed tests
- Update `src/beans/world.py`:
  - Replace `_create_beans(self, beans_config, bean_count, male_count)` signature to `_create_beans(self, beans_config, bean_context: BeanContext)`.
  - In `_initialize()`, pass `ctx = BeanContext(bean_count=..., male_count=..., rng=self._rng)`.
  - Use RNG-aware factories: `create_random_genotype(rng=ctx.rng)` and `create_phenotype(beans_config, genotype, rng=ctx.rng)`.
- Add new tests for speed computation (public API only) in `tests/test_bean_dynamics.py`:
  - `test_world_step_calculates_bean_speed_correctly`:
    - Build `WorldConfig(seed=42, width=..., height=..., population_density=...)`.
    - Use `BeansConfig` tuned to avoid energy side-effects.
    - Create `World`, assert 1 bean, prepare `BeanState` with `age=some`, `size=target_size`, `energy=high`, `speed=0.0`.
    - `world.step(dt=1.0)` and compute expected speed: `expected = max(bcfg.min_speed_factor, genetic_max_speed(bcfg, genotype) * age_speed_factor(age, genetic_max_age(bcfg, genotype), bcfg.min_speed_factor))`.
    - Assert `bean.speed == pytest.approx(expected)`.
  - `test_world_min_speed_floor`
  - `test_world_seed_repeatable_speed`.
- Run these tests, ensure they pass.
- Commit changes.

Phase 5 - Cleanup, docs, lint & PR
- Remove temporary wrappers if any.
- Add documentation in `summaries` and code docstrings.
- Run `make format`, `make lint`, `make test`.
- Prep PR for `feat/deterministic-bean-context` including test coverage and commit history.

Testing details & `make` commands
--------------------------------
- Run a single test file:
  `make test-specific TEST_SPECIFIC=tests/test_context_validation.py`
- Run a single test function:
  `make test-specific TEST_SPECIFIC=tests/test_bean_dynamics.py::test_world_step_calculates_bean_speed_correctly`
- Run the full suite:
  `make test` or `make test-cov`.

Public API restrictions
-----------------------
- All tests must use only public interfaces: `World`, `World.step`, `Bean.to_state`, `Bean.update_from_state`, `create_genotype_from_values`, `create_phenotype_from_values`, `create_random_genotype(rng=...)`, `create_phenotype(config, genotype, rng=...)`, `genetic_max_age`, `genetic_max_speed`, `age_speed_factor`.
- No direct access to private attributes like `Bean._max_age` or `World._rng`.

Acceptance criteria
-------------------
- Deterministic `World` creation using `WorldConfig.seed`.
- `create_random_genotype(rng=...)` and `create_phenotype(rng=...)` reproducible for same seed.
- `BeanContext` used by `World` and `_create_beans` accepts RNG.
- Tests confirm `World.step()` computes bean speeds deterministically and according to the expected formula.
- Lint and format checks pass, and tests are stable (no global `random.seed()` used).

Optional & Future enhancements
------------------------------
- Add `World.create_with_seed(seed=...)` helper or add `seed` production into `WorldConfig` JSON example.
- Add more deterministic scenarios (spawn positions) to `BeanContext` if needed.
- Consider a `World` factory function for testers (e.g., `World.create_test_world(seed=..., beans_config=...)`) while keeping public API minimal and consistent.


References & PR Checklist
------------------------
- Branch naming: `feat/deterministic-bean-context`.
- Commit strategy:
  - `test(...)`: failing tests first.
  - `feat(...)`: incremental feature implementation.
  - `refactor(...)`/`chore(...)` for refactors & docs.
- Run the main tests and coverage before PR.
- Create PR with a concise summary and test reproduction steps.



JS/Markdown: Done — the plan file is complete for step-by-step TDD implementation.
