# Genotype Implementation for Beans

**Date:** 2025-11-30  
**Branch:** genes

> **Note:** As of 2025-12-02, genetics-related code has been extracted to a dedicated module. See [2025-12-02-genetics-module-extraction.md](./2025-12-02-genetics-module-extraction.md) for details.

## Overview

Implemented a genetics system where each bean carries a `Genotype` - an immutable set of genetic traits that will influence bean behavior. Initial beans receive random genotypes; future beans will inherit from parents.

## Problem

Beans had no genetic variation. All beans behaved identically based on config values. To enable natural selection and evolution, beans need inherited traits that affect their behavior.

## Solution

### Gene Enum with Metadata

Each gene is defined as an enum value holding its name and valid range:

```python
class GeneInfo(NamedTuple):
    name: str
    min: float
    max: float

class Gene(Enum):
    METABOLISM_SPEED = GeneInfo("metabolism_speed", 0.0, 1.0)
    MAX_GENETIC_SPEED = GeneInfo("max_genetic_speed", 0.0, 1.0)
    FAT_ACCUMULATION = GeneInfo("fat_accumulation", 0.0, 1.0)
    MAX_GENETIC_AGE = GeneInfo("max_genetic_age", 0.0, 1.0)
```

### Genes as Multipliers

All genes use 0.0-1.0 range and act as **multipliers** on config base values:

| Gene | Phenotype Formula (future) |
|------|---------------------------|
| `METABOLISM_SPEED` | `energy_burn = base_cost * (0.5 + gene_value)` |
| `MAX_GENETIC_SPEED` | `max_speed = config.speed_max * gene_value` |
| `FAT_ACCUMULATION` | `storage_efficiency = gene_value` |
| `MAX_GENETIC_AGE` | `max_age = config.max_age_years * gene_value` |

**Note:** Min values may need tuning to avoid beans that can't move (speed=0) or die immediately (age=0).

### Genotype as Pydantic Model

Immutable, validated container for gene values:

```python
class Genotype(BaseModel):
    genes: dict[Gene, float]
    model_config = {"frozen": True}
```

### Bean Receives Genotype (Doesn't Create It)

```python
Bean(config=cfg, id=1, sex=Sex.MALE, genotype=genotype)
```

### World Creates Random Genotypes for Initial Population

```python
Bean(..., genotype=create_random_genotype())
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Gene enum with NamedTuple values** | Type-safe, self-documenting, easy iteration |
| **Genes as multipliers (0.0-1.0)** | Consistent range, config sets world limits, gene sets individual potential |
| **Pydantic for Genotype** | Built-in validation, immutability, serialization |
| **Bean doesn't create genotype** | Clear separation - beans don't know their origin |

## Files Changed

- `src/beans/bean.py` - Added Gene, GeneInfo, Genotype, create_random_genotype()
- `src/beans/world.py` - Updated to create random genotypes for initial beans
- `tests/test_bean.py` - Added 7 genotype tests, updated existing tests
- `tests/test_bean_sprite.py` - Updated fixtures with genotype
- `tests/test_energy.py` - Updated fixtures with genotype
- `tests/test_world.py` - Updated test to pass genotype

## Next Steps

1. Implement gene effects on bean behavior (phenotype expression)
2. Tune min values for MAX_GENETIC_AGE and MAX_GENETIC_SPEED
3. Implement mating and gene inheritance/combination
4. Add mutation during inheritance

## Diagram

See [2025-11-30-genotype-diagram.md](./2025-11-30-genotype-diagram.md)
