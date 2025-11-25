from __future__ import annotations
from typing import List, Tuple
import random
import math
import logging

logger = logging.getLogger(__name__)


class PlacementStrategy:
    def place(self, count: int, width: int, height: int, size: int) -> List[Tuple[float, float]]:
        raise NotImplementedError()
    
    def _can_fit(self, size: int, count: int, width: int, height: int) -> bool:
        effective_diameter = size + 2  # diameter + 1px on each side
        area_per_sprite = math.pi * ( (effective_diameter/2) * (effective_diameter/2))
        total_area_needed = count * area_per_sprite
        available_area = width * height
        return total_area_needed <= (available_area * self.packing_efficiency)


class RandomPlacementStrategy(PlacementStrategy):
    def __init__(self, packing_efficiency: float = 0.45) -> None:
        self.packing_efficiency = packing_efficiency

    def place(self, count: int, width: int, height: int, size: int) -> List[Tuple[float, float]]:
        logger.debug(f">>>>> RandomPlacementStrategy.place: count={count}, width={width}, height={height}, size={size}")
        positions: List[Tuple[float, float]] = []
        for _ in range(count):
            can_fit = self._can_fit(size, count, width, height)
            x = random.uniform(0, width)
            y = random.uniform(0, height)
            positions.append((x, y))
        logger.debug(f">>>>> Generated {len(positions)} positions")
        return positions
    

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
                can_fit = self._can_fit(size, count, width, height)
                if len(positions) >= count:
                    break
                x = (c + 0.5) * size
                y = (r + 0.5) * size
                positions.append((x, y))
            if len(positions) >= count:
                break
        logger.info(f">>>>> Generated {len(positions)} positions")
        return positions


class ClusteredPlacementStrategy(PlacementStrategy):
    def __init__(self, packing_efficiency: float = 0.55) -> None:
        self.packing_efficiency = packing_efficiency

    def place(self, count: int, width: int, height: int, size: int) -> List[Tuple[float, float]]:
        logger.info(f">>>>> ClusteredPlacementStrategy.place: count={count}, width={width}, height={height}, size={size}")
        if count <= 0:
            logger.warning(">>>>> Count <= 0, returning empty list")
            return []
        clusters = max(1, count // 5)
        centers = [(random.uniform(0, width), random.uniform(0, height)) for _ in range(clusters)]
        logger.debug(f">>>>> Created {clusters} cluster centers")
        positions: List[Tuple[float, float]] = []
        for i in range(count):
            can_fit = self._can_fit(size, count, width, height)
            center = centers[i % clusters]
            angle = random.random() * 2 * math.pi
            radius = random.random() * (size * 2)
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            x = max(0.0, min(float(width), x))
            y = max(0.0, min(float(height), y))
            positions.append((x, y))
        logger.info(f">>>>> Generated {len(positions)} positions")
        return positions


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
