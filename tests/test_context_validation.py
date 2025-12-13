import random
import pytest

from beans.context import BeanContext


def test_bean_context_validation_passes_for_valid_counts():
    ctx = BeanContext(bean_count=5, male_count=2, rng=random.Random(42))
    assert ctx.bean_count == 5
    assert ctx.male_count == 2
    assert hasattr(ctx, "rng")


def test_bean_context_validation_fails_when_male_greater_than_bean_count():
    with pytest.raises(ValueError):
        _ = BeanContext(bean_count=3, male_count=4)


def test_bean_context_validation_fails_negative_count():
    with pytest.raises(ValueError):
        _ = BeanContext(bean_count=-1, male_count=0)
