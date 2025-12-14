from __future__ import annotations

import random
from abc import ABC, abstractmethod
from typing import Iterable, List, Tuple, Any


class RandomnessProvider(ABC):
    @abstractmethod
    def random(self) -> float:
        ...

    @abstractmethod
    def randint(self, a: int, b: int) -> int:
        ...

    @abstractmethod
    def choice(self, seq: Iterable[Any]) -> Any:
        ...

    @abstractmethod
    def sample_positions(self, n: int, bounds: Tuple[float, float]) -> List[Tuple[float, float]]:
        ...

    # explicit-only: sequential retrieval
    def next_explicit(self) -> Any:  # default raises
        raise IndexError("No explicit values available")


class SystemRandomnessProvider(RandomnessProvider):
    def __init__(self) -> None:
        self._rng = random.Random()

    def random(self) -> float:
        return self._rng.random()

    def randint(self, a: int, b: int) -> int:
        return self._rng.randint(a, b)

    def choice(self, seq: Iterable[Any]) -> Any:
        seq = list(seq)
        return self._rng.choice(seq)

    def sample_positions(self, n: int, bounds: Tuple[float, float]) -> List[Tuple[float, float]]:
        w, h = bounds
        return [(self._rng.random() * w, self._rng.random() * h) for _ in range(n)]


class SeededRandomnessProvider(RandomnessProvider):
    def __init__(self, seed_or_rng: int | random.Random) -> None:
        if isinstance(seed_or_rng, random.Random):
            self._rng = seed_or_rng
        else:
            self._rng = random.Random(seed_or_rng)

    def random(self) -> float:
        return self._rng.random()

    def randint(self, a: int, b: int) -> int:
        return self._rng.randint(a, b)

    def choice(self, seq: Iterable[Any]) -> Any:
        seq = list(seq)
        return self._rng.choice(seq)

    def sample_positions(self, n: int, bounds: Tuple[float, float]) -> List[Tuple[float, float]]:
        w, h = bounds
        return [(self._rng.random() * w, self._rng.random() * h) for _ in range(n)]


class ExplicitProvider(RandomnessProvider):
    def __init__(self, values: Iterable[Any]) -> None:
        self._values = list(values)
        self._idx = 0

    def random(self) -> float:
        # Not meaningful for explicit; return fallback by raising
        raise IndexError("ExplicitProvider has no random values")

    def randint(self, a: int, b: int) -> int:
        raise IndexError("ExplicitProvider has no randint values")

    def choice(self, seq: Iterable[Any]) -> Any:
        raise IndexError("ExplicitProvider has no choice values")

    def sample_positions(self, n: int, bounds: Tuple[float, float]) -> List[Tuple[float, float]]:
        # If values are positions, return next n positions
        out: List[Tuple[float, float]] = []
        for _ in range(n):
            out.append(self.next_explicit())
        return out

    def next_explicit(self) -> Any:
        if self._idx >= len(self._values):
            raise IndexError("ExplicitProvider exhausted")
        v = self._values[self._idx]
        self._idx += 1
        return v
