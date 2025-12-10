import time

from beans.placement import RandomPlacementStrategy
from beans.population import DensityPopulationEstimator


def test_random_placement_performance_small_config():
    """Test placement performance with small.json config dimensions and population.
    
    small.json has: width=400, height=300, population_density=0.005
    This should result in approximately 6 beans (400*300*0.005 = 600 beans worth of space = ~6 at size 10)
    """
    # Config from small.json
    width = 400
    height = 300
    population_density = 0.005
    sprite_size = 10  # Default bean sprite size

    # Estimate population
    estimator = DensityPopulationEstimator()
    male_count, female_count = estimator.estimate(
        width=width,
        height=height,
        sprite_size=sprite_size,
        population_density=population_density,
        male_female_ratio=1.0
    )
    total_count = male_count + female_count

    # Create placement strategy and time it
    strategy = RandomPlacementStrategy()

    start_time = time.perf_counter()
    positions = strategy.place(total_count, width, height, sprite_size)
    end_time = time.perf_counter()

    elapsed_ms = (end_time - start_time) * 1000

    # Verify results
    assert len(positions) >= int(total_count * 0.9), f"Failed to place 90% of beans. Expected {total_count}, got {len(positions)}"

    # Log performance metrics
    print("\nPlacement Performance (small.json config):")
    print(f"  Dimensions: {width}x{height}")
    print(f"  Population density: {population_density}")
    print(f"  Beans placed: {len(positions)} / {total_count}")
    print(f"  Time: {elapsed_ms:.2f}ms")
    print(f"  Placement rate: {len(positions) / (elapsed_ms / 1000):.0f} beans/sec")


def test_random_placement_performance_medium_scale():
    """Test placement performance with larger population."""
    width = 800
    height = 600
    population_density = 0.02  # Denser population
    sprite_size = 8

    estimator = DensityPopulationEstimator()
    male_count, female_count = estimator.estimate(
        width=width,
        height=height,
        sprite_size=sprite_size,
        population_density=population_density,
        male_female_ratio=1.0
    )
    total_count = male_count + female_count

    strategy = RandomPlacementStrategy()

    start_time = time.perf_counter()
    positions = strategy.place(total_count, width, height, sprite_size)
    end_time = time.perf_counter()

    elapsed_ms = (end_time - start_time) * 1000

    assert len(positions) >= int(total_count * 0.9)

    print("\nPlacement Performance (medium scale):")
    print(f"  Dimensions: {width}x{height}")
    print(f"  Population density: {population_density}")
    print(f"  Beans placed: {len(positions)} / {total_count}")
    print(f"  Time: {elapsed_ms:.2f}ms")
    print(f"  Placement rate: {len(positions) / (elapsed_ms / 1000):.0f} beans/sec")


def test_random_placement_performance_large_scale():
    """Test placement performance with very large population."""
    width = 2000
    height = 1500
    population_density = 0.01
    sprite_size = 5

    estimator = DensityPopulationEstimator()
    male_count, female_count = estimator.estimate(
        width=width,
        height=height,
        sprite_size=sprite_size,
        population_density=population_density,
        male_female_ratio=1.0
    )
    total_count = male_count + female_count

    strategy = RandomPlacementStrategy()

    start_time = time.perf_counter()
    positions = strategy.place(total_count, width, height, sprite_size)
    end_time = time.perf_counter()

    elapsed_ms = (end_time - start_time) * 1000

    assert len(positions) >= int(total_count * 0.9)

    print("\nPlacement Performance (large scale):")
    print(f"  Dimensions: {width}x{height}")
    print(f"  Population density: {population_density}")
    print(f"  Beans placed: {len(positions)} / {total_count}")
    print(f"  Time: {elapsed_ms:.2f}ms")
    print(f"  Placement rate: {len(positions) / (elapsed_ms / 1000):.0f} beans/sec")
