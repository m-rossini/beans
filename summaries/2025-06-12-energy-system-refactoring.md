# Energy System Refactoring

## Overview

Refactored the energy system in `Bean` to use private helper methods and integrate age-based energy efficiency with metabolism gene influence. This follows the same pattern established for age survival mechanics.

## Key Design Decisions

### Energy Cost Formula

```
energy_cost = base_cost × metabolism_factor / age_efficiency
```

Where:
- `base_cost = |speed| × energy_cost_per_speed`
- `metabolism_factor = 0.5 + METABOLISM_SPEED_gene` (range: 0.5 to 1.5)
- `age_efficiency = age_energy_efficiency(age, max_age, min_energy_efficiency)` (range: 0.3 to 1.0)

### Metabolism Gene Impact

Higher metabolism = higher energy cost:
- Gene value 0.0 → 0.5× base cost multiplier
- Gene value 0.5 → 1.0× base cost multiplier  
- Gene value 1.0 → 1.5× base cost multiplier

### Age-Based Efficiency

Similar curve to `age_speed_factor()`:
- Newborns: Low efficiency (floor at `min_energy_efficiency = 0.3`)
- Mature beans: Peak efficiency (1.0)
- Old beans: Declining efficiency (floor at 0.3)

Low efficiency means **higher energy cost** (division by efficiency).

### Configuration

Added `min_energy_efficiency` parameter to `BeansConfig`:
- Default value: 0.3
- Prevents division by zero at age 0
- Models real-world biological inefficiency at birth and old age

## Implementation Details

### New Methods in `Bean`

| Method | Visibility | Description |
|--------|------------|-------------|
| `_calculate_energy_gain()` | Private | Returns `config.energy_gain_per_step` |
| `_calculate_energy_cost()` | Private | Calculates cost using speed, metabolism, and age efficiency |
| `can_survive_energy()` | Public | Returns `self.energy > 0` |

### New Function in `genetics.py`

| Function | Description |
|----------|-------------|
| `age_energy_efficiency(age, max_age, min_efficiency)` | Returns efficiency factor [min_efficiency, 1.0] |

### Modified Methods

- `Bean._update_energy()`: Now calls private helper methods
- `Bean.survive()`: Now calls `can_survive_energy()` in survival check

## Diagram

See [energy-system-refactoring-diagram.md](./2025-06-12-energy-system-refactoring-diagram.md)

## Testing

21 energy-related tests covering:
- Energy gain calculation
- Energy cost with metabolism influence
- Age efficiency curve (newborn, mature, old)
- `can_survive_energy()` boundary cases
- Integration with survival mechanics

All 94 tests passing.

## Files Changed

- `src/config/loader.py` - Added `min_energy_efficiency` parameter
- `src/config/small.json`, `medium.json`, `large.json` - Added parameter
- `src/beans/genetics.py` - Added `age_energy_efficiency()`, removed stub
- `src/beans/bean.py` - Added private methods and `can_survive_energy()`
- `tests/test_energy.py` - Added comprehensive tests
