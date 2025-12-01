# Phenotype Implementation

**Date:** 2025-12-01  
**Branch:** add-collision-detection

## Overview

Introduced a `Phenotype` dataclass to represent mutable bean traits that change during simulation. This separates the genetic blueprint (Genotype - immutable) from the expressed characteristics (Phenotype - mutable) that evolve over time.

## Key Design Decisions

### 1. Phenotype as Dataclass (not Pydantic)
- **Rationale:** Phenotype changes every tick, so lightweight dataclass is more performant than Pydantic
- **Serialization:** Uses `dataclasses.asdict()` via `to_dict()` method for future state persistence

### 2. Read-Only Properties on Bean
- Phenotype values are exposed via read-only `@property` decorators (no setters)
- **Rationale:** Phenotype can only change through bean's internal update cycle, not external assignment
- This enforces encapsulation: external code reads `bean.energy`, but only `bean.update()` modifies it

### 3. Mandatory Phenotype Parameter
- Bean requires phenotype to be passed at construction (no default creation)
- World is responsible for creating phenotype via `create_phenotype()` factory

### 4. Speed Derived from Genotype
- Initial speed is calculated from `MAX_GENETIC_SPEED` gene: `speed = random.uniform(-max, max)` where `max = config.speed_max * gene_value`
- Removed `speed` parameter from Bean constructor

## Components

| Component | Description |
|-----------|-------------|
| `Phenotype` | Dataclass with `age`, `speed`, `energy`, `size` fields |
| `create_phenotype()` | Factory function deriving initial phenotype from config + genotype |
| `can_survive_energy()` | Placeholder for energy survival bounds (TODO) |
| `can_survive_size()` | Placeholder for size survival bounds (TODO) |

## Phenotype Fields

| Field | Initial Value | Updated By |
|-------|---------------|------------|
| `age` | 0.0 | `Bean.update()` - increments by 1.0 per tick |
| `speed` | Random within genetic limit | Not yet updated (future: aging effects) |
| `energy` | `config.initial_energy` | `Bean._energy_tick()` - gain minus cost |
| `size` | `config.initial_bean_size` | Not yet updated (future: fat accumulation) |

## TODOs Added

1. `create_phenotype()`: Review initial values for phenotype creation
2. `can_survive_energy()`: Implement energy survival bounds check
3. `can_survive_size()`: Implement size survival bounds check
4. `World._initialize()`: Extract bean creation into a dedicated method

## Files Changed

- `src/beans/bean.py` - Added Phenotype, factory, survival checks, updated Bean class
- `src/beans/world.py` - Updated to create phenotype before bean
- `tests/test_bean.py` - Added sample_phenotype fixture
- `tests/test_energy.py` - Added sample_phenotype fixture
- `tests/test_bean_sprite.py` - Added sample_phenotype fixture
- `tests/test_world.py` - Updated to use create_phenotype

## Diagram

See [2025-12-01-phenotype-diagram.md](./2025-12-01-phenotype-diagram.md)

## Tests

All 70 tests pass.
