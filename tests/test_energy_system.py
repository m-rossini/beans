from beans.bean import Bean, Sex
from beans.energy_system import create_energy_system_from_name
from beans.genetics import Gene, Genotype, create_phenotype, create_random_genotype
from config.loader import BeansConfig


# Helper to set bean state via public API (used only to establish initial conditions)
def set_bean_state(bean: Bean, *, energy: float | None = None, size: float | None = None):
    """Create a BeanState from the bean, modify provided fields, and apply via update_from_state."""
    state = bean.to_state()
    state.store(
        age=state.age,
        speed=state.speed,
        energy=energy if energy is not None else state.energy,
        size=size if size is not None else state.size,
    )
    bean.update_from_state(state)


def make_test_config():
    return BeansConfig(
        speed_min=-5,
        speed_max=5,
        initial_energy=100.0,
        initial_bean_size=10,
        metabolism_base_burn=0.10,
        energy_cost_per_speed=0.5,
        energy_baseline=50.0,
        fat_gain_rate=0.1,
        energy_to_fat_ratio=1.0,
        fat_burn_rate=0.1,
        fat_to_energy_ratio=0.9,
        min_bean_size=3.0,
        max_bean_size=20.0,
        size_sigma_frac=0.15,
        size_penalty_above_k=0.20,
        size_penalty_min_above=0.3,
        size_penalty_below_k=0.15,
        size_penalty_min_below=0.4,
    )


def make_bean_with_genes(config: BeansConfig, *, energy: float | None = None, size: float = 10.0, speed: float = 3.0):
    genes = {
        Gene.METABOLISM_SPEED: 0.5,
        Gene.MAX_GENETIC_SPEED: 0.5,
        Gene.FAT_ACCUMULATION: 0.5,
        Gene.MAX_GENETIC_AGE: 0.5,
    }
    genotype = Genotype(genes=genes)
    phenotype = create_phenotype(config, genotype)
    phenotype.size = size
    phenotype.speed = speed
    bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=genotype, phenotype=phenotype)
    if energy is not None:
        set_bean_state(bean, energy=energy)
    return bean


def test_intake_increases_energy():
    config = make_test_config()
    energy_system = create_energy_system_from_name("standard", config)
    bean = make_bean_with_genes(config, energy=50.0)

    before = bean.energy
    state = energy_system.apply_energy_system(bean, energy_intake_eu=20.0)
    bean.update_from_state(state)
    assert bean.energy > before


def test_metabolism_reduces_energy_over_time():
    config = make_test_config()
    energy_system = create_energy_system_from_name("standard", config)
    # start with higher energy and no intake
    bean = make_bean_with_genes(config, energy=120.0)

    before = bean.energy
    for _ in range(5):
        state = energy_system.apply_energy_system(bean, energy_intake_eu=0.0)
        bean.update_from_state(state)
    assert bean.energy < before


def test_size_increases_when_energy_above_baseline():
    config = make_test_config()
    energy_system = create_energy_system_from_name("standard", config)
    bean = make_bean_with_genes(config, energy=config.energy_baseline + 20)

    size_before = bean.size
    state = energy_system.apply_energy_system(bean, energy_intake_eu=0.0)
    bean.update_from_state(state)
    assert bean.size >= size_before


def test_size_decreases_when_energy_below_baseline():
    config = make_test_config()
    energy_system = create_energy_system_from_name("standard", config)
    bean = make_bean_with_genes(config, energy=config.energy_baseline - 20)

    size_before = bean.size
    state = energy_system.apply_energy_system(bean, energy_intake_eu=0.0)
    bean.update_from_state(state)
    assert bean.size <= size_before


def test_size_clamping():
    config = make_test_config()
    energy_system = create_energy_system_from_name("standard", config)
    # too small
    bean = make_bean_with_genes(config, energy=50.0)
    set_bean_state(bean, size=1.0)
    state = energy_system.apply_energy_system(bean, energy_intake_eu=0.0)
    bean.update_from_state(state)
    assert bean.size >= config.min_bean_size

    # too large
    bean2 = make_bean_with_genes(config, energy=50.0)
    set_bean_state(bean2, size=50.0)
    state2 = energy_system.apply_energy_system(bean2, energy_intake_eu=0.0)
    bean2.update_from_state(state2)
    assert bean2.size <= config.max_bean_size


def test_survival_health_and_starvation():
    config = BeansConfig(
        speed_min=-5,
        speed_max=5,
        initial_energy=100.0,
        initial_bean_size=10,
        min_bean_size=3.0,
        max_bean_size=20.0,
    )
    energy_system = create_energy_system_from_name("standard", config)
    genotype = create_random_genotype()
    phenotype = create_phenotype(config, genotype)
    phenotype.size = 30.0  # Obese
    bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=genotype, phenotype=phenotype)
    set_bean_state(bean, energy=100.0)

    # Starvation survival (simulate low energy)
    set_bean_state(bean, energy=0.0)
    survived, reason = bean.survive()
    assert not survived
    assert reason == "energy_depleted"

    if hasattr(energy_system, "can_survive_starvation"):
        survived_starvation = energy_system.can_survive_starvation(bean)
        assert isinstance(survived_starvation, bool)
