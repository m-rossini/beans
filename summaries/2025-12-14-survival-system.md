# 2025-12-14 - Survival System (Design Summary) ✅

## Overview
This short ADR-style summary describes the survival-check system implemented to run at the end of each `World.step()`.

Goals:
- Provide an extensible, configurable survival-check system that decides bean survival **only** at the integration point (after per-bean updates in `World.step()`).
- Implement base rules (age and starvation) and add configuration-driven behaviors (starvation depletion rate and probabilistic obesity death).
- Maintain compatibility with existing semantics and canonical death reasons already used by tests (e.g., `"energy_depleted"`, `"max_age_reached"`).

## Key design decisions
- Centralized survival logic in `src/beans/survival.py` via:
  - `SurvivalResult` dataclass
  - `SurvivalChecker` interface
  - `DefaultSurvivalChecker` default implementation
- Survival checks are invoked from `World.step()` after energy and dynamics updates; `World` records deaths in `dead_beans: List[DeadBeanRecord]`.
- Use injectable RNG (world-private RNG) for deterministic probabilistic behavior in tests.
- Config fields were added to `BeansConfig` so behavior is tunable via the config loader.

## Configuration fields added
- `starvation_base_depletion: float` — base size units consumed per starvation tick
- `starvation_depletion_multiplier: float` — multiplier applied when energy <= 0
- `enable_obesity_death: bool` — toggle probabilistic obesity death
- `obesity_death_probability: float` — probability (0.0-1.0) of death when above obesity threshold
- `obesity_threshold_factor: float` — threshold multiplier of `max_bean_size` to be considered obese

These values are validated when loading config and have sensible defaults.

## Behavior summary
- Age death: if `bean.can_survive_age()` is False, bean dies with reason `"max_age_reached"`.
- Starvation: when `bean.energy <= 0`:
  - If `bean.size <= min_bean_size` → die with reason `"energy_depleted"`.
  - Otherwise, draw on fat: reduce `bean.size` by `starvation_base_depletion * starvation_depletion_multiplier` (clamped at `min_bean_size`) and set `bean.energy = 0.0`.
- Obesity death (optional): if enabled and `bean.size >= obesity_threshold_factor * max_bean_size`, roll RNG and possibly mark death with reason `"obesity"`.

## Tests & TDD notes
- Integration tests live in `tests/test_survival_integration.py`. They only interact with the simulation via `world.step()` to ensure the integration contract is respected.
- Added tests for:
  - Starvation-depletes-and-survives-until-min-size
  - Death when fat depleted and energy zero
  - Age death
  - Probabilistic obesity death (seeded/deterministic in tests)
  - Starvation depletion rate honored (config-driven)
  - External-event hook no-op

## Diagrams
Mermaid diagram of the survival decision flow:

```mermaid
flowchart TD
    A[World.step() per-bean updates] --> B[SurvivalChecker.check(bean, world)]
    B --> |age exceeded| C[Dead: max_age_reached]
    B --> |energy <= 0| D{size <= min_bean_size}
    D --> |true| E[Dead: energy_depleted]
    D --> |false| F[Consume fat: size -= depletion]
    F --> G[Alive]
    B --> |obesity enabled & above threshold + RNG hit| H[Dead: obesity]
    B --> |none matched| G

```

## How to run tests (local dev)

Run the full test suite (same commands used during development):

```bash
# Windows (cmd.exe)
set PYTHONPATH=src && set LOGGING_LEVEL= && python -m pytest -v -s
```

Or run the new specific integration tests:

```bash
set PYTHONPATH=src && python -m pytest -v -s tests/test_survival_integration.py
```

## Follow-ups / TODOs
- Consider moving death bookkeeping into a SurvivalManager or the SurvivalChecker (implementation notes present in code TODOs).
- Expand SurvivalChecker interface for external-event handling (we have a no-op hook now).
- Add documentation in README and a short snippet showing how to tune survival behavior via config file.

---

*File generated and committed as part of the survival-checks work (Phase 4).*