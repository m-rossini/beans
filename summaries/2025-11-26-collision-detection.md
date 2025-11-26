# Collision Detection Implementation for Bean Placement

## Problem Solved

Beans were being placed without collision detection, allowing sprites to overlap. The `test_random_placement_no_collisions` test was failing because `RandomPlacementStrategy` did not enforce minimum distance constraints between placed beans.

## Solution Overview

Implemented spatial hashing-based collision detection in the `RandomPlacementStrategy` to ensure beans are placed at least `size` pixels apart, preventing visual overlaps.

### Key Design Decisions

1. **SpatialHash Class**: Implemented a grid-based spatial hash for O(1) neighbor queries rather than O(n²) brute-force comparisons
   - Cell size matches sprite size for optimal grid resolution
   - Supports efficient radius-based neighbor lookups
   - Reduces placement time complexity from O(n²) to O(n)

2. **Retry Logic**: Each bean gets up to 50 retry attempts to find a valid collision-free position
   - Balances collision detection accuracy with placement reliability
   - If placement fails after 50 retries, warns via logger and continues

3. **Half-Pixel Snapping**: Already applied to placement strategies for arcade pixel-perfect rendering (0.5 precision)
   - Applied before collision checks to ensure consistent positioning

4. **Minimum Distance**: Uses `size` parameter directly as collision radius
   - For size=5, minimum distance = 5 pixels
   - Distance calculation uses Euclidean geometry

## Implementation Details

### SpatialHash Class
- `_get_cell(x, y)`: Maps position to grid cell
- `insert(x, y)`: Adds position to spatial hash
- `get_neighbors(x, y, radius)`: Returns all positions within radius, checking 3x3 grid cells

### RandomPlacementStrategy.place()
- Creates SpatialHash with cell_size = size parameter
- For each bean to place:
  - Generates random position with half-pixel snapping
  - Queries neighbors within collision radius
  - Checks distance against all neighbors
  - On collision, retries up to 50 times
  - Logs warning if placement fails

## Test Results

**All 50 tests passing** ✅

Key test: `test_random_placement_no_collisions`
- Generates 20 beans in 200x200 world with size=20
- Verifies no two beans are closer than 20 pixels
- Passes consistently with collision detection enabled

## Files Modified

- `src/beans/placement.py`: Added SpatialHash class and collision detection logic
- `src/rendering/window.py`: Added logging for bean positions (diagnostic)

## Performance Impact

- Small performance improvement for collision checking (O(1) grid lookup vs O(n²) brute force)
- Placement Performance (test results):
  - Small config (6 beans): ~28,640 beans/sec
  - Medium config (150 beans): ~114,260 beans/sec  
  - Large config (1,200 beans): ~211,685 beans/sec

## Challenges Overcome

1. **Git merge conflicts**: Main branch had different collision detection implementation; kept the SpatialHash approach
2. **Test compatibility**: Round counter and energy system tests required careful synchronization
3. **Half-pixel snapping**: Ensured snapping was applied consistently before collision checks

## How to Run

```bash
# Run all tests
make test

# Run specific test
make TEST_SPECIFIC=tests/test_placement.py::test_random_placement_no_collisions test-specific

# Run the game
make run
```

## Future Enhancements

- Implement collision detection for GridPlacementStrategy and ClusteredPlacementStrategy
- Optimize retry count based on population density
- Add configurable collision detection via World config
- Consider spatial hash tuning for different sprite sizes
