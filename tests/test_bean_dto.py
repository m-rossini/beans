from beans.bean import Bean, BeanState
from beans.genetics import create_phenotype, create_random_genotype
from config.loader import BeansConfig


def test_bean_to_state():
    bcfg = BeansConfig(speed_min=-5, speed_max=5, initial_bean_size=10)
    genotype = create_random_genotype()
    phenotype = create_phenotype(bcfg, genotype)
    bean = Bean(
        config=bcfg,
        id=42,
        sex=__import__("beans").bean.Sex.MALE,
        genotype=genotype,
        phenotype=phenotype,
    )

    # Create a state from the bean twice
    state1 = bean.to_state()
    state2 = bean.to_state()
    assert isinstance(state1, BeanState)
    # Value equality should hold
    assert state1 == state2
    # Ensure fields match bean
    assert state1.id == bean.id
    assert state1.age == bean.age
    assert state1.energy == bean.energy


def test_bean_update_from_state():
    bcfg = BeansConfig(speed_min=-5, speed_max=5, initial_bean_size=10)
    genotype = create_random_genotype()
    phenotype = create_phenotype(bcfg, genotype)
    bean = Bean(
        config=bcfg,
        id=99,
        sex=__import__("beans").bean.Sex.FEMALE,
        genotype=genotype,
        phenotype=phenotype,
    )

    state = bean.to_state()
    state.store(age=5.0, speed=1.0, energy=12.0, size=8.0)
    bean.update_from_state(state)
    assert bean.age == 5.0
    assert bean.speed == 1.0
    assert bean.energy == 12.0
    assert bean.size == 8.0
