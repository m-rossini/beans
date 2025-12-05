# Plan: Pluggable Energy System Implementation (TDD)

Each phase is a **separate branch** merged after completion. Each step within a phase is a **commit**.

---

## Phase 1: Configuration Constants
**Branch:** `feature/energy-system-config`

### Step 1.1: Write failing test for new config fields
- Test in `test_config.py` asserting: `fat_gain_rate`, `fat_burn_rate`, `metabolism_base_burn`, `energy_to_fat_ratio`, `fat_to_energy_ratio`, `energy_max_storage`, `size_sigma_frac`, `size_penalty_above_k`, `size_penalty_below_k`, `size_penalty_min_above`, `size_penalty_min_below`
- Run test → **fails**
- **Commit:** "test: add tests for energy system config fields"

### Step 1.2: Add config fields
- Add fields to `BeansConfig` with spec defaults
- Run test → **passes**
- **Commit:** "feat: add energy system configuration fields"

**Merge branch**

---

## Phase 2: World Environment Stubs
**Branch:** `feature/energy-system-world-stubs`

### Step 2.1: Write failing test for world energy intake
- Test: `get_energy_intake()` returns `DEFAULT_ENERGY_INTAKE` (1.0)
- Run test → **fails**
- **Commit:** "test: add test for world energy intake"

### Step 2.2: Implement world energy intake stub
- Add method to `World` returning hardcoded 1.0
- Run test → **passes**
- **Commit:** "feat: add world energy intake stub"

### Step 2.3: Write failing test for world temperature
- Test: `get_temperature()` returns `DEFAULT_TEMPERATURE` (1.0)
- Run test → **fails**
- **Commit:** "test: add test for world temperature"

### Step 2.4: Implement world temperature stub
- Add method to `World` returning hardcoded 1.0
- Run test → **passes**
- **Commit:** "feat: add world temperature stub"

**Merge branch**

---

## Phase 3: EnergySystem Class with Intake
**Branch:** `feature/energy-system-intake`

### Step 3.1: Write failing test for EnergySystem creation
- Create `tests/test_energy_system.py`
- Test: `EnergySystem` can be instantiated with config
- Run test → **fails**
- **Commit:** "test: add test for EnergySystem instantiation"

### Step 3.2: Create EnergySystem skeleton
- Create `src/beans/energy_system.py` with constructor
- Run test → **passes**
- **Commit:** "feat: add EnergySystem class skeleton"

### Step 3.3: Write failing test for apply_intake
- Test: `apply_intake(bean, 10.0)` increases `bean.energy` by 10.0
- Run test → **fails**
- **Commit:** "test: add test for apply_intake"

### Step 3.4: Implement apply_intake
- Add `apply_intake()` method
- Run test → **passes**
- **Commit:** "feat: implement apply_intake method"

**Merge branch**

---

## Phase 4: Basal Metabolism
**Branch:** `feature/energy-system-basal-metabolism`

### Step 4.1: Write failing test for basal metabolism burn
- Test: `update_energy()` decreases energy proportional to size
- Test: larger size burns more energy
- Run test → **fails**
- **Commit:** "test: add tests for basal metabolism burn"

### Step 4.2: Implement basal metabolism burn
- Add metabolism burn: `burn = metabolism_base_burn * (1 + 0.5 * METABOLISM_SPEED) * size`
- Run test → **passes**
- **Commit:** "feat: implement basal metabolism burn"

### Step 4.3: Write failing test for metabolism gene effect
- Test: higher `METABOLISM_SPEED` gene increases burn rate
- Run test → **fails**
- **Commit:** "test: add test for metabolism gene effect"

### Step 4.4: Verify metabolism gene implementation
- Run test → **passes** (already implemented in 4.2)
- **Commit:** "test: verify metabolism gene effect"

**Merge branch**

---

## Phase 5: Movement Cost
**Branch:** `feature/energy-system-movement-cost`

### Step 5.1: Write failing test for movement cost
- Test: `update_energy()` deducts `abs(speed) * movement_cost_per_speed` from energy
- Test: uses current speed value at calculation moment
- Run test → **fails**
- **Commit:** "test: add tests for movement cost"

