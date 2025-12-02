# Genetics Module Extraction

**Date:** 2025-12-02  
**Branch:** add-collision-detection

## Overview

Extracted all genetics-related classes and functions from `src/beans/bean.py` into a dedicated `src/beans/genetics.py` module. This improves code organization, separation of concerns, and makes the genetics system more discoverable.

## Problem

The `bean.py` file had grown to contain both the `Bean` entity class and all genetics-related code (genotype, phenotype, genes, helper functions). This mixed responsibilities and made the file harder to navigate.

## Solution

Created `src/beans/genetics.py` containing:

### Classes (4)
- `GeneInfo` - NamedTuple for gene metadata (name, min/max range)
- `Gene` - Enum defining gene types with validation ranges
- `Genotype` - Pydantic BaseModel for immutable genetic blueprint
- `Phenotype` - Dataclass for mutable trait expression

### Functions (10)
- `size_sigma()` - Calculate size standard deviation (±15%)
- `size_z_score()` - Calculate z-score for size deviation
- `age_speed_factor()` - Calculate speed factor based on age lifecycle
- `genetic_max_age()` - Calculate max age from config and genotype
- `size_target()` - Calculate target size based on age and genotype
- `genetic_max_speed()` - Calculate max speed from config and genotype
- `create_random_genotype()` - Factory for random genotypes
- `create_phenotype()` - Factory for initial phenotypes
- `can_survive_energy()` - Placeholder for energy survival check
- `can_survive_size()` - Placeholder for size survival check

## Module Structure

```
src/beans/
├── __init__.py
├── bean.py          # Bean, Sex (imports from genetics)
├── genetics.py      # NEW: All genetics-related code
├── placement.py
├── population.py
└── world.py         # Imports from genetics for factories
```

## Import Pattern

```python
# In bean.py
from .genetics import (
    Gene, Genotype, Phenotype,
    size_z_score, size_target,
    genetic_max_age, genetic_max_speed, age_speed_factor,
)

# In world.py
from .genetics import create_random_genotype, create_phenotype

# In tests
from beans.bean import Bean, Sex
from beans.genetics import Gene, Genotype, Phenotype, create_random_genotype
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Separate genetics module** | Clear separation of concerns, easier to find genetics code |
| **Bean imports from genetics** | Bean still uses genetics types but doesn't define them |
| **Factory functions in genetics** | `create_random_genotype` and `create_phenotype` stay with their types |
| **Helper functions in genetics** | Functions like `age_speed_factor` are genetics-specific |

## Files Changed

- `src/beans/genetics.py` - **NEW** - All genetics code with logging
- `src/beans/bean.py` - Removed genetics code, imports from `.genetics`
- `src/beans/world.py` - Updated imports to use `.genetics`
- `tests/test_bean.py` - Updated imports
- `tests/test_energy.py` - Updated imports
- `tests/test_bean_sprite.py` - Updated imports
- `tests/test_world.py` - Updated imports

## Testing

All genetics-related tests pass (21 tests). The module extraction is a pure refactoring with no behavioral changes.

## Logging

Added `logger = logging.getLogger(__name__)` to genetics module with debug logs in:
- `create_random_genotype()` - Logs created gene values
- `create_phenotype()` - Logs created phenotype values
