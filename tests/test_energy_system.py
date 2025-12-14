from beans.bean import Bean, Sex
from beans.energy_system import create_energy_system_from_name
from beans.genetics import Gene, Genotype, create_phenotype_from_values, create_random_genotype
from config.loader import BeansConfig


# Note: Tests should not call update_from_state directly; create deterministic
# beans via `make_bean_with_genes` instead (it uses `create_phenotype_from_values`).


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
    """Deterministic bean factory using explicit genotype and phenotype values.

    If `energy` is provided, it will be embedded into the phenotype at
    construction time (avoids calling update_from_state from tests).
    """
    genes = {
        Gene.METABOLISM_SPEED: 0.5,
        Gene.MAX_GENETIC_SPEED: 0.5,
        Gene.FAT_ACCUMULATION: 0.5,
        Gene.MAX_GENETIC_AGE: 0.5,
    }
    genotype = Genotype(genes=genes)
    energy_val = float(energy) if energy is not None else float(config.initial_energy)
    phenotype = create_phenotype_from_values(
        config, genotype, age=0.0, speed=float(speed), energy=energy_val, size=float(size), target_size=float(size)
    )
    bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=genotype, phenotype=phenotype)
    return bean


def test_intake_increases_energy():
    config = make_test_config()
    energy_system = create_energy_system_from_name("standard", config)
    bean = make_bean_with_genes(config, energy=50.0)

    before = bean.energy
    state = energy_system.apply_energy_system(bean, energy_intake_eu=20.0)
    # returned state should reflect increased energy and original bean should be unchanged
    assert state.energy > before
    assert bean.energy == before


def test_metabolism_reduces_energy_over_time():
    config = make_test_config()
    energy_system = create_energy_system_from_name("standard", config)
    # start with higher energy and no intake
    bean = make_bean_with_genes(config, energy=120.0)

    prev = bean.energy
    for _ in range(5):
        state = energy_system.apply_energy_system(bean, energy_intake_eu=0.0)
        assert state.energy <= prev
        prev = state.energy
    # original bean remains unchanged
    assert bean.energy == 120.0


def test_size_increases_when_energy_above_baseline():
    config = make_test_config()
    energy_system = create_energy_system_from_name("standard", config)
    bean = make_bean_with_genes(config, energy=config.energy_baseline + 20)

    size_before = bean.size
    state = energy_system.apply_energy_system(bean, energy_intake_eu=0.0)
    assert state.size >= size_before
    assert bean.size == size_before


def test_size_decreases_when_energy_below_baseline():
    config = make_test_config()
    energy_system = create_energy_system_from_name("standard", config)
    bean = make_bean_with_genes(config, energy=config.energy_baseline - 20)

    size_before = bean.size
    state = energy_system.apply_energy_system(bean, energy_intake_eu=0.0)
    assert state.size <= size_before
    assert bean.size == size_before


def test_size_clamping():
    config = make_test_config()
    energy_system = create_energy_system_from_name("standard", config)
    # too small (create bean already at small size)
    bean = make_bean_with_genes(config, energy=50.0, size=1.0)
    state = energy_system.apply_energy_system(bean, energy_intake_eu=0.0)
    # the returned state should be clamped; original bean still holds the old size
    assert state.size >= config.min_bean_size
    assert bean.size == 1.0

    # too large
    bean2 = make_bean_with_genes(config, energy=50.0, size=50.0)
    state2 = energy_system.apply_energy_system(bean2, energy_intake_eu=0.0)
    assert state2.size <= config.max_bean_size
    assert bean2.size == 50.0


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
    phenotype = create_phenotype_from_values(config, genotype, age=0.0, speed=0.0, energy=100.0, size=10.0, target_size=10.0)
    phenotype.size = 30.0  # Obese
    # Create bean already at zero energy to test immediate starvation behavior
    bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=genotype, phenotype=create_phenotype_from_values(config, genotype, age=0.0, speed=0.0, energy=0.0, size=30.0, target_size=10.0))
    survived, reason = bean.survive()
    assert not survived
    assert reason == "energy_depleted"
