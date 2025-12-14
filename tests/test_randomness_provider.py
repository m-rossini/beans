import random
import pytest

from beans.environment.randomness import SystemRandomnessProvider, SeededRandomnessProvider, ExplicitProvider


def test_seeded_provider_is_reproducible():
    p1 = SeededRandomnessProvider(42)
    p2 = SeededRandomnessProvider(42)

    # multiple draws should match across providers constructed with same seed
    vals1 = [p1.random() for _ in range(5)]
    vals2 = [p2.random() for _ in range(5)]
    assert vals1 == vals2

    ints1 = [p1.randint(0, 100) for _ in range(5)]
    ints2 = [p2.randint(0, 100) for _ in range(5)]
    assert ints1 == ints2


def test_system_provider_has_valid_api():
    p = SystemRandomnessProvider()
    r = p.random()
    assert 0.0 <= r < 1.0
    i = p.randint(1, 5)
    assert 1 <= i <= 5
    # sample positions returns correct count
    pos = p.sample_positions(3, (10, 20))
    assert len(pos) == 3
    for x, y in pos:
        assert 0 <= x < 10
        assert 0 <= y < 20


def test_explicit_provider_returns_values_in_order_and_raises_when_exhausted():
    seq = ["a", "b", "c"]
    p = ExplicitProvider(seq)
    assert p.next_explicit() == "a"
    assert p.next_explicit() == "b"
    assert p.next_explicit() == "c"
    with pytest.raises(IndexError):
        p.next_explicit()

    # explicit provider for positions
    pos_seq = [(1, 2), (3, 4)]
    ppos = ExplicitProvider(pos_seq)
    assert ppos.next_explicit() == (1, 2)
    assert ppos.next_explicit() == (3, 4)
    with pytest.raises(IndexError):
        ppos.next_explicit()
