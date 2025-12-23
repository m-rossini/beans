## Plan: Modular Bean–Food Collision Handling (Detection in Movement, Logic in World/Subsystems)

**Goal:** Implement a modular system where the movement system detects all collisions (including bean–food and bean–dead-bean), reports them, and the world/subsystems apply the simulation logic (energy transfer, food decay, etc.), following strict TDD, environment, and git workflow.

---

### Phase 1: Environment & Branch Setup

1. Open a PowerShell terminal.
2. Activate the Python environment:
   ```
   c:\dev\DevProjects\beans\beans\Scripts\Activate.ps1
   ```
3. Check current git branch:
   ```
   git branch
   ```
4. If on `main`, create and switch to a new branch:
   ```
   git checkout -b feature/bean-food-collision-energy
   ```

---

### Phase 2: TDD – Write Failing Integration Test

1. In `tests/`, add or extend a test (e.g., `test_food_intake.py`) to:
   - Simulate a tick where a bean’s sprite overlaps a food/dead-bean grid cell.
   - Assert that after the tick, the bean’s energy increases and the food’s energy decreases.
   - Assert that food is only removed on decay, not immediately.
2. Run the test:
   ```
   make test TEST=tests/test_food_intake.py
   ```
3. Confirm the test fails for the correct (feature-missing) reason.

---

### Phase 3: Implement Collision Detection in Movement System

1. In `SpriteMovementSystem` (or equivalent), add logic to:
   - Detect when a sprite overlaps a food/dead-bean grid cell during movement.
   - Build a list of collision events: `[(bean_id, food_position), ...]`.
2. Do **not** apply energy or update model state here—just detect and report.
3. Run all tests to ensure no regressions:
   ```
   make test
   ```
4. Commit:
   ```
   git add .
   git commit -m "Detect bean-food/dead-bean collisions in movement system"
   ```

---

### Phase 4: Implement Business Logic in World/Subsystems

1. In the world or a dedicated subsystem, process the collision events reported by the movement system:
   - For each `(bean_id, food_position)`:
     - Call `food_manager.consume_energy_from_food(food_position)`.
     - Add the returned energy to the bean’s state.
2. Ensure the food manager only manages food state, not beans.
3. Run the specific test:
   ```
   make test TEST=tests/test_food_intake.py
   ```
4. If it passes, run all tests:
   ```
   make test
   ```
5. Commit:
   ```
   git add .
   git commit -m "Apply food energy to beans via world/subsystems on collision"
   ```

---

### Phase 5: Finalize, Refactor, and Document

1. Refactor for clarity, modularity, and minimal coupling.
2. Update documentation and diagrams if needed.
3. Run all tests:
   ```
   make test
   ```
4. Commit:
   ```
   git add .
   git commit -m "Refactor and document modular bean-food collision handling"
   ```

---

### Phase 6: Pull Request and Review

1. Push the branch:
   ```
   git push -u origin feature/bean-food-collision-energy
   ```
2. Create a pull request and request code review.

---

**Ready for your review or adjustments before proceeding.**
