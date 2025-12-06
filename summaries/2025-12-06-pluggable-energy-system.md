# 2025-12-06 Pluggable Energy System

## Context

The simulation needed a comprehensive energy system that handles metabolism, fat storage/burning, size consequences, and survival mechanics. The system needed to be:
- Config-driven and pluggable (swappable implementations)
- Owned by World (not Bean) to follow the "World as physics engine" pattern
- Tested via interface behavior, not implementation details

## Decision

### Architecture

**World owns EnergySystem**: The `World` class creates and owns the `EnergySystem` instance, orchestrating energy operations during `step()`. Bean is a pure data entity with no energy system reference.

**Config-driven factory**: Energy system type is specified in `WorldConfig.energy_system` (default: `"standard"`). The factory function `create_energy_system_from_name()` instantiates the appropriate implementation.

**Abstract interface + concrete implementation**: `EnergySystem` is an ABC defining the contract. `StandardEnergySystem` provides the default implementation.

### EnergySystem Interface

```python
class EnergySystem(ABC):
    def apply_intake(bean, energy_eu) -> None
    def apply_basal_metabolism(bean) -> None
    def apply_movement_cost(bean) -> None
    def apply_fat_storage(bean) -> None
    def apply_fat_burning(bean) -> None
    def handle_negative_energy(bean) -> None
    def clamp_size(bean) -> None
    def size_speed_penalty(bean) -> float
    def can_survive_starvation(bean) -> bool
    def can_survive_health(bean) -> bool
```

### Configuration Fields (BeansConfig)

| Field | Default | Purpose |
|-------|---------|---------|
| `fat_gain_rate` | 0.02 | Rate of fat storage from surplus energy |
| `fat_burn_rate` | 0.02 | Rate of fat burning from energy deficit |
| `metabolism_base_burn` | 0.01 | Basal metabolism burn rate per tick |
| `energy_to_fat_ratio` | 1.0 | Energy consumed per fat unit stored |
| `fat_to_energy_ratio` | 0.9 | Energy recovered per fat unit burned |
| `energy_max_storage` | 200.0 | Maximum circulating energy storage |
| `energy_baseline` | 50.0 | Neutral metabolism line |
| `size_sigma_frac` | 0.15 | Sigma fraction for z-score calculation |
| `size_penalty_above_k` | 0.20 | Penalty factor when overweight |
| `size_penalty_below_k` | 0.15 | Penalty factor when underweight |
| `size_penalty_min_above` | 0.3 | Minimum speed multiplier when overweight |
| `size_penalty_min_below` | 0.4 | Minimum speed multiplier when underweight |

### World Orchestration

```python
# World.step() orchestrates the update loop
for bean in self.beans:
    self._update_bean(bean)      # Energy system operations
    bean.update(dt)              # Age increment only
    alive, reason = bean.survive()
    # ... handle death/survival

# World._update_bean() applies energy mechanics
def _update_bean(self, bean: Bean) -> None:
    self.energy_system.apply_basal_metabolism(bean)
    self.energy_system.apply_movement_cost(bean)
```

### Key Formulas

- **Basal metabolism**: `burn = metabolism_base_burn * (1 + 0.5 * METABOLISM_SPEED) * size`
- **Movement cost**: `cost = abs(speed) * energy_cost_per_speed`
- **Fat storage**: `fat_gain = fat_gain_rate * FAT_ACCUMULATION * surplus`
- **Fat burning**: `fat_burned = fat_burn_rate * FAT_ACCUMULATION * deficit`
- **Size speed penalty**: Z-score based exponential decay when outside ±2σ of target size
- **Starvation**: Death when `size <= min_bean_size`
- **Obesity**: Probabilistic death when `size > target_size * 2.5`

## Consequences

- **Modularity**: New energy systems can be added by implementing `EnergySystem` ABC and registering in factory
- **Testability**: Tests verify interface behavior, not implementation—swapping implementations doesn't break tests
- **Separation of concerns**: World orchestrates physics, Bean holds data, EnergySystem encapsulates energy logic
- **Configuration flexibility**: All energy parameters tunable via JSON config files

## Testing

```bash
make test-specific TEST_SPECIFIC=tests/test_energy_system.py
make test
```

All 136 tests pass.

## Diagram

See [2025-12-06-pluggable-energy-system-diagram.md](2025-12-06-pluggable-energy-system-diagram.md)
