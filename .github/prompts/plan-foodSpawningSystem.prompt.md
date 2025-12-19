# Food Spawning System Implementation Plan (Detailed, with Git Workflow)

## Overview
Implement a flexible, config-driven food spawning system for the simulation, supporting:
- Configurable food quantity, quality, max energy, spawn frequency, spawn distribution, and decay rate.
- No food spawning on occupied positions.
- Strict TDD and git process, with explicit commands and user OK at each phase.
- No introspection, no local imports, fail fast, no unnecessary code comments.

## General Process & Git Workflow
- If on `main`, create a new feature branch:  
  `git checkout -b feature/food-spawning-system`
- Each phase is implemented in sequence, following TDD:
  - Write failing test(s)
  - Implement code to pass test(s)
  - Run only new/changed tests:  
    `make test TESTS=tests/path/to/test_file.py`
  - If all pass, run all tests:  
    `make test`
  - After all tests pass, commit changes:  
    `git add .`  
    `git commit -m "<concise business-focused message>"`
  - At the end of each phase, request explicit user OK before proceeding.
- After all phases, push branch and create a pull request:  
  `git push origin feature/food-spawning-system`

## Phases & Steps

### Phase 0: Setup & Initial Commit
1. Ensure you are on `main` branch:
    `git checkout main`
2. Create a new feature branch:  
    `git checkout -b feature/food-spawning-system`
3. Initial commit to set up branch:  
    `git commit --allow-empty -m "Start food spawning system feature branch"`
4. Ensure you are in the correct python environment, with command bean/Scripts/activate 
    or `source bean/bin/activate` as appropriate note that even in wiondows you ar erunning powershell therefore the activate.bat does NOT WORK. stick to activate
### Phase 1: Config & Interface Preparation
1. Add/extend config for food spawning parameters (quantity, quality, max energy, frequency, distribution, decay).
2. Update or create interface in FoodManager/HybridFoodManager for spawning logic.
3. Add/adjust tests for config and interface.
4. Run only new/changed tests:  
   `make test TESTS=tests/path/to/test_file.py`
5. Run all tests:  
   `make test`
6. Commit:  
   `git add .`  
   `git commit -m "Add config and interface for food spawning"`
7. **User OK required to proceed to next phase.**

### Phase 2: Initial Food Spawning Logic
1. Implement initial food spawning at simulation start, using config parameters.
2. Ensure no food spawns on occupied positions.
3. Add/adjust tests for initial spawning logic.
4. Run only new/changed tests:  
   `make test TESTS=tests/path/to/test_file.py`
5. Run all tests:  
   `make test`
6. Commit:  
   `git add .`  
   `git commit -m "Implement initial food spawning logic"`
7. **User OK required to proceed to next phase.**

### Phase 3: Ongoing Food Spawning (Per Step)
1. Implement ongoing food spawning at configured frequency (e.g., every N steps).
2. Support spawn distribution (random, uniform, etc.) as per config.
3. Add/adjust tests for ongoing spawning and distribution.
4. Run only new/changed tests:  
   `make test TESTS=tests/path/to/test_file.py`
5. Run all tests:  
   `make test`
6. Commit:  
   `git add .`  
   `git commit -m "Implement ongoing food spawning logic"`
7. **User OK required to proceed to next phase.**

### Phase 4: Food Decay & Max Energy Cap
1. Implement food decay and enforce max energy per food item.
2. Add/adjust tests for decay and max energy logic.
3. Run only new/changed tests:  
   `make test TESTS=tests/path/to/test_file.py`
4. Run all tests:  
   `make test`
5. Commit:  
   `git add .`  
   `git commit -m "Implement food decay and max energy cap"`
6. **User OK required to proceed to next phase.**

### Phase 5: Integration & Refactoring
1. Integrate new logic with rendering and simulation loop.
2. Refactor for clarity, modularity, and testability (no introspection/local imports).
3. Add/adjust integration tests as needed.
4. Run only new/changed tests:  
   `make test TESTS=tests/path/to/test_file.py`
5. Run all tests:  
   `make test`
6. Commit:  
   `git add .`  
   `git commit -m "Integrate and refactor food spawning system"`
7. **User OK required to proceed to next phase.**

### Phase 6: Documentation & Summary
1. Write summary and ADR in `summaries/` (overview, design, challenges, instructions).
2. Create/update mermaid diagram if needed.
3. Commit:  
   `git add .`  
   `git commit -m "Document food spawning system implementation"`
4. Push branch and create pull request:  
   `git push origin feature/food-spawning-system`
5. Request code review.

## Process Rules
- TDD: Write failing test, implement, ensure test passes, repeat.
- Use Makefile for all test/coverage commands.
- No introspection, no local imports, fail fast.
- No unnecessary code comments.
- User OK required at each phase transition.
- Each commit message should be concise and business-focused.
- After all phases, create a pull request and request code review.
