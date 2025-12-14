# Survival System — TDD-first Plan

This document captures the TDD-first, phased plan for adding a starvation-aware, configurable, and extensible SurvivalChecker to the simulation. Tests will be integration-only and must exercise behavior through `world.step()`.

## TL;DR
- Implement `SurvivalChecker` + `DefaultSurvivalChecker`.
- Rules: age death, energy→starvation (negative energy draws from fat, fat depletes faster while starving), optional obesity fatality using RNG.
- Tests must be integration tests that use `world.step()` and assert `world.dead_beans` and bean state.
- Workflow is phased and TDD-first; after each phase I will ask you to commit/approve before moving on.

---

## Phases & Steps

### Pre Phase — Preparations
- Ensure local environment is set up and tests run with `make test`.

### Phase 0 — Branch & Test Setup (in-progress)
- Create feature branch `feat/survival-checks`.
- Confirm `make test` works locally.
- Add placeholder integration test file `tests/test_survival_integration.py`.
- Prepare small test fixtures/helpers for deterministic bean/world creation (will use existing factories like `create_phenotype_from_values`, `create_genotype_from_values`).

### Phase 1 — Add failing integration tests
- Add integration tests (only call `world.step()` for assertions):
  - `test_starvation_depletes_fat_and_survives_until_min_size` — energy ≤ 0: after a step, size decreases by `starvation_fat_depletion_rate * starvation_multiplier` and bean survives if `size > min_bean_size`.
  - `test_death_when_fat_depleted_and_energy_zero` — energy ≤ 0 and size <= min -> bean dies and `reason == "STARVATION"`.
  - `test_age_death` — set `age >= genetic_max_age` and expect `reason == "MAX_AGE"`.
  - `test_obesity_probabilistic_death_seeded` — enable obesity death in config, seed world RNG, assert deterministic death/no-death after `world.step()`.
  - `test_external_event_hook_noop` — ensure hook exists and does not cause deaths unexpectedly when `world.step()` runs.
- Run tests and confirm all added tests fail.

### Phase 2 — Implement survival system core
- Add `src/beans/survival.py` with:
  - `SurvivalResult` dataclass: `alive: bool`, `reason: Optional[str]`, `message: Optional[str]`.
  - `SurvivalReason` enum: `MAX_AGE`, `STARVATION`, `OBESITY`, `EXTERNAL_EVENT`, etc.
  - `SurvivalChecker` ABC with `check(bean, phenotype, genotype, world) -> SurvivalResult` and `handle_event(bean, event)` (no-op default).
  - `DefaultSurvivalChecker` implementing rules and taking `BeansConfig` and `rng`.
- Starvation behavior: if `energy <= 0` then set `phenotype.energy = 0` and reduce `phenotype.size` by `starvation_fat_depletion_rate * starvation_multiplier`; if `size <= config.min_bean_size`, die with `STARVATION`, else survive.
- Age check takes priority over starvation.
- Obesity death behind `enable_obesity_death` and uses injected RNG for determinism.
- Add the external-event no-op hook.
- Iterate until integration tests from Phase 1 pass.

### Phase 3 — Wire into simulation & integration tests
- Add new config fields to `BeansConfig`:
  - `starvation_fat_depletion_rate: float` (default 0.05)
  - `starvation_multiplier_when_energy_zero: float` (default 2.0)
  - `enable_obesity_death: bool` (default False)
  - `obesity_death_probability: float` (default 0.0)
  - `obesity_threshold_size: float` (sensible default)
- Instantiate and inject `DefaultSurvivalChecker` in `World` or `Population` and pass the world's RNG.
- Update `world.step()` to call `checker.check(...)` after bean updates; if `alive == False` then call `bean.kill()`, remove from population, and append `(bean, reason)` to `world.dead_beans`.
- Run and fix integration tests.

### Phase 4 — Cleanup, docs & final tests
- Migrate/remove old helper functions (implement or remove `can_survive_size` in `src/beans/genetics.py`).
- Add summary doc in `summaries/YYYY-MM-DD-survival-system.md` and a mermaid diagram.
- Run full test suite and coverage, fix regressions.
- Prepare PR and request code review.

---

## Config Defaults (proposed)
- `starvation_fat_depletion_rate = 0.05`
- `starvation_multiplier_when_energy_zero = 2.0`
- `enable_obesity_death = False`

I can adjust these if you prefer alternatives.

## Decisions & Questions
- Energy handling while starving: recommended to set `phenotype.energy = 0` per starvation tick and model the deficit by reducing `size` (fat). Confirm if you prefer preserving negative energy instead.
- Obesity death: keep behind a config switch (off by default) or postpone to future phase? Recommended: behind switch.

---

## Testing rules (enforced)
- All tests are integration-style and must make assertions by calling `world.step()` only.
- TDD workflow: write failing tests first, implement minimal code to pass, then refactor.
- After each phase completes and tests pass, I will ask you to commit/approve to continue.

---

If this file looks good, I’ll start Phase 0 (branch + placeholder tests). Reply with confirmation to proceed or with adjustments to config defaults/energy handling preferences.
