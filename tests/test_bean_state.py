import pytest

from beans.bean import BeanState


def test_beanstate_init_and_reset():
    # Initialize a bean state
    state = BeanState(
        id=1, age=2.0, speed=3.0, energy=4.0, size=5.0, target_size=5.0, alive=True
    )
    assert state.id == 1
    assert state.age == 2.0
    assert state.speed == 3.0
    assert state.energy == 4.0
    assert state.size == 5.0

    # Reuse the same BeanState via `store` to ensure public API for reuse
    state.store(age=1.0, speed=1.5, energy=2.5, size=6.0)
    assert state.id == 1
    assert state.age == 1.0
    assert state.speed == 1.5
    assert state.energy == 2.5
    assert state.size == 6.0


def test_beanstate_id_is_immutable():
    state = BeanState(
        id=1, age=0.0, speed=0.0, energy=0.0, size=1.0, target_size=1.0, alive=True
    )
    with pytest.raises(AttributeError):
        state.id = 2


def test_beanstate_partial_store_updates_only_informed_fields():
    state = BeanState(
        id=10, age=1.0, speed=2.0, energy=3.0, size=4.0, target_size=4.0, alive=True
    )
    state.store(age=5.0, energy=9.5)
    assert state.id == 10
    assert state.age == 5.0
    assert state.speed == 2.0  # unchanged
    assert state.energy == 9.5
    assert state.size == 4.0  # unchanged
