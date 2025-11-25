import random

from beans.placement import RandomPlacementStrategy


def test_random_placement_reproducible_with_seed():
    random.seed(12345)
    strategy = RandomPlacementStrategy()
    positions1 = strategy.place(5, width=100, height=100, size=10)

    random.seed(12345)
    positions2 = strategy.place(5, width=100, height=100, size=10)

    assert positions1 == positions2


def test_random_placement_different_seeds_produces_different_positions():
    random.seed(1)
    strategy = RandomPlacementStrategy()
    positions1 = strategy.place(5, width=100, height=100, size=10)

    random.seed(2)
    positions2 = strategy.place(5, width=100, height=100, size=10)

    assert positions1 != positions2


def test_random_placement_zero_count_returns_empty():
    strategy = RandomPlacementStrategy()
    positions = strategy.place(0, width=100, height=100, size=10)
    assert positions == []


def test_random_placement_negative_count_returns_empty():
    strategy = RandomPlacementStrategy()
    positions = strategy.place(-5, width=100, height=100, size=10)
    assert positions == []
