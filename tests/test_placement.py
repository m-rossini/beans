import random
import math
import logging
import pytest

from beans.placement import RandomPlacementStrategy, GridPlacementStrategy, ClusteredPlacementStrategy

logger = logging.getLogger(__name__)


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

def test_grid_placement_no_collisions():
    """Test that GridPlacementStrategy places beans without collisions"""
    strategy = GridPlacementStrategy()
    positions = strategy.place(20, width=200, height=200, size=20)
    
    # Verify all positions were placed
    assert len(positions) == 20
    
    # Verify no collisions
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            x1, y1 = positions[i]
            x2, y2 = positions[j]
            distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            assert distance >= 20, f"Collision at positions {i} and {j}: distance={distance}"


def test_grid_placement_collision_detection_90_percent_success():
    """Test that GridPlacementStrategy succeeds when 90% threshold can be met"""
    strategy = GridPlacementStrategy()
    requested = 50
    
    # Larger space allows 90% of 50 beans to fit comfortably
    positions = strategy.place(requested, width=400, height=400, size=15)
    
    # Should place at least 90%
    assert len(positions) >= requested * 0.9, f"Placed {len(positions)}, needed at least {requested * 0.9}"
    
    # Verify no collisions
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            x1, y1 = positions[i]
            x2, y2 = positions[j]
            distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            assert distance >= 15, f"Collision at positions {i} and {j}: distance={distance}"


def test_clustered_placement_no_collisions():
    """Test that ClusteredPlacementStrategy places beans without collisions"""
    random.seed(1)
    strategy = ClusteredPlacementStrategy()
    positions = strategy.place(20, width=200, height=200, size=20)
    
    # Verify all positions were placed
    assert len(positions) == 20
    
    # Verify no collisions
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            x1, y1 = positions[i]
            x2, y2 = positions[j]
            distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            assert distance >= 20, f"Collision at positions {i} and {j}: distance={distance}"


def test_clustered_placement_collision_detection_90_percent_success():
    """Test that ClusteredPlacementStrategy succeeds when 90% threshold can be met"""
    random.seed(1)
    strategy = ClusteredPlacementStrategy()
    requested = 50
    
    # Larger space allows 90% of 50 beans to fit comfortably
    positions = strategy.place(requested, width=400, height=400, size=15)
    
    # Should place at least 90%
    assert len(positions) >= requested * 0.9, f"Placed {len(positions)}, needed at least {requested * 0.9}"
    
    # Verify no collisions
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            x1, y1 = positions[i]
            x2, y2 = positions[j]
            distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            assert distance >= 15, f"Collision at positions {i} and {j}: distance={distance}"
