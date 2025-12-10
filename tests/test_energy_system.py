from beans.bean import Bean, Sex
from beans.energy_system import create_energy_system_from_name
from beans.genetics import Gene, Genotype, create_phenotype, create_random_genotype
from config.loader import BeansConfig


# Helper to set bean state via public API
def set_bean_state(bean: Bean, *, energy: float | None = None, size: float | None = None):
    """Create a BeanState from the bean, modify provided fields, and apply via update_from_state."""
    state = bean.to_state()
    # Use store to set desired fields
    state.store(
        age=state.age,
        speed=state.speed,
        energy=energy if energy is not None else state.energy,
        size=size if size is not None else state.size,
    )
    bean.update_from_state(state)

# Whole-cycle and edge-case tests using only the public API
class TestEnergySystemWholeCycle:
    """Whole-cycle and edge-case tests for EnergySystem using only the public API."""

    def test_energy_cycle_intake_and_burn(self):
        """Bean energy increases with intake, then decreases due to metabolism and movement."""
        config = BeansConfig(
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
        energy_system = create_energy_system_from_name("standard", config)
        genes = {
            Gene.METABOLISM_SPEED: 0.5,
            Gene.MAX_GENETIC_SPEED: 0.5,
            Gene.FAT_ACCUMULATION: 0.5,
            Gene.MAX_GENETIC_AGE: 0.5,
        }
        genotype = Genotype(genes=genes)
        phenotype = create_phenotype(config, genotype)
        phenotype.size = 10.0
        phenotype.speed = 3.0
        bean = Bean(config=config, id=1, sex=Sex.MALE, genotype=genotype, phenotype=phenotype)
        # Set initial energy via public API
        set_bean_state(bean, energy=50.0)

        # Intake energy
        initial_energy = bean.energy
        energy_system.apply_energy_system(bean, energy_intake_eu=20.0)
        assert bean.energy > initial_energy

        # Simulate multiple cycles to trigger metabolism, movement, fat storage/burning
        for _ in range(5):
            energy_system.apply_energy_system(bean, energy_intake_eu=0.0)

        # Bean should have lost energy due to metabolism and movement
        assert bean.energy < initial_energy + 20.0

        # If energy > baseline, size should increase (fat storage)
        if bean.energy > config.energy_baseline:
            size_before = bean.size
            energy_system.apply_energy_system(bean, energy_intake_eu=0.0)
            assert bean.size >= size_before

        # If energy < baseline, size should decrease (fat burning)
        set_bean_state(bean, energy=30.0)
        size_before = bean.size
        energy_system.apply_energy_system(bean, energy_intake_eu=0.0)
        assert bean.size <= size_before

        # Clamp size edge cases
        set_bean_state(bean, size=1.0)
        energy_system.apply_energy_system(bean, energy_intake_eu=0.0)
        assert bean.size >= config.min_bean_size
        set_bean_state(bean, size=50.0)
        energy_system.apply_energy_system(bean, energy_intake_eu=0.0)
        assert bean.size <= config.max_bean_size

    def test_survival_health_and_starvation(self):
        """Test health and starvation survival via public API."""
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
        # Use bean's survive method to check survival
        survived, reason = bean.survive()
        assert not survived
        assert reason == "energy_depleted"

        # If public API exposes can_survive_starvation, test it
        if hasattr(energy_system, "can_survive_starvation"):
            survived_starvation = energy_system.can_survive_starvation(bean)
            assert isinstance(survived_starvation, bool)
