from __future__ import annotations
from typing import List, Tuple
import random
import math
import logging

logger = logging.getLogger(__name__)


class SpatialHash:
    """Fast spatial hash for collision detection."""
    
    def __init__(self, cell_size: int) -> None:
        self.cell_size = max(1, cell_size)
        self.grid: dict[Tuple[int, int], List[Tuple[float, float]]] = {}
    
    def _get_cell(self, x: float, y: float) -> Tuple[int, int]:
        """Get grid cell coordinates for position."""
        return (int(x // self.cell_size), int(y // self.cell_size))
    
    def add(self, x: float, y: float) -> None:
        """Add position to hash grid."""
        cell = self._get_cell(x, y)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append((x, y))
        logger.debug(f">>>>> SpatialHash.add: position=({x:.2f}, {y:.2f}), cell={cell}")
    
    def has_collision(self, x: float, y: float, collision_radius: float) -> bool:
        """Check if position collides with any existing position within radius."""
        cell = self._get_cell(x, y)
        radius_sq = collision_radius * collision_radius
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                neighbor_cell = (cell[0] + dx, cell[1] + dy)
                if neighbor_cell in self.grid:
                    for px, py in self.grid[neighbor_cell]:
                        dist_sq = (x - px) ** 2 + (y - py) ** 2
                        if dist_sq < radius_sq:
                            logger.debug(f">>>>> SpatialHash.has_collision: collision at ({x:.2f}, {y:.2f}) with ({px:.2f}, {py:.2f})")
                            return True
        return False


def validate_placements(positions: List[Tuple[float, float]], size: int, width: int, height: int) -> None:
    """Validate that returned placements have no overlaps and are within bounds.
    
    Args:
        positions: List of (x, y) coordinates from place()
        size: Sprite size (collision radius)
        width: World width
        height: World height
    
    Raises:
        AssertionError: If placements overlap or are out of bounds
    """
    if not positions:
        raise AssertionError("Placements list is empty")
    
    collision_radius = float(size)
    
    # Check each position against others for overlaps
    for i, (x1, y1) in enumerate(positions):
        # Verify within bounds
        if x1 < 0 or x1 > width or y1 < 0 or y1 > height:
            raise AssertionError(
                f"Position {i} at ({x1:.2f}, {y1:.2f}) is out of bounds [0, {width}] x [0, {height}]"
            )
        
        # Check for overlaps with all subsequent positions
        for j in range(i + 1, len(positions)):
            x2, y2 = positions[j]
            dist_sq = (x1 - x2) ** 2 + (y1 - y2) ** 2
            radius_sq = collision_radius * collision_radius
            
            if dist_sq < radius_sq:
                raise AssertionError(
                    f"Positions {i} and {j} overlap: ({x1:.2f}, {y1:.2f}) and ({x2:.2f}, {y2:.2f}), "
                    f"distance={math.sqrt(dist_sq):.2f}, required_separation={size}"
                )
    
    logger.info(f">>>>> validate_placements: All {len(positions)} placements are valid (no overlaps, within bounds)")


class PlacementStrategy:
    def place(self, count: int, width: int, height: int, size: int) -> List[Tuple[float, float]]:
        raise NotImplementedError()
    
    def _can_fit(self, size: int, count: int, width: int, height: int) -> bool:
        effective_diameter = size + 2  # diameter + 1px on each side
        area_per_sprite = math.pi * ( (effective_diameter/2) * (effective_diameter/2))
        total_area_needed = count * area_per_sprite
        available_area = width * height
        logger.debug(f">>>>> PlacementStrategy._can_fit: size={size}, count={count}, width={width}, height={height}, total_area_needed={total_area_needed}, available_area={available_area}, packing_efficiency={self.packing_efficiency}")
        return total_area_needed <= (available_area * self.packing_efficiency)
    
    def _place_with_collision_detection(
        self,
        generator,
        count: int,
        width: int,
        height: int,
        size: int
    ) -> List[Tuple[float, float]]:
        """
        Generic collision detection wrapper for placement strategies.
        
        Args:
            generator: Callable that yields (x, y) positions
            count: Target number of sprites to place
            width, height: World dimensions
            size: Sprite size (collision radius)
        
        Returns:
            List of collision-free positions, or raises SystemExit if <90% threshold
        """
        hash_grid = SpatialHash(cell_size=max(1, size * 3))
        positions: List[Tuple[float, float]] = []
        collision_radius = float(size)
        
        for x, y in generator:
            if len(positions) >= count:
                break
            
            if not hash_grid.has_collision(x, y, collision_radius):
                hash_grid.add(x, y)
                positions.append((x, y))
        
        # Check if we met minimum threshold (90%)
        min_sprites = int(count * 0.9)
        if len(positions) >= min_sprites:
            logger.info(f">>>>> Generated {len(positions)} collision-free positions (requested {count}, ratio={len(positions)/count:.2%})")
            return positions
        else:
            logger.error(f">>>>> Failed to place minimum sprites. Placed: {len(positions)}, Required: {min_sprites}, Requested: {count}")
            raise SystemExit(1)


class RandomPlacementStrategy(PlacementStrategy):
    def __init__(self, packing_efficiency: float = 0.45) -> None:
        self.packing_efficiency = packing_efficiency

    def place(self, count: int, width: int, height: int, size: int) -> List[Tuple[float, float]]:
        logger.info(f">>>>> RandomPlacementStrategy.place: count={count}, width={width}, height={height}, size={size}")

        if count <= 0:
            logger.warning(">>>>> Count <= 0, returning empty list")
            return []
        
        if not self._can_fit(size, count, width, height):
            logger.error(f">>>>> Not enough space to fit {count} sprites of size {size} in {width}x{height}")
            raise SystemExit(1)
        
        def random_generator():
            """Generate unlimited random positions."""
            while True:
                yield (random.uniform(0, width), random.uniform(0, height))
        
        return self._place_with_collision_detection(
            random_generator(), count, width, height, size
        )
    

class GridPlacementStrategy(PlacementStrategy):
    def __init__(self, packing_efficiency: float = 0.64) -> None:
        self.packing_efficiency = packing_efficiency 

    def place(self, count: int, width: int, height: int, size: int) -> List[Tuple[float, float]]:
        logger.info(f">>>>> GridPlacementStrategy.place: count={count}, width={width}, height={height}, size={size}")
        if count <= 0:
            logger.warning(">>>>> Count <= 0, returning empty list")
            return []
        
        cols = max(1, width // size)
        rows = max(1, height // size)
        positions: List[Tuple[float, float]] = []
        for r in range(rows):
            for c in range(cols):
                if len(positions) >= count:
                    break
                x = (c + 0.5) * size
                y = (r + 0.5) * size
                positions.append((x, y))
            if len(positions) >= count:
                break
        
        # Check if we met minimum threshold (90%)
        min_sprites = int(count * 0.9)
        if len(positions) >= min_sprites:
            logger.info(f">>>>> Generated {len(positions)} positions (requested {count}, ratio={len(positions)/count:.2%})")
            return positions
        else:
            logger.error(f">>>>> Failed to place minimum sprites. Placed: {len(positions)}, Required: {min_sprites}, Requested: {count}")
            raise SystemExit(1)


class ClusteredPlacementStrategy(PlacementStrategy):
    def __init__(self, packing_efficiency: float = 0.55) -> None:
        self.packing_efficiency = packing_efficiency

    def place(self, count: int, width: int, height: int, size: int) -> List[Tuple[float, float]]:
        logger.info(f">>>>> ClusteredPlacementStrategy.place: count={count}, width={width}, height={height}, size={size}")
        
        if count <= 0:
            logger.warning(">>>>> Count <= 0, returning empty list")
            return []
        
        if not self._can_fit(size, count, width, height):
            logger.error(f">>>>> Not enough space to fit {count} sprites of size {size} in {width}x{height}")
            raise SystemExit(1)
        
        clusters = max(1, count // 5)
        centers = [(random.uniform(0, width), random.uniform(0, height)) for _ in range(clusters)]
        logger.debug(f">>>>> Created {clusters} cluster centers")
        
        def cluster_generator():
            """Generate positions around cluster centers."""
            i = 0
            while True:
                center = centers[i % clusters]
                angle = random.random() * 2 * math.pi
                radius = random.random() * (size * 2)
                x = center[0] + radius * math.cos(angle)
                y = center[1] + radius * math.sin(angle)
                x = max(0.0, min(float(width), x))
                y = max(0.0, min(float(height), y))
                yield (x, y)
                i += 1
        
        return self._place_with_collision_detection(
            cluster_generator(), count, width, height, size
        )


def create_strategy_from_name(name: str) -> PlacementStrategy:
    """Return a placement strategy instance given a config name string."""
    logger.info(f">>>>> create_strategy_from_name: name={name}")
    match name.lower() if name else '':
        case 'random':
            logger.debug(">>>>> Creating RandomPlacementStrategy")
            return RandomPlacementStrategy()
        case 'grid':
            logger.debug(">>>>> Creating GridPlacementStrategy")
            return GridPlacementStrategy()
        case 'clustered' | 'cluster':
            logger.debug(">>>>> Creating ClusteredPlacementStrategy")
            return ClusteredPlacementStrategy()
        case _:
            logger.debug(f">>>>> Unknown strategy '{name}', defaulting to RandomPlacementStrategy")
            return RandomPlacementStrategy()
