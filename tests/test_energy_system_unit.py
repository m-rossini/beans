from beans.bean import Bean, Sex
from beans.energy_system import create_energy_system_from_name
from beans.genetics import Gene, Genotype, create_phenotype_from_values
from config.loader import BeansConfig

# Minimal helpers copied from existing tests for deterministic creation


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


def make_bean_with_genes(
    config: BeansConfig,
    *,
    energy: float | None = None,
    size: float = 10.0,
    speed: float = 3.0,
):
    """Create a bean deterministically using explicit genotype and phenotype values.

    Uses `create_phenotype_from_values` to avoid RNG-based variations and ensure
    tests are deterministic.
    """
    genes = {
        Gene.METABOLISM_SPEED: 0.5,
        Gene.MAX_GENETIC_SPEED: 0.5,
        Gene.FAT_ACCUMULATION: 0.5,
        Gene.MAX_GENETIC_AGE: 0.5,
    }
    genotype = Genotype(genes=genes)
    # Determine deterministic energy value
    energy_val = energy if energy is not None else config.initial_energy
    phenotype = create_phenotype_from_values(
        config,
        genotype,
        age=0.0,
        speed=float(speed),
        energy=float(energy_val),
        size=float(size),
        target_size=float(size),
    )
    bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=genotype, phenotype=phenotype)
    return bean


def test_apply_energy_returns_state_and_does_not_mutate_bean():
    config = make_test_config()
    energy_system = create_energy_system_from_name("standard", config)
    bean = make_bean_with_genes(config, energy=50.0)

    before = bean.energy
    state = energy_system.apply_energy_system(bean, energy_intake_eu=20.0)
    assert state.energy > before
    assert bean.energy == before


def test_intake_changes_returned_state_but_not_bean():
    config = make_test_config()
    energy_system = create_energy_system_from_name("standard", config)
    bean = make_bean_with_genes(config, energy=50.0)

    before = bean.energy
    state = energy_system.apply_energy_system(bean, energy_intake_eu=20.0)
    assert state.energy > before
    assert bean.energy == before


def test_metabolism_reduces_returned_energy_over_time():
    config = make_test_config()
    energy_system = create_energy_system_from_name("standard", config)
    bean = make_bean_with_genes(config, energy=120.0)

    prev = bean.energy
    for _ in range(5):
        state = energy_system.apply_energy_system(bean, energy_intake_eu=0.0)
        assert state.energy <= prev
        prev = state.energy
    assert bean.energy == 120.0


def test_size_clamping_on_returned_state():
    config = make_test_config()
    energy_system = create_energy_system_from_name("standard", config)

    bean = make_bean_with_genes(config, energy=50.0)
    # set bean to be too small via state
    state0 = bean.to_state()
    state0.store(size=1.0)
    bean.update_from_state(state0)

    state = energy_system.apply_energy_system(bean, energy_intake_eu=0.0)
    assert state.size >= config.min_bean_size
    # original bean remains at size 1.0 until update_from_state is called
    assert bean.size == 1.0
