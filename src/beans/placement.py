from __future__ import annotations
from typing import List, Tuple
import random
import math


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
        positions: List[Tuple[float, float]] = []
        for _ in range(count):
            can_fit = self._can_fit(size, count, width, height)
            x = random.uniform(0, width)
            y = random.uniform(0, height)
            positions.append((x, y))
        return positions
    

class GridPlacementStrategy(PlacementStrategy):
    def __init__(self, packing_efficiency: float = 0.64) -> None:
        self.packing_efficiency = packing_efficiency 

    def place(self, count: int, width: int, height: int, size: int) -> List[Tuple[float, float]]:
        if count <= 0:
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
        return positions


class ClusteredPlacementStrategy(PlacementStrategy):
    def __init__(self, packing_efficiency: float = 0.55) -> None:
        self.packing_efficiency = packing_efficiency

    def place(self, count: int, width: int, height: int, size: int) -> List[Tuple[float, float]]:
        if count <= 0:
            return []
        clusters = max(1, count // 5)
        centers = [(random.uniform(0, width), random.uniform(0, height)) for _ in range(clusters)]
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

        return positions


def create_strategy_from_name(name: str) -> PlacementStrategy:
    """Return a placement strategy instance given a config name string."""
    match name.lower() if name else '':
        case 'random':
            return RandomPlacementStrategy()
        case 'grid':
            return GridPlacementStrategy()
        case 'clustered' | 'cluster':
            return ClusteredPlacementStrategy()
        case _:
            return RandomPlacementStrategy()
