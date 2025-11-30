# Placement Validator Refactoring

**Date:** 2025-11-28  
**Branch:** add-collision-detection

## Overview

Simplified the placement validator system by removing underperforming cell-based validators and keeping only two clear options: a fast default and an accurate alternative.

## Problem

The original implementation had 4 validators:
- `ConsecutiveFailureValidator` - stops after 3 consecutive failed placements
- `SpaceAvailabilityValidator` - cell-based, stops when <10% free space
- `MaximumDensityValidator` - cell-based, stops when no valid cells remain
- `PixelDensityValidator` - pixel-level accuracy, stops when no valid pixels remain

Performance testing revealed:
- `maximum_density` offered **no advantage** over `consecutive_failure` (similar placement rate, slower)
- `space_availability` was **too conservative** (stopped early, placed 10-20% fewer beans)
- Cell-based tracking couldn't capture pixel-level gaps, causing premature saturation

## Solution

Removed `SpaceAvailabilityValidator` and `MaximumDensityValidator`, keeping only:

| Validator | Use Case | Trade-off |
|-----------|----------|-----------|
| `consecutive_failure` | **Default** | Fast, ~70% placement at high density |
| `pixel_density` | Maximum packing | ~85% placement, 5-10× slower |

## Performance Results (1600×1200 @ density=0.7)

| Validator | Beans Placed | Rate | Time |
|-----------|-------------|------|------|
| consecutive_failure | 39,278 | 73.1% | 931ms |
| pixel_density | 46,532 | **86.6%** | 6,369ms |

## Key Decisions

1. **Removed cell-based validators**: Grid discretization causes false negatives (marking valid pixels as invalid)
2. **Kept pixel-level accuracy**: `PixelDensityValidator` uses bitset (~240KB for 1600×1200) for precise tracking
3. **Default remains fast**: `consecutive_failure` is the sensible default for most use cases

## Files Changed

- `src/beans/placement.py` - Removed ~120 lines (2 classes)
- `src/config/large.json` - Updated to use `pixel_density` at density 0.55
- `tests/test_placement_validators.py` - Updated tests for `PixelDensityValidator`
- `tests/test_placement_performance.py` - Simplified comparison tests

## Configuration

```json
{
  "world": {
    "placement_validator": "consecutive_failure"  // or "pixel_density"
  }
}
```

## Diagram

See [2025-11-28-placement-validator-diagram.md](./2025-11-28-placement-validator-diagram.md)
