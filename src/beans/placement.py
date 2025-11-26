from __future__ import annotations
from typing import List, Tuple
import random
import math
import logging

logger = logging.getLogger(__name__)

PIXEL_DISTANCE = 1  # Minimum distance in pixels between sprites to avoid overlap

def _snap_to_half_pixel(value: float) -> float:
    """Round to nearest 0.5 for arcade pixel-perfect rendering."""
    return round(value * 2) / 2


class SpatialHash:
    """Grid-based spatial hash for fast collision detection."""
    
    def __init__(self, cell_size: int, width: int, height: int) -> None:
        self.cell_size = cell_size
        self.width = width
        self.height = height
        self.grid: dict[tuple[int, int], list[tuple[float, float]]] = {}
    
    def _get_cell(self, x: float, y: float) -> tuple[int, int]:
        """Get grid cell coordinates for a position."""
        return (int(x // self.cell_size), int(y // self.cell_size))
    
    def insert(self, x: float, y: float) -> None:
        """Insert a position into the spatial hash."""
        cell = self._get_cell(x, y)
        if cell not in self.grid:
            self.grid[cell] = []
        self.grid[cell].append((x, y))
    
    def get_neighbors(self, x: float, y: float, radius: float) -> list[tuple[float, float]]:
        """Get all positions within radius of (x, y)."""
        cell = self._get_cell(x, y)
        neighbors = []
        # Check neighboring cells
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                check_cell = (cell[0] + dx, cell[1] + dy)
                if check_cell in self.grid:
                    for pos in self.grid[check_cell]:
                        distance = math.sqrt((pos[0] - x) ** 2 + (pos[1] - y) ** 2)
                        if distance <= radius:
                            neighbors.append(pos)
        return neighbors


class PlacementStrategy:
    def place(self, count: int, width: int, height: int, size: int) -> List[Tuple[float, float]]:
        raise NotImplementedError()


class RandomPlacementStrategy(PlacementStrategy):
    def __init__(self, max_retries: int = 50) -> None:
        self.max_retries = max_retries

    def place(self, count: int, width: int, height: int, size: int) -> List[Tuple[float, float]]:
        logger.info(f">>>>> RandomPlacementStrategy.place: count={count}, width={width}, height={height}, size={size}")
        if count <= 0:
            logger.warning(">>>>> Count <= 0, returning empty list")
            return []
        
        positions: List[Tuple[float, float]] = []
        spatial_hash = SpatialHash(cell_size=size, width=width, height=height)
        
        for _ in range(count):
            placed = False
            for attempt in range(self.max_retries):
                x = _snap_to_half_pixel(random.uniform(0, width))
                y = _snap_to_half_pixel(random.uniform(0, height))
                
                # Check for collisions with existing positions
                neighbors = spatial_hash.get_neighbors(x, y, radius=size)
                collision_detected = False
                for neighbor_x, neighbor_y in neighbors:
                    distance = math.sqrt((x - neighbor_x) ** 2 + (y - neighbor_y) ** 2)
                    if distance < size:
                        collision_detected = True
                        break
                
                if not collision_detected:
                    positions.append((x, y))
                    spatial_hash.insert(x, y)
                    placed = True
                    break
            
            if not placed:
                logger.warning(f">>>>> Failed to place bean {len(positions)} after {self.max_retries} attempts")
        
        logger.info(f">>>>> Generated {len(positions)} positions")
        return positions
    

class GridPlacementStrategy(PlacementStrategy):
    def __init__(self) -> None:
        pass

    def place(self, count: int, width: int, height: int, size: int) -> List[Tuple[float, float]]:
        logger.info(f">>>>> GridPlacementStrategy.place: count={count}, width={width}, height={height}, size={size}")
        raise NotImplementedError("GridPlacementStrategy is not yet implemented.")


class ClusteredPlacementStrategy(PlacementStrategy):
    def __init__(self) -> None:
        pass

    def place(self, count: int, width: int, height: int, size: int) -> List[Tuple[float, float]]:
        logger.info(f">>>>> ClusteredPlacementStrategy.place: count={count}, width={width}, height={height}, size={size}")
        raise NotImplementedError("ClusteredPlacementStrategy is not yet implemented.")

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
