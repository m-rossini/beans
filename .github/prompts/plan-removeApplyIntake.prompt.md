## Plan: Remove `apply_intake` from Energy System (Intern-Level, With Commits)

This plan details every phase and step to safely remove the `_apply_intake` method, update code and tests, and ensure all work is committed at the end of each phase.

---

### Phase 1: Environment Setup & Branching

1. Open PowerShell.
2. `cd C:\dev\DevProjects\beans`
3. `./beans/Scripts/Activate`
4. `git status` (ensure on `main`)
5. `git checkout main`
6. `git pull`
7. `git checkout -b remove-apply-intake-energy-system`
8. **Commit:**  
   - `git add .`  
   - `git commit -m "Setup branch for removing apply_intake"`

---

### Phase 2: Remove `_apply_intake` from Codebase

#### Step 2.1: Remove from Abstract Base Class
- Delete `_apply_intake` from `EnergySystem` in `src/beans/energy_system.py`.

#### Step 2.2: Remove from Standard Implementation
- Delete `_apply_intake` from `StandardEnergySystem`.

#### Step 2.3: Refactor Usage in `apply_energy_system`
- Remove the call to `_apply_intake` and adjust logic/signature.

#### Step 2.4: Search and Refactor All Usages
- Search for `_apply_intake`/`apply_intake` in the codebase and remove/refactor all usages.

#### Step 2.5: Update Documentation
- Remove or update docstrings/comments referencing `_apply_intake`.

**Commit:**  
- `git add .`  
- `git commit -m "Remove apply_intake from energy system classes and all usages"`

---

### Phase 3: Update and Refactor Tests

#### Step 3.1: Identify Affected Tests
- Search `tests/` for any test referencing `apply_intake`.

#### Step 3.2: Update Expected Values
- Update expected values in tests to match new logic (do not change structure).

#### Step 3.3: Refactor or Remove Direct Calls
- Refactor/remove tests that directly call `apply_intake`.

#### Step 3.4: Run Specific Tests
- `make test TESTS=tests/test_energy_system.py` (or relevant file)

#### Step 3.5: Run All Tests
- `make test`

**Commit:**  
- `git add .`  
- `git commit -m "Update tests for removal of apply_intake"`

---

### Phase 4: Linting and Code Quality

1. `make lint`
2. Fix any linting errors.

**Commit:**  
- `git add .`  
- `git commit -m "Lint and style fixes after apply_intake removal"`

---

### Phase 5: Post-Work and Pull Request

1. Create/update summary ADR in `summaries/`.
2. (Optional) Add/update mermaid diagram.
3. `git add .`
4. `git commit -m "Document removal of apply_intake in ADR"`
5. `git push --set-upstream origin remove-apply-intake-energy-system`
6. Open a pull request and request review.

---

### Further Considerations

- Confirm with the team if any legacy code still needs direct energy intake.
- Ask for clarification if any ambiguity arises.
