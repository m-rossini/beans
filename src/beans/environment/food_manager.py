from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Set, Tuple

from config.loader import EnvironmentConfig


@dataclass
class FoodManager:
    """Manages food items on a coarse grid.

    - Grid size is derived from world width/height and the configured cell size.
    - Initial population is calculated from `food_density` (fraction of cells occupied).
    - Each `step()` spawns new food deterministically using a fractional accumulator
      based on `food_spawn_rate_per_round`.
    """

    env_config: EnvironmentConfig
    width: int
    height: int
    rng: Optional[object] = None

    def __post_init__(self) -> None:
        cell = self.env_config.cell_size
        self._cells_x = max(1, self.width // cell)
        self._cells_y = max(1, self.height // cell)
        self._num_cells = self._cells_x * self._cells_y
        self._cells: Set[Tuple[int, int]] = set()
        self._spawn_acc = 0.0

        initial = int(self._num_cells * self.env_config.food_density)
        for i in range(initial):
            x = i % self._cells_x
            y = i // self._cells_x
            self._cells.add((x, y))

    @property
    def food_count(self) -> int:
        return len(self._cells)

    def step(self) -> None:
        to_add_f = self.env_config.food_spawn_rate_per_round * self._num_cells
        self._spawn_acc += to_add_f
        to_add = int(self._spawn_acc)
        if to_add <= 0:
            return None
        self._spawn_acc -= to_add

        added = 0
        for y in range(self._cells_y):
            for x in range(self._cells_x):
                if (x, y) not in self._cells:
                    self._cells.add((x, y))
                    added += 1
                    if added >= to_add:
                        return None

    def consume(self, cell_x: int, cell_y: int) -> bool:
        """Consume food at the given cell coordinates; return True if consumed."""
        if (cell_x, cell_y) in self._cells:
            self._cells.remove((cell_x, cell_y))
            return True
        return False

    def has_food_at(self, cell_x: int, cell_y: int) -> bool:
        return (cell_x, cell_y) in self._cells
