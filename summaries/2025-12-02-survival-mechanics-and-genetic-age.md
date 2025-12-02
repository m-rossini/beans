# Survival Mechanics and Genetic Age System

**Date**: 2025-12-02  
**Branch**: add-collision-detection

## Overview

Implemented a comprehensive survival system for beans with genetically-determined lifespans. The system ensures beans die when they reach their genetic maximum age or run out of energy.

## Key Design Decisions

### 1. Genetic Max Age Computed Once at Initialization

The `_max_age` is calculated once when a Bean is created and stored as an instance variable. This avoids redundant calculations during each `update()` or `survive()` call.

```python
self._max_age = genetic_max_age(config, genotype)
```

### 2. Logarithmic Age Gene Curve

The `MAX_GENETIC_AGE` gene uses a logarithmic transformation applied at genotype creation to favor longevity:

| Raw Gene Value | Transformed Value | Effect |
|----------------|-------------------|--------|
| 0.0 | 0.1 | Minimum 10% lifespan |
| 0.5 | ~0.73 | Favors longevity |
| 1.0 | 1.0 | Full lifespan |

The curve is: `min_fraction + (1 - min_fraction) * log(1 + k*x) / log(1 + k)`

### 3. Survival Responsibility in Bean Class

Survival logic moved from `World.step()` to `Bean` class:

- `can_survive_age()` - checks if age < genetic max age
- `survive()` - returns `(alive: bool, reason: str | None)`

### 4. max_age_rounds in BeansConfig

`max_age_rounds` is computed from world config (`max_age_years * rounds_per_year`) and stored in `BeansConfig`, simplifying function signatures throughout the codebase.

## Architecture

See [survival-mechanics-diagram.md](./2025-12-02-survival-mechanics-diagram.md)

## Files Modified

| File | Changes |
|------|---------|
| `src/config/loader.py` | Added `max_age_rounds` field to `BeansConfig` |
| `src/beans/genetics.py` | Added `apply_age_gene_curve()`, updated `create_random_genotype()` |
| `src/beans/bean.py` | Added `_max_age`, `can_survive_age()`, `survive()` |
| `src/beans/world.py` | Simplified `step()` to use `bean.survive()` |
| `tests/test_genetics.py` | New tests for age curve transformation |
| `tests/test_energy.py` | Added `TestBeanSurvival` class |

## Testing

```bash
python -m pytest tests/ -v
# 84 tests passed
```
