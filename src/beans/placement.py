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


class PixelDensityValidator(PlacementValidator):
    """Pixel-level validator using bitset for maximum accuracy.
    
    Tracks valid placement positions at pixel granularity using two bitsets:
    - occupied_bitmap: marks pixels within placed beans
    - invalid_bitmap: marks pixels within collision distance of any bean
    
    Only saturates when no valid pixels remain. More accurate than cell-based
    validators but with higher memory usage (~240KB for 1600x1200).
    """
    
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.total_pixels = width * height
        # Bitset for invalid placement positions (within collision distance)
        self.invalid_bitmap = bytearray((self.total_pixels + 7) // 8)
        self.invalid_count = 0
    
    def _get_pixel_index(self, x: int, y: int) -> int:
        """Convert pixel coordinates to linear index."""
        return y * self.width + x
    
    def _set_invalid(self, pixel_index: int) -> bool:
        """Mark pixel as invalid. Returns True if already invalid."""
        byte_index = pixel_index // 8
        bit_index = pixel_index % 8
        was_set = (self.invalid_bitmap[byte_index] >> bit_index) & 1
        if not was_set:
            self.invalid_bitmap[byte_index] |= (1 << bit_index)
            self.invalid_count += 1
        return bool(was_set)
    
    def mark_placed(self, x: float, y: float, size: int) -> None:
        """Mark all pixels within collision distance as invalid."""
        center_x = int(x)
        center_y = int(y)
        # Collision distance is 'size' pixels (bean diameter)
        # Mark all pixels where a new bean center would collide
        for dy in range(-size, size + 1):
            for dx in range(-size, size + 1):
                px = center_x + dx
                py = center_y + dy
                if 0 <= px < self.width and 0 <= py < self.height:
                    # Check if within circular collision zone
                    if dx * dx + dy * dy <= size * size:
                        pixel_index = self._get_pixel_index(px, py)
                        self._set_invalid(pixel_index)
    
    def mark_failed(self) -> None:
        """No-op for pixel density validator."""
        pass
    
    def is_saturated(self) -> bool:
        """Return True when no valid pixels remain."""
        return self.invalid_count >= self.total_pixels
    
    def reset(self) -> None:
        """Clear all invalid pixels."""
        self.invalid_bitmap = bytearray((self.total_pixels + 7) // 8)
        self.invalid_count = 0


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
        """Get all positions in the 9 surrounding grid cells."""
        cell = self._get_cell(x, y)
        neighbors = []
        # Check neighboring cells
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                check_cell = (cell[0] + dx, cell[1] + dy)
                if check_cell in self.grid:
                    neighbors.extend(self.grid[check_cell])
        return neighbors


class PlacementStrategy:
    def place(self, count: int, width: int, height: int, size: int) -> List[Tuple[float, float]]:
        raise NotImplementedError()


def create_validator_from_name(name: str, width: int, height: int, size: int) -> PlacementValidator:
    """Return a placement validator instance given a config name string.
    
    Available validators:
    - consecutive_failure (default): Fast, stops after 3 consecutive failed placements
    - pixel_density: Accurate pixel-level tracking, places ~10-15% more beans but slower
    """
    logger.info(f">>>>> create_validator_from_name: name={name}")
    match name.lower() if name else '':
        case 'consecutive_failure' | 'consecutive':
            logger.debug(">>>>> Creating ConsecutiveFailureValidator")
            return ConsecutiveFailureValidator(threshold=3)
        case 'pixel_density' | 'pixel':
            logger.debug(">>>>> Creating PixelDensityValidator")
            return PixelDensityValidator(width=width, height=height)
        case _:
            logger.debug(f">>>>> Unknown validator '{name}', defaulting to ConsecutiveFailureValidator")
            return ConsecutiveFailureValidator(threshold=3)


class RandomPlacementStrategy(PlacementStrategy):
    def __init__(self, max_retries: int = 50, validator_name: str = "consecutive_failure") -> None:
        self.max_retries = max_retries
        self.validator_name = validator_name

    def place(self, count: int, width: int, height: int, size: int) -> List[Tuple[float, float]]:
        logger.info(f">>>>> RandomPlacementStrategy.place: count={count}, width={width}, height={height}, size={size}")
        if count <= 0:
            logger.warning(">>>>> Count <= 0, returning empty list")
            return []
        
        positions: List[Tuple[float, float]] = []
        spatial_hash = SpatialHash(cell_size=size, width=width, height=height)
        validator = create_validator_from_name(self.validator_name, width, height, size)
        
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

def create_strategy_from_name(name: str, validator_name: str = "consecutive_failure") -> PlacementStrategy:
    """Return a placement strategy instance given a config name string."""
    logger.info(f">>>>> create_strategy_from_name: name={name}, validator_name={validator_name}")
    match name.lower() if name else '':
        case 'random':
            logger.debug(">>>>> Creating RandomPlacementStrategy")
            return RandomPlacementStrategy(validator_name=validator_name)
        case 'grid':
            logger.debug(">>>>> Creating GridPlacementStrategy")
            return GridPlacementStrategy()
        case 'clustered' | 'cluster':
            logger.debug(">>>>> Creating ClusteredPlacementStrategy")
            return ClusteredPlacementStrategy()
        case _:
            logger.debug(f">>>>> Unknown strategy '{name}', defaulting to RandomPlacementStrategy")
            return RandomPlacementStrategy(validator_name=validator_name)