### Step 5.2: Implement movement cost
- Add movement cost calculation using current phenotype speed
- Run test → **passes**
- **Commit:** "feat: implement movement cost calculation"

**Merge branch**

---

## Phase 6: Fat Storage and Burning (Atomic)
**Branch:** `feature/energy-system-fat-mechanics`

### Step 6.1: Write failing test for fat storage from surplus
- Test: when `energy > energy_baseline`, size increases
- Test: energy decreases by `fat_gain * energy_to_fat_ratio`
- Test: higher `FAT_ACCUMULATION` gene increases fat gain rate
- Run test → **fails**
- **Commit:** "test: add tests for fat storage from surplus"

### Step 6.2: Implement fat storage
- Add surplus → fat conversion: `fat_gain = fat_gain_rate * FAT_ACCUMULATION * surplus`
- Run test → **passes**
- **Commit:** "feat: implement fat storage from surplus energy"

### Step 6.3: Write failing test for fat burning from deficit
- Test: when `energy < energy_baseline`, size decreases and energy increases
- Test: uses `fat_to_energy_ratio` for conversion
- Test: higher `FAT_ACCUMULATION` gene decreases fat burn rate
- Run test → **fails**
- **Commit:** "test: add tests for fat burning from deficit"

### Step 6.4: Implement fat burning
- Add deficit → fat burn: `fat_burn = fat_burn_rate * (1.2 - FAT_ACCUMULATION) * deficit`
- Run test → **passes**
- **Commit:** "feat: implement fat burning from energy deficit"

### Step 6.5: Write failing test for atomic fat mechanics
- Test: storage happens first, then burning, in single `update_energy()` call
- Test: intermediate states not observable externally
- Run test → **fails**
- **Commit:** "test: add test for atomic fat storage then burning"

### Step 6.6: Verify atomic behavior
- Ensure both operations in sequence within `update_energy()`
- Run test → **passes**
- **Commit:** "feat: verify atomic fat storage and burning sequence"

**Merge branch**

---

## Phase 7: Energy Overflow to Fat Burn
**Branch:** `feature/energy-system-negative-energy-handling`

### Step 7.1: Write failing test for negative energy overflow
- Test: if energy goes negative after costs, fat is burned to compensate
- Test: `size` decreases, `energy` becomes 0
- Run test → **fails**
- **Commit:** "test: add tests for negative energy overflow to fat"

### Step 7.2: Implement negative energy overflow
- If `energy < 0`: burn fat = `abs(energy) / fat_to_energy_ratio`, reduce size, set energy to 0
- Run test → **passes**
- **Commit:** "feat: implement negative energy overflow to fat burn"

**Merge branch**

---

## Phase 8: Size Clamping
**Branch:** `feature/energy-system-size-clamping`

### Step 8.1: Write failing test for size clamping
- Test: size cannot go below `min_bean_size`
- Test: size cannot exceed `max_bean_size`
- Run test → **fails**
- **Commit:** "test: add tests for size clamping"

### Step 8.2: Implement size clamping with TODO
- Add clamp after all size changes
- Add `# TODO: Extract size changes and clamping to separate sizing subsystem`
- Run test → **passes**
- **Commit:** "feat: implement size clamping with sizing subsystem TODO"

**Merge branch**

---

## Phase 9: Size Speed Penalty
**Branch:** `feature/energy-system-size-speed-penalty`

### Step 9.1: Write failing test for penalty within normal range
- Test: `size_speed_penalty()` returns 1.0 when size within ±2σ of target
- Run test → **fails**
- **Commit:** "test: add test for normal range speed penalty"

### Step 9.2: Write failing test for overweight penalty
- Test: penalty < 1.0 when `size > target + 2σ`
- Test: penalty respects `size_penalty_min_above`
- Run test → **fails**
- **Commit:** "test: add test for overweight speed penalty"

