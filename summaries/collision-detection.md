# Beans Project - Architecture & Decision Records

## Latest: Random Placement Strategy (November 26, 2025)

**Status**: ✅ Complete - All 48 tests passing

- **Main Summary**: [2025-11-26-random-placement-strategy-with-collision-detection.md](./2025-11-26-random-placement-strategy-with-collision-detection.md)
- **Diagrams**: [2025-11-26-placement-algorithm-diagrams.md](./2025-11-26-placement-algorithm-diagrams.md)

### Highlights
- ✅ O(1) collision detection via spatial hashing
- ✅ ~230k beans/sec placement rate at 1200 bean scale
- ✅ 90% placement success threshold enforcement
- ✅ 48 tests (7 new, all passing)

---

## Architecture Timeline

### 2025-11-25: Energy System
[2025-11-25-energy-system.md](./2025-11-25-energy-system.md) | [Diagrams](./2025-11-25-energy-system-diagram.md)
- Energy tracking, gain/cost mechanics, death conditions

### 2025-11-25: Population Estimation  
[2025-11-25-population-estimation.md](./2025-11-25-population-estimation.md) | [Diagrams](./2025-11-25-population-estimation-diagram.md)
- Density-based estimation, SoftLog ceiling, male/female ratios

### 2025-11-19: Bean Class Split
[2025-11-19-BeanClassSplitIntoLogicAndSpriteComponents.md](./2025-11-19-BeanClassSplitIntoLogicAndSpriteComponents.md)
- Logic/sprite separation pattern

### 2025-01-20: Collision Detection Foundation
[2025-01-20-collision-detection-implementation.md](./2025-01-20-collision-detection-implementation.md)
- Initial collision detection architecture

---

## Core Design Patterns

### 1. Strategy Pattern (Placement)
- `PlacementStrategy` base with shared helpers (`_get_min_distance()`, `_get_valid_bounds()`, `_can_fit()`)
- ✅ `RandomPlacementStrategy` - Random placement with O(1) collision detection
- 🔲 `GridPlacementStrategy` - Future implementation
- 🔲 `ClusteredPlacementStrategy` - Future implementation

### 2. Estimator Pattern (Population)
- `PopulationEstimator` base class
- `DensityPopulationEstimator` - Area-based calculation
- `SoftLogPopulationEstimator` - Logarithmic soft cap

### 3. Component Separation
- **Bean** - Logic only (age, energy, gender)
- **BeanSprite** - Rendering only (position, visual)
- **World** - Orchestrator (manages beans and lifecycle)

---

## Performance Metrics

| Scale | Dimensions | Size | Count | Time | Rate |
|-------|-----------|------|-------|------|------|
| Small | 400×300 | 10 | 6 | 0.21ms | 28,558/sec |
| Medium | 800×600 | 8 | 150 | 1.42ms | 105,308/sec |
| Large | 2000×1500 | 5 | 1200 | 5.25ms | 228,397/sec |

**Algorithm**: O(1) avg collision detection via spatial hash with 9-cell neighborhood checks

---

## Test Summary

✅ **48 Tests Passing** (0 failures)

- Placement tests: 4
- World integration: 2  
- Rendering: 4
- Performance: 3
- Config: 10
- Energy: 4
- Population: 14
- Bean: 3
- BeanSprite: 3
- Other: 2

---

## Quick Reference

### Placement Math
- **Valid bounds**: `[PIXEL_DISTANCE + size/2, width - PIXEL_DISTANCE - size/2]`
- **Collision distance**: `size + PIXEL_DISTANCE` (center-to-center)
- **Spatial hash cell**: `sprite_size × 3`
- **Success threshold**: ≥ 90% of requested beans

### Key Files
```
src/beans/placement.py           # SpatialHash + RandomPlacementStrategy
tests/test_placement.py          # Unit tests
tests/test_placement_performance.py  # Benchmarks
summaries/                       # Architecture docs & diagrams
```

### Run Commands
```bash
make test                        # All tests
make test-specific TEST_SPECIFIC=tests/test_placement.py
make test-specific TEST_SPECIFIC=tests/test_placement_performance.py
```

---

## Related Documentation

- [Bean Sprite Architecture](./bean_sprite_architecture.md)
- [Collision Detection Architecture](./collision-detection-architecture.md)

---

## Next Phases

1. **Grid Placement** - Regular spacing pattern (~64% efficiency)
2. **Clustered Placement** - Grouped population centers (~55% efficiency)  
3. **Optimization** - Partial updates, caching, strategy selection
4. **Advanced Rendering** - Particle effects, trails, interactions
