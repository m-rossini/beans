# Collision Detection Implementation - Architecture Decision Record

## Problem Statement
Bean placement strategies (Random, Grid, Clustered) needed to support collision detection to prevent sprite overlaps while maintaining minimum placement success thresholds.

## Solution Overview
Implemented spatial hash-based O(1) collision detection with consistent 90% placement success threshold across all strategies. All placement methods follow a unified generation + validation pattern.

## Key Design Decisions

### 1. Spatial Hash Grid
**Decision**: Use grid-based spatial hashing instead of brute-force collision checking.
- **Cell Size**: `size * 3` (sprite size multiplied by 3)
- **Complexity**: O(1) average collision detection per sprite
- **Implementation**: Dictionary-based grid storing positions in neighboring cells

**Rationale**: 
- Brute-force O(n²) checking would degrade rapidly with population size
- Cell-based approach checks only nearby neighbors (max 9 cells)
- Scales linearly with final placement count, not quadratically

### 2. Unified Collision Detection Method
**Decision**: Extract shared `_place_with_collision_detection()` helper in base class.

**Implementation**:
```python
def _place_with_collision_detection(
    self, generator, count, width, height, size
) -> List[Tuple[float, float]]
```

**Rationale**:
- Random and Clustered strategies had identical collision detection logic (DRY violation)
- Grid strategy differs (finite grid vs infinite generator) but applies same threshold
- Shared method eliminates duplication while allowing strategy-specific generators

### 3. 90% Success Threshold
**Decision**: Apply 90% minimum placement ratio AFTER generation completes, not as early exit.

**Pattern**:
```python
# Generate all available positions
for position in generator:
    if len(positions) >= count:
        break
    if not has_collision(position):
        positions.append(position)

# Check threshold AFTER generation
min_sprites = int(count * 0.9)
if len(positions) >= min_sprites:
    return positions
else:
    raise SystemExit(1)
```

**Rationale**:
- 90% is a acceptance criterion, not an early exit check
- Allows generator to exhaust naturally (infinite generators run until count reached)
- Grid strategy can generate fewer positions (finite grid) and still pass if ratio >= 90%
- Separates "how many can we generate" from "did we meet minimum requirement"

### 4. Strategy-Specific Packing Efficiency
**Decision**: Each strategy has its own packing efficiency constant for `_can_fit()` checks.

**Values**:
- Random: 0.45 (45% area utilization - conservative for random placement)
- Grid: 0.64 (64% area utilization - higher packing density)
- Clustered: 0.55 (55% area utilization - between random and grid)

**Rationale**:
- Different strategies have different spatial characteristics
- Random placement can't pack as densely as regular grid
- Clustering offers moderate efficiency between extremes
- `_can_fit()` provides early warning if space is genuinely insufficient

## Architecture

```
PlacementStrategy (base class)
├── _can_fit(): Check theoretical space feasibility
├── _place_with_collision_detection(): Shared collision detection logic
│
├── RandomPlacementStrategy
│   ├── place(): Calls infinite random generator + shared collision detection
│   └── Generator: Unlimited random positions
│
├── GridPlacementStrategy
│   ├── place(): Iterates grid cells directly
│   └── Pattern: Finite grid, applies 90% threshold after grid exhausted
│
└── ClusteredPlacementStrategy
    ├── place(): Calls cluster-offset generator + shared collision detection
    └── Generator: Positions around random cluster centers
```

## Test Coverage
- **Total Tests**: 52 passing
- **Coverage**: 92% overall
  - `placement.py`: 84% (missing lines are error paths and debug logging)
  - Other modules: 89-100%
- **Placement-Specific Tests**: 8 tests covering all three strategies

## Key Implementation Details

### SpatialHash Class
- O(1) average collision detection via cell lookup
- Stores positions in grid cells based on cell_size
- `has_collision()` checks 9 neighboring cells (3x3 neighborhood)

### Random Strategy
- Infinite generator yields random world positions
- Collision detection loop: generate → check collision → append if valid
- Stops when count reached or generator exhausted
- Early exit: `_can_fit()` check prevents impossible requests

### Grid Strategy
- Finite generation: calculates grid dimensions, iterates cells
- No collision detection needed (grid inherently non-overlapping)
- Applies 90% threshold after grid cells exhausted
- Early exit: `_can_fit()` check for impossible space requests

### Clustered Strategy
- Infinite generator creates cluster centers, generates offsets around them
- Uses trigonometric positioning (angle + radius from center)
- Collision detection prevents clusters from overlapping
- Early exit: `_can_fit()` check for impossible requests

## Challenges Overcome

1. **DRY Violation**: Random and Clustered both had identical collision logic
   - Solution: Extracted `_place_with_collision_detection()` shared method

2. **Threshold Placement**: Initial approach used `_can_fit()` as early exit
   - Problem: This bypassed the 90% threshold contract
   - Solution: Applied 90% threshold AFTER generation completes, not before

3. **Architectural Inconsistency**: Grid strategy differs from Random/Clustered
   - Random/Clustered: Infinite generators → collision check → 90% threshold
   - Grid: Finite iteration → 90% threshold
   - Solution: Unified interface via base class, strategy-specific generators

## Performance Characteristics
- **Random Placement**: O(n) where n = final placed count (generator calls + collision checks)
- **Grid Placement**: O(grid_size) where grid_size = (width/size) × (height/size)
- **Clustered Placement**: O(n) with per-position cost higher than Random due to generator overhead
- **Collision Detection**: O(1) average per sprite check via spatial hashing

## Future Considerations
- `_can_fit()` currently used for early warnings but could be removed if diagnostic logging sufficient
- Cell size formula (`size * 3`) could be tuned based on empirical testing
- 90% threshold could be parameterized if different strategies need different minimums
- Spatial hash could be pre-allocated for known world bounds to reduce dynamic allocation

## How to Run
```bash
make test                    # Run all 52 tests
make test-cov              # Run tests with 92% coverage report
make format                # Format code with black/isort
make type-check           # Run mypy type checking
```

## Validation
✅ All 52 tests passing
✅ 92% code coverage maintained
✅ Collision-free placement verified
✅ 90% threshold consistently applied
✅ No code duplication in collision detection
✅ Unified interface across all strategies