### Step 9.3: Write failing test for underweight penalty
- Test: penalty < 1.0 when `size < target - 2σ`
- Test: penalty respects `size_penalty_min_below`
- Run test → **fails**
- **Commit:** "test: add test for underweight speed penalty"

### Step 9.4: Implement size_speed_penalty
- Add z-score calculation and penalty logic
- Add `# TODO: Extract size speed penalty to sizing subsystem`
- Run test → **passes**
- **Commit:** "feat: implement size speed penalty with sizing subsystem TODO"

**Merge branch**

---

## Phase 10: Survival Methods
**Branch:** `feature/energy-system-survival`

### Step 10.1: Write failing test for updated can_survive_energy
- Test: returns `False` when `size <= min_bean_size` (starvation)
- Test: returns `True` otherwise
- Test: compatible with existing `survive()` call
- Run test → **fails**
- **Commit:** "test: add tests for updated can_survive_energy"

### Step 10.2: Update can_survive_energy implementation
- Delegate to `EnergySystem` for size-based starvation check
- Maintain compatibility with existing `survive()` method
- Run test → **passes**
- **Commit:** "feat: update can_survive_energy for starvation"

### Step 10.3: Write failing test for can_survive_health (obesity)
- Test: returns `False` with probability when `size > target_size * 2.5`
- Test: returns `True` when size is healthy
- Run test → **fails**
- **Commit:** "test: add tests for can_survive_health"

### Step 10.4: Implement can_survive_health
- Add `can_survive_health()` to `Bean` delegating to `EnergySystem`
- Run test → **passes**
- **Commit:** "feat: implement can_survive_health method"

### Step 10.5: Write failing test for survive() integration
- Test: `survive()` calls `can_survive_age()`, `can_survive_energy()`, and `can_survive_health()`
- Run test → **fails**
- **Commit:** "test: add test for survive integration with can_survive_health"

### Step 10.6: Update survive() to include health check
- Add `can_survive_health()` call to existing `survive()` method
- Run test → **passes**
- **Commit:** "feat: integrate can_survive_health into survive method"

**Merge branch**

---

## Phase 11: Bean Integration
**Branch:** `feature/energy-system-bean-integration`

### Step 11.1: Write failing test for Bean using EnergySystem
- Test: `Bean.update()` uses `EnergySystem` for energy calculations
- Test: existing energy behavior preserved
- Run test → **fails**
- **Commit:** "test: add tests for Bean EnergySystem integration"

### Step 11.2: Inject EnergySystem into Bean
- Update `Bean` constructor and `update()` to delegate
- Run test → **passes**
- **Commit:** "feat: integrate EnergySystem into Bean"

**Merge branch**

---

## Phase 12: Update Order Refactoring
**Branch:** `feature/energy-system-update-order`

### Step 12.1: Write failing test for canonical update order
- Test: order is `update_age()` → `update_speed()` → `update_energy()` → `decide_actions()`
- Run test → **fails**
- **Commit:** "test: add test for canonical update order"

### Step 12.2: Refactor update method order
- Reorder method calls in `Bean.update()`
- Run test → **passes**
- **Commit:** "feat: refactor Bean.update to canonical order"

**Merge branch**

---

## Phase 13: Documentation
**Branch:** `feature/energy-system-documentation`

### Step 13.1: Create summary ADR
- Write `summaries/2025-12-XX-pluggable-energy-system.md`
- **Commit:** "docs: add energy system ADR summary"

### Step 13.2: Create mermaid diagram
- Create flow diagram linked from summary
- **Commit:** "docs: add energy system mermaid diagram"

**Merge branch**

---

## Open Questions

1. **World stubs location:** Placed in `World` class. Is this correct, or should they be in a separate `Environment` class?

2. **Existing tests:** Some tests in `test_bean_energy.py` test current energy behavior. Should they be updated during Phase 11 (Bean Integration) or kept as-is to verify backward compatibility?

3. **Death reason strings:** Current reasons are `"max_age_reached"` and `"energy_depleted"`. For the new starvation and obesity deaths, what strings should be used? Suggestions: `"starvation"` and `"obesity"` or `"size_depleted"` and `"size_exceeded"`?
