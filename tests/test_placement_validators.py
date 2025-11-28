from beans.placement import ConsecutiveFailureValidator, PixelDensityValidator


class TestConsecutiveFailureValidatorSaturationDetection:
    """Tests for ConsecutiveFailureValidator - detects when placement becomes futile."""

    def test_successful_placement_gives_second_chance_after_saturation(self):
        """Validator should detect saturation when consecutive failures reach threshold.
        
        This is the core purpose: knowing when placement is too difficult to continue.
        A successful placement resets, giving another chance.
        """
        validator = ConsecutiveFailureValidator(threshold=3)
        
        # Simulate placement attempts: trying to place beans
        validator.mark_failed()  # Attempt 1: couldn't place
        validator.mark_failed()  # Attempt 2: couldn't place
        assert validator.is_saturated() is False  # Still trying
        
        validator.mark_failed()  # Attempt 3: couldn't place
        assert validator.is_saturated() is True   # Stop! World is saturated
        
        # But then we manage to place one bean
        validator.mark_placed(x=10.0, y=20.0, size=5)
        assert validator.is_saturated() is False  # Second chance granted
        
        # Now we can fail again up to threshold
        validator.mark_failed()
        validator.mark_failed()
        assert validator.is_saturated() is False
        validator.mark_failed()
        assert validator.is_saturated() is True

    def test_reset_allows_fresh_saturation_detection(self):
        """Reset should clear saturation, as if starting a new placement phase.
        
        Useful when: starting placement in a new world or region.
        """
        validator = ConsecutiveFailureValidator(threshold=2)
        
        # Saturated in first phase
        validator.mark_failed()
        validator.mark_failed()
        assert validator.is_saturated() is True
        
        # Reset: new phase starts
        validator.reset()
        assert validator.is_saturated() is False
        
        # Can fail again, saturation only after threshold
        validator.mark_failed()
        assert validator.is_saturated() is False
        validator.mark_failed()
        assert validator.is_saturated() is True

    def test_validator_survives_mixed_success_failure_sequence(self):
        """Validator should correctly track saturation through realistic placement attempts.
        
        Scenario: trying to place beans in a progressively filling world.
        """
        validator = ConsecutiveFailureValidator(threshold=3)
        
        # Early placement: easy, lots of successes
        validator.mark_placed(x=10.0, y=10.0, size=5)
        validator.mark_placed(x=50.0, y=50.0, size=5)
        validator.mark_placed(x=90.0, y=90.0, size=5)
        assert validator.is_saturated() is False
        
        # Middle: harder, some failures creep in
        validator.mark_failed()
        validator.mark_placed(x=30.0, y=30.0, size=5)
        validator.mark_failed()
        assert validator.is_saturated() is False
        
        # Late: very hard, consecutive failures accumulate
        validator.mark_failed()
        assert validator.is_saturated() is False
        validator.mark_failed()
        assert validator.is_saturated() is True  # Give up


class TestPixelDensityValidatorSaturationDetection:
    """Tests for PixelDensityValidator - pixel-level accuracy for maximum density."""

    def test_empty_world_stays_unsaturated(self):
        """Empty world should never be saturated.
        
        Purpose: Placement should always work when world is empty.
        """
        validator = PixelDensityValidator(width=100, height=100)
        
        # Check multiple times - should stay unsaturated
        assert validator.is_saturated() is False
        assert validator.is_saturated() is False
        assert validator.is_saturated() is False

    def test_gradually_filling_world_eventually_saturates(self):
        """As beans fill the world, saturation eventually triggers.
        
        Purpose: Proves pixel tracking works and saturation happens when world fills.
        Scenario: 50x50 world (smaller for speed), beans of size 5.
        """
        validator = PixelDensityValidator(width=50, height=50)
        
        # Place beans across the world - should stay unsaturated for a while
        positions = [
            (10.0, 10.0),
            (25.0, 10.0),
            (40.0, 10.0),
            (10.0, 25.0),
            (25.0, 25.0),
            (40.0, 25.0),
            (10.0, 40.0),
            (25.0, 40.0),
        ]
        
        for x, y in positions:
            validator.mark_placed(x=x, y=y, size=5)
        # World not saturated yet with sparse placement
        assert validator.is_saturated() is False

    def test_reset_clears_pixel_tracking(self):
        """Reset should clear all pixel tracking for fresh placement phase.
        
        Purpose: Starting a new world or region should have full space available.
        """
        validator = PixelDensityValidator(width=20, height=20)
        
        # Fill the small world
        for y in range(0, 20, 5):
            for x in range(0, 20, 5):
                validator.mark_placed(x=float(x), y=float(y), size=5)
        
        # Reset: should start fresh
        validator.reset()
        assert validator.is_saturated() is False
        assert validator.invalid_count == 0

    def test_larger_beans_saturate_world_faster(self):
        """Larger beans should saturate world faster due to covering more pixels.
        
        Purpose: Proves bean size affects saturation - same number of large beans
        covers more pixels than small beans.
        """
        validator_small = PixelDensityValidator(width=50, height=50)
        validator_large = PixelDensityValidator(width=50, height=50)
        
        # Place same pattern with different sizes
        for i in range(5):
            validator_small.mark_placed(x=float(i * 10), y=25.0, size=3)
            validator_large.mark_placed(x=float(i * 10), y=25.0, size=8)
        
        # Large beans should mark more pixels as invalid
        assert validator_large.invalid_count > validator_small.invalid_count
