from __future__ import annotations
from typing import List, Tuple
import random
import math
import logging

logger = logging.getLogger(__name__)
PIXEL_DISTANCE = 1


class SpatialHash:
    """Fast spatial hash for collision detection using grid-based spatial partitioning."""
    
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
    
    def has_collision(self, x: float, y: float, min_distance: float) -> bool:
        """Check if position collides with any existing position within min_distance."""
        cell = self._get_cell(x, y)
        min_distance_sq = min_distance * min_distance
        
        # Check current cell and 8 neighbors
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                neighbor_cell = (cell[0] + dx, cell[1] + dy)
                if neighbor_cell in self.grid:
                    for px, py in self.grid[neighbor_cell]:
                        dist_sq = (x - px) ** 2 + (y - py) ** 2
                        if dist_sq < min_distance_sq:
                            logger.debug(f">>>>> SpatialHash.has_collision: collision at ({x:.2f}, {y:.2f}) with ({px:.2f}, {py:.2f}), distance={math.sqrt(dist_sq):.2f}")
                            return True
        return False


class PlacementStrategy:
    def place(self, count: int, width: int, height: int, size: int) -> List[Tuple[float, float]]:
        raise NotImplementedError("PlacementStrategy is an abstract base class.")
    
    def _get_min_distance(self, size: int) -> float:
        """Calculate minimum distance between bean centers: size + PIXEL_DISTANCE."""
        return float(size + PIXEL_DISTANCE)
    
    def _get_valid_bounds(self, size: int, width: int, height: int) -> Tuple[float, float, float, float]:
        """Get valid positioning bounds accounting for PIXEL_DISTANCE and bean radius.
        
        Returns: (min_x, max_x, min_y, max_y)
        """
        min_coord = PIXEL_DISTANCE + (size / 2.0)
        max_x = width - min_coord
        max_y = height - min_coord
        return (min_coord, max_x, min_coord, max_y)
    
    def _can_fit(self, size: int, count: int, width: int, height: int) -> bool:
        effective_diameter = size + (2 * PIXEL_DISTANCE)
        area_per_sprite = math.pi * ((effective_diameter / 2.0) ** 2)
        total_area_needed = count * area_per_sprite
        available_area = width * height
        logger.debug(f">>>>> PlacementStrategy._can_fit: size={size}, count={count}, width={width}, height={height}, total_area_needed={total_area_needed}, available_area={available_area}, packing_efficiency={self.packing_efficiency}")
        return total_area_needed <= (available_area * self.packing_efficiency)

class RandomPlacementStrategy(PlacementStrategy):
    def __init__(self, packing_efficiency: float = 0.45) -> None:
        self.packing_efficiency = packing_efficiency

    def place(self, count: int, width: int, height: int, size: int) -> List[Tuple[float, float]]:
        logger.info(f">>>>> RandomPlacementStrategy.place: count={count}, width={width}, height={height}, size={size}")
        
        if count <= 0:
            logger.warning(">>>>> Count <= 0, returning empty list")
            return []
        
        if not self._can_fit(size, int(count * 0.9), width, height):
            logger.warning(">>>>> Cannot fit at least 90% of sprites    , returning empty list")
            return []
        
        min_x, max_x, min_y, max_y = self._get_valid_bounds(size, width, height)
        min_distance = self._get_min_distance(size)
        
        def random_generator():
            """Generate unlimited random positions within valid bounds."""
            while True:
                x = random.uniform(min_x, max_x)
                y = random.uniform(min_y, max_y)
                yield (x, y)
        
        # Use spatial hash for collision detection
        spatial_hash = SpatialHash(cell_size=max(1, int(size * 3)))
        positions: List[Tuple[float, float]] = []
        
        for x, y in random_generator():
            if len(positions) >= count:
                break
            
            if not spatial_hash.has_collision(x, y, min_distance):
                spatial_hash.add(x, y)
                positions.append((x, y))
        
        # Check 90% threshold
        min_required = int(count * 0.9)
        if len(positions) >= min_required:
            logger.info(f">>>>> RandomPlacementStrategy: placed {len(positions)}/{count} (ratio={len(positions)/count:.2%})")
            return positions
        else:
            logger.warning(f">>>>> Failed to place minimum 90%. Placed: {len(positions)}, Required: {min_required}")
            return []


class GridPlacementStrategy(PlacementStrategy):
    def __init__(self, packing_efficiency: float = 0.64) -> None:
        self.packing_efficiency = packing_efficiency 

    def place(self, count: int, width: int, height: int, size: int) -> List[Tuple[float, float]]:
        raise NotImplementedError("GridPlacementStrategy is not implemented yet.")

class ClusteredPlacementStrategy(PlacementStrategy):
    def __init__(self, packing_efficiency: float = 0.55) -> None:
        self.packing_efficiency = packing_efficiency

    def place(self, count: int, width: int, height: int, size: int) -> List[Tuple[float, float]]:
        raise NotImplementedError("ClusteredPlacementStrategy is not implemented yet.")

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
