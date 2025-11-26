from __future__ import annotations
from typing import List, Tuple
import random
import math
import logging

logger = logging.getLogger(__name__)

PIXEL_DISTANCE = 1  # Minimum distance in pixels between sprites to avoid overlap


class PlacementValidator:
    """Abstract base class for placement validation strategies."""
    
    def mark_placed(self, x: float, y: float, size: int) -> None:
        """Mark a position as occupied after successful placement."""
        raise NotImplementedError()
    
    def mark_failed(self) -> None:
        """Track a failed placement attempt."""
        raise NotImplementedError()
    
    def is_saturated(self) -> bool:
        """Check if world is saturated and no more placements are feasible."""
        raise NotImplementedError()
    
    def reset(self) -> None:
        """Reset validator state."""
        raise NotImplementedError()


class ConsecutiveFailureValidator(PlacementValidator):
    """Detects saturation by tracking consecutive failed placement attempts."""
    
    def __init__(self, threshold: int = 3) -> None:
        self.threshold = threshold
        self.consecutive_failures = 0
    
    def mark_placed(self, x: float, y: float, size: int) -> None:
        """Reset failure counter on successful placement."""
        self.consecutive_failures = 0
    
    def mark_failed(self) -> None:
        """Increment failure counter."""
        self.consecutive_failures += 1
    
    def is_saturated(self) -> bool:
        """Return True if consecutive failures exceed threshold."""
        return self.consecutive_failures >= self.threshold
    
    def reset(self) -> None:
        """Reset failure counter."""
        self.consecutive_failures = 0


class SpaceAvailabilityValidator(PlacementValidator):
    """Tracks occupied space; detects saturation by analyzing remaining free space."""
    
    def __init__(self, width: int, height: int, cell_size: int = 1) -> None:
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_width = (width + cell_size - 1) // cell_size
        self.grid_height = (height + cell_size - 1) // cell_size
        self.occupied: set[tuple[int, int]] = set()
    
    def _get_cells(self, x: float, y: float, size: int) -> set[tuple[int, int]]:
        """Get all grid cells occupied by a circle at (x, y) with given size."""
        cells = set()
        radius = size
        x_min = max(0, int((x - radius) // self.cell_size))
        x_max = min(self.grid_width - 1, int((x + radius) // self.cell_size))
        y_min = max(0, int((y - radius) // self.cell_size))
        y_max = min(self.grid_height - 1, int((y + radius) // self.cell_size))
        
        for grid_x in range(x_min, x_max + 1):
            for grid_y in range(y_min, y_max + 1):
                cells.add((grid_x, grid_y))
        
        return cells
    
    def mark_placed(self, x: float, y: float, size: int) -> None:
        """Mark cells occupied by placed bean."""
        cells = self._get_cells(x, y, size)
        self.occupied.update(cells)
    
    def mark_failed(self) -> None:
        """No-op for space availability validator."""
        pass
    
    def is_saturated(self) -> bool:
        """Check if less than 10% free space remains."""
        total_cells = self.grid_width * self.grid_height
        free_cells = total_cells - len(self.occupied)
        free_ratio = free_cells / total_cells
        return free_ratio < 0.1
    
    def reset(self) -> None:
        """Clear occupied cells."""
        self.occupied.clear()


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
    
    @staticmethod
    def consecutive_failure_validator(threshold: int = 3) -> ConsecutiveFailureValidator:
        """Create a consecutive failure validator."""
        return ConsecutiveFailureValidator(threshold=threshold)
    
    @staticmethod
    def space_availability_validator(width: int, height: int, cell_size: int = 1) -> SpaceAvailabilityValidator:
        """Create a space availability validator."""
        return SpaceAvailabilityValidator(width=width, height=height, cell_size=cell_size)


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
        validator = PlacementStrategy.consecutive_failure_validator(threshold=3)
        
        for bean_idx in range(count):
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
                    validator.mark_placed(x, y, size)
                    placed = True
                    break
            
            if not placed:
                validator.mark_failed()
                logger.warning(f">>>>> Failed to place bean {bean_idx} after {self.max_retries} attempts")
                if validator.is_saturated():
                    logger.warning(f">>>>> World saturated: {len(positions)} of {count} beans placed ({len(positions)/count*100:.1f}%)")
                    break
        
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
