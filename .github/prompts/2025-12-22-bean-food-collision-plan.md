## Plan: Bean-Food Collision Energy Transfer (TDD, Git, Environment, Step-by-Step, Correct Activation)

This plan details every step for a beginner, using TDD, correct git workflow, and correct environment activation for Windows (using `activate`), to implement beans eating food with minimal coupling.

---

### Phase 1: Setup and Branching

**Goal:** Prepare the environment and create a new branch for the feature.

#### Steps:
1. Open a terminal.
2. Activate the Python environment:
   - On Windows (cmd):  
     ```
     c:\dev\DevProjects\beans\beans\Scripts\activate
     ```
3. Check if you are on the `main` branch:  
   ```
   git branch
   ```
4. If on `main`, create and switch to a new branch:  
   ```
   git checkout -b feature/bean-food-collision-energy
   ```

---

### Phase 2: Write the First Failing Test (TDD)

**Goal:** Write a test that describes what should happen when a bean eats food.

#### Steps:
1. In the `tests/` folder, create a new test file (e.g., `test_food_intake.py`).
2. Write a test that:
   - Puts a bean and food at the same position.
   - Calls the method for bean-food collision.
   - Asserts the bean’s energy increases and the food’s energy decreases.
3. Run the test using the Makefile:  
   ```
   make test TEST=tests/test_food_intake.py
   ```
   - The test should fail (feature not implemented yet).

---

### Phase 3: Implement the Interface and Feature

**Goal:** Add the code to make the test pass, using minimal coupling.

#### Steps:
1. In `src/beans/environment/`, create `food_intake_service.py` with a `FoodIntakeService` interface.
2. Add a method `process_bean_food_collision(bean, position)` to the interface.
3. In `HybridFoodManager`, implement this method:
   - Calculate energy transfer based on bean and food properties.
   - Subtract energy from food at the position.
   - Return the energy gained.
4. In the collision system, call this method when a bean collides with food, and update the bean’s energy.

---

### Phase 4: Run Tests and Commit

**Goal:** Make sure the new feature works and save your progress.

#### Steps:
1. Run the specific test again:  
   ```
   make test TEST=tests/test_food_intake.py
   ```
2. If it passes, run all tests:  
   ```
   make test
   ```
3. If all tests pass, commit your changes:  
   ```
   git add .
   git commit -m "Implement bean-food collision energy transfer with decoupled interface"
   ```

---

### Phase 5: Food Removal on Decay

**Goal:** Ensure food is only removed during the decay step.

#### Steps:
1. In the food manager, only lower food energy when eaten.
2. In the decay step, remove food if its energy is zero or very small.
3. Write a test to check that food is only removed after decay, not immediately.
4. Run the test:  
   ```
   make test TEST=tests/test_food_intake.py
   ```
5. If it passes, run all tests:  
   ```
   make test
   ```
6. Commit if all tests pass:  
   ```
   git add .
   git commit -m "Ensure food removal only on decay step"
   ```

---

### Further Considerations

1. Always use absolute imports at the top of files.
2. Never use introspection, local imports, or unnecessary try/except blocks.
3. Ask for permission before moving to the next phase or committing.
