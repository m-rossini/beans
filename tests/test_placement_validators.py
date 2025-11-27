import pytest
from beans.placement import ConsecutiveFailureValidator


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
