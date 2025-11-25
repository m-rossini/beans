import random
import math
import logging
import pytest

from beans.placement import RandomPlacementStrategy

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


def test_random_placement_no_collisions():
    """Test that no two beans are placed closer than size distance"""
    random.seed(1)  # Use a seed that would cause collisions without collision detection
    strategy = RandomPlacementStrategy()
    positions = strategy.place(20, width=200, height=200, size=20)
    
    # Check all pairs of positions
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            x1, y1 = positions[i]
            x2, y2 = positions[j]
            distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            assert distance >= 20, f"Beans at positions {positions[i]} and {positions[j]} collide (distance: {distance})"


def test_random_placement_collision_detection_90_percent_threshold():
    """Test that placement fails when unable to meet 90% threshold in tight space"""
    strategy = RandomPlacementStrategy()
    requested = 50
    
    # Space too tight to place 90% of 50 beans (size 15 each) in 100x100
    # This should fail and raise SystemExit
    with pytest.raises(SystemExit):
        strategy.place(requested, width=100, height=100, size=15)


def test_random_placement_collision_detection_90_percent_success():
    """Test that placement succeeds when 90% threshold can be met"""
    random.seed(1)
    strategy = RandomPlacementStrategy()
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
