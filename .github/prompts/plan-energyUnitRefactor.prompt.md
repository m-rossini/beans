# Energy Tests Refactor Plan (energyUnitRefactor)

Goal: Convert fragile tests in `tests/test_energy_system.py` to deterministic, behavior-focused unit tests that assert on the returned `BeanState` from `EnergySystem.apply_energy_system()` and verify purity (the function should not mutate the original `Bean`). Keep each change small and follow TDD; ask for permission before each git action.

---

## Branching & git workflow (one small commit per step)
0. Ensure you are in the beans environment

1. Branch: `tests/refactor/energy-unit` (local)
   - Purpose: isolate this refactor.
   - Git command (Windows cmd.exe):
     - git checkout -b tests/refactor/energy-unit
   - Permission checkpoint: ask before creating the branch.

2. Add unit purity test
   - File: `tests/test_energy_system.py`
   - New test: `test_apply_energy_returns_state_and_does_not_mutate_bean`
     - Call `state = energy_system.apply_energy_system(bean, energy_intake_eu=X)` and assert:
       - `state.energy` changed relative to input
       - `bean.energy` remains unchanged
   - Goal: establish expected failing test (if current tests relied on mutation), then make test pass by editing tests only.
   - Permission checkpoint: ask before editing the test file.

3. Convert the other energy tests to assert on returned `BeanState` (unit-focused)
   - Tests to update:
     - `test_intake_increases_energy` → assert `state.energy > original_energy` and `bean.energy == original_energy`.
     - `test_metabolism_reduces_energy_over_time` → iterate calls to `apply_energy_system()` and assert monotonic decrease in returned states (`state.energy` sequence non-increasing), or assert `state.energy < initial` after several iterations.
     - `test_size_increases_when_energy_above_baseline` / `test_size_decreases_when_energy_below_baseline` → assert `state.size >= bean.size` or `<=` respectively; also assert the original bean unchanged.
     - `test_size_clamping` → assert returned `state.size` within `[min_bean_size, max_bean_size]` and original bean unchanged.
   - Keep survival tests behavior-focused; minimal edits to avoid implementation coupling.
   - Permission checkpoint: ask before making these edits.

4. Run tests & linters (TDD loop)
   - Single test: set TEST_SPECIFIC and use `make test-specific`.
   - Run file-specific: `set TEST_SPECIFIC=tests/test_energy_system.py && make test-specific`.
   - Full suite: `make test`.
   - Linting: `make ruff` and `make lint`.
   - Fix any style or failing tests.
   - Permission checkpoint: ask before running the tests.

5. Commit changes
   - Commands:
     - git add tests/test_energy_system.py
     - git commit -m "tests(energy): assert apply_energy_system returns BeanState and does not mutate bean"
   - Permission checkpoint: ask before committing.

6. Push branch & open PR
   - Command: git push -u origin tests/refactor/energy-unit
   - Open PR with rationale: "Convert energy tests to unit-focused, behavior-oriented tests; assert on return values and purity to reduce flakiness." Include references to TDD steps and test rationale.
   - Permission checkpoint: ask before pushing/opening PR.

7. Post-merge: create summary doc and proceed to next refactor phase
   - Add a short summary in `summaries/` describing the change, test decisions, and any follow-ups (e.g., future helper additions).
   - Permission checkpoint: ask before creating/committing summaries.

---

## Exact test edits (concrete)

- Add: `test_apply_energy_returns_state_and_does_not_mutate_bean` (verifies returned state energy change and bean unchanged).

- Modify `test_intake_increases_energy`:
  - Replace assertion on `bean` after `bean.update_from_state(state)` with assertions on `state.energy` and `bean.energy` unchanged.

- Modify `test_metabolism_reduces_energy_over_time`:
  - Prefer checking returned `state.energy` over time by calling `apply_energy_system()` repeatedly and verifying monotonic decrease in returned `state.energy` values.

- Modify `test_size_increases_when_energy_above_baseline` and `test_size_decreases_when_energy_below_baseline`:
  - Assert `state.size >= initial_size` or `state.size <= initial_size` respectively; assert bean unchanged.

- Modify `test_size_clamping`:
  - Call `apply_energy_system()` and assert `state.size` is clamped to `config.min_bean_size` or `config.max_bean_size`; assert bean unchanged.

- Leave `test_survival_health_and_starvation` as a behavior test, possibly with minor edits to avoid internal coupling.

---

## Safety & risks

- Risk: tests may reveal expectations that depend on mutation; mitigate by keeping tests small and adding explicit comments. If production API clarifications are needed (e.g., public helper to set bean state for integration tests), open a small follow-up PR.

- Keep each commit focused and run full test suite before pushing.

---

## Permission checkpoints

I will ask explicit permission before:
- Creating the branch.
- Editing `tests/test_energy_system.py`.
- Running tests locally.
- Committing changes.
- Pushing the branch and opening a PR.

---

If you approve I will start with: "May I create branch `tests/refactor/energy-unit` locally now?" and pause for your confirmation before proceeding.
