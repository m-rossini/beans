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
    print(f"\nPlacement Performance (small.json config):")
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
    
    print(f"\nPlacement Performance (medium scale):")
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
    
    print(f"\nPlacement Performance (large scale):")
    print(f"  Dimensions: {width}x{height}")
    print(f"  Population density: {population_density}")
    print(f"  Beans placed: {len(positions)} / {total_count}")
    print(f"  Time: {elapsed_ms:.2f}ms")
    print(f"  Placement rate: {len(positions) / (elapsed_ms / 1000):.0f} beans/sec")


def test_validator_comparison_consecutive_failure():
    """Test placement with consecutive_failure validator using large.json config.
    
    Uses: width=1600, height=1200, population_density=0.4, sprite_size=5
    This test uses the consecutive_failure validator to see how many beans can be placed.
    """
    width = 1600
    height = 1200
    population_density = 0.4
    sprite_size = 5
    
    from beans.population import DensityPopulationEstimator
    estimator = DensityPopulationEstimator()
    male_count, female_count = estimator.estimate(
        width=width,
        height=height,
        sprite_size=sprite_size,
        population_density=population_density,
        male_female_ratio=1.0
    )
    total_count = male_count + female_count
    
    strategy = RandomPlacementStrategy(validator_name="consecutive_failure")
    
    start_time = time.perf_counter()
    positions = strategy.place(total_count, width, height, sprite_size)
    end_time = time.perf_counter()
    
    elapsed_ms = (end_time - start_time) * 1000
    placement_rate = len(positions) / total_count * 100
    
    print(f"\n{'='*60}")
    print(f"VALIDATOR COMPARISON: consecutive_failure")
    print(f"{'='*60}")
    print(f"  Config: large.json dimensions (1600x1200)")
    print(f"  Population density: {population_density}")
    print(f"  Sprite size: {sprite_size}")
    print(f"  Requested beans: {total_count}")
    print(f"  Beans placed: {len(positions)}")
    print(f"  Placement rate: {placement_rate:.1f}%")
    print(f"  Time: {elapsed_ms:.2f}ms")
    print(f"{'='*60}")
    
    # No assertion on minimum - we want to see the actual result
    assert len(positions) > 0, "Should place at least some beans"


def test_validator_comparison_pixel_density():
    """Test placement with pixel_density validator using large.json config.
    
    Uses: width=1600, height=1200, population_density=0.4, sprite_size=5
    This test uses the pixel_density validator to see how many beans can be placed.
    Note: pixel_density is slower but places ~10-15% more beans at high density.
    """
    width = 1600
    height = 1200
    population_density = 0.4
    sprite_size = 5
    
    from beans.population import DensityPopulationEstimator
    estimator = DensityPopulationEstimator()
    male_count, female_count = estimator.estimate(
        width=width,
        height=height,
        sprite_size=sprite_size,
        population_density=population_density,
        male_female_ratio=1.0
    )
    total_count = male_count + female_count
    
    strategy = RandomPlacementStrategy(validator_name="pixel_density")
    
    start_time = time.perf_counter()
    positions = strategy.place(total_count, width, height, sprite_size)
    end_time = time.perf_counter()
    
    elapsed_ms = (end_time - start_time) * 1000
    placement_rate = len(positions) / total_count * 100
    
    print(f"\n{'='*60}")
    print(f"VALIDATOR COMPARISON: pixel_density")
    print(f"{'='*60}")
    print(f"  Config: large.json dimensions (1600x1200)")
    print(f"  Population density: {population_density}")
    print(f"  Sprite size: {sprite_size}")
    print(f"  Requested beans: {total_count}")
    print(f"  Beans placed: {len(positions)}")
    print(f"  Placement rate: {placement_rate:.1f}%")
    print(f"  Time: {elapsed_ms:.2f}ms")
    print(f"{'='*60}")
    
    # No assertion on minimum - we want to see the actual result
    assert len(positions) > 0, "Should place at least some beans"


def test_validator_comparison_all_high_density():
    """Compare both validators at high density (0.7) to see which places more beans.
    
    This is the key comparison test showing the trade-offs between validators:
    - consecutive_failure: Fast, good placement rate
    - pixel_density: Slower but places ~10-15% more beans
    """
    width = 1600
    height = 1200
    population_density = 0.7
    sprite_size = 5
    
    from beans.population import DensityPopulationEstimator
    estimator = DensityPopulationEstimator()
    male_count, female_count = estimator.estimate(
        width=width,
        height=height,
        sprite_size=sprite_size,
        population_density=population_density,
        male_female_ratio=1.0
    )
    total_count = male_count + female_count
    
    validators = ["consecutive_failure", "pixel_density"]
    results = []
    
    print(f"\n{'='*70}")
    print(f"VALIDATOR COMPARISON AT HIGH DENSITY (0.7)")
    print(f"{'='*70}")
    print(f"Config: {width}x{height}, density={population_density}, sprite_size={sprite_size}")
    print(f"Requested beans: {total_count}")
    print(f"{'='*70}")
    
    for validator_name in validators:
        strategy = RandomPlacementStrategy(validator_name=validator_name)
        
        start_time = time.perf_counter()
        positions = strategy.place(total_count, width, height, sprite_size)
        end_time = time.perf_counter()
        
        elapsed_ms = (end_time - start_time) * 1000
        placement_pct = len(positions) / total_count * 100
        
        results.append({
            "validator": validator_name,
            "placed": len(positions),
            "pct": placement_pct,
            "time_ms": elapsed_ms
        })
        
        print(f"{validator_name:25} | {len(positions):6} beans ({placement_pct:5.1f}%) | {elapsed_ms:7.0f}ms")
    
    print(f"{'='*70}")
    
    # Find the winner
    best = max(results, key=lambda r: r["placed"])
    print(f"WINNER: {best['validator']} with {best['placed']} beans ({best['pct']:.1f}%)")
    print(f"{'='*70}")
    
    # All validators should place at least some beans
    for r in results:
        assert r["placed"] > 0, f"{r['validator']} should place at least some beans"
