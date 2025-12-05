---
agent: agent
---
# Pluggable Energy System Specification (Bean Simulation)

---

## 1. Context & Scope

This specification defines a **pluggable Energy System module** responsible ONLY for:

- Energy intake
- Energy storage
- Fat accumulation
- Fat burning
- Metabolic cost
- Body size consequence

The Energy System **does not**:
- handle age (only comments where age is updated)
- change speed directly (only provides size penalty)
- make decisions
- read world state yet (defaults are used)
- update position or season effects

Each system (age, movement, energy, world) must remain independent.

---

## 2. System Philosophy

Principles:

1. **Energy is conserved logically** (fat is energy)
2. **Systems communicate through the Phenotype only**
3. **The world is optional** (defaults used if unavailable)
4. **Genes tune intensity, not structure**
5. **All rates are per tick**
6. **Energy handles size, speed reads size**
7. **Beans do not grow magically — everything is paid via energy**

---

## 3. Bean Update Order (Canonical)

This defines the engine loop.

```python
def update():
    self.update_age()         # NOT part of energy system
    self.update_speed()       # uses size penalty
    self.update_energy()      # THIS SYSTEM
    self.decide_actions()     # dummy for now
```

Age update done elsewhere:

```python
self.age += 1
```

---

## 4. Interfaces (Pluggable)

### Energy System Interface

```python
class EnergySystem:

    def apply_intake(self, bean, energy_eu: float) -> None:
        """
        Called when the bean eats.
        Directly increases circulating energy.
        """

    def update_energy(self, bean) -> dict:
        """
        Main per-tick method.
        Handles:
          - fat storage
          - fat burning
          - basal metabolism
          - size change
        Returns metrics dict for debugging and logging.
        """

    def size_speed_penalty(self, bean) -> float:
        """
        Returns size-based speed multiplier.
        Does not change speed. Caller applies multiplier.
        """

    def death_check(self, bean) -> bool:
        """
        Returns True if bean should die due to body failure.
        """
```

---

## 5. Phenotype Fields (REQUIRED)

Energy uses these exact names:

```python
phenotype.energy        # circulating energy
phenotype.size          # fat storage / body mass
phenotype.target_size   # ideal size (computed elsewhere)
phenotype.age           # not modified here
phenotype.speed         # only to compute movement cost
```

---

## 6. Genotype Fields (REQUIRED)

Energy depends on:

```python
gene[FAT_ACCUMULATION]
gene[METABOLISM_SPEED]
```

---

## 7. Configuration

```python
DEFAULT_ENERGY_INTAKE = 1.0
DEFAULT_TEMPERATURE   = 1.0

energy_baseline        = 50.0
energy_max_storage     = 200.0

fat_gain_rate          = 0.02
fat_burn_rate          = 0.02

metabolism_base_burn   = 0.01

energy_to_fat_ratio    = 1.0
fat_to_energy_ratio    = 0.9

min_bean_size          = 3.0
max_bean_size          = 18.0

movement_cost_per_speed = 0.1

size_sigma_frac = 0.15

size_penalty_above_k = 0.20
size_penalty_below_k = 0.15

size_penalty_min_above = 0.3
size_penalty_min_below = 0.4
```

---

## 8. Default Environment Inputs

```python
temperature = DEFAULT_TEMPERATURE
energy_input = DEFAULT_ENERGY_INTAKE
```

---

## 9. Core Energy Mechanics

### Intake

```python
phenotype.energy += energy_input
```

### Surplus → Fat Storage

```python
surplus = max(0, energy - energy_baseline)

fat_gain = fat_gain_rate * FAT_ACCUMULATION * surplus
energy -= fat_gain * energy_to_fat_ratio
size += fat_gain
```

### Deficit → Fat Burn

```python
deficit = max(0, energy_baseline - energy)

fat_burn = fat_burn_rate * (1.2 - FAT_ACCUMULATION) * deficit
energy += fat_burn * fat_to_energy_ratio
size -= fat_burn
```

### Basal Metabolism Burn

```python
burn = metabolism_base_burn * (1 + 0.5 * METABOLISM_SPEED) * size
energy -= burn

if energy < 0:
    fat = abs(energy) / fat_to_energy_ratio
    size -= fat
    energy = 0
```

### Movement Cost (Optional)

```python
movement_cost = abs(speed) * movement_cost_per_speed
energy -= movement_cost
```

### Size Clamp

```python
size = clamp(size, min_bean_size, max_bean_size)
```

---

## 10. Speed Penalty (Z-score)

```python
sigma = target_size * size_sigma_frac
z = (size - target_size) / sigma
```

```python
if z > 2:
    penalty = max(size_penalty_min_above, 1 - z * size_penalty_above_k)
elif z < -2:
    penalty = max(size_penalty_min_below, 1 + z * size_penalty_below_k)
else:
    penalty = 1.0
```

Speed application:

```python
speed *= penalty
```

---

## 11. Death Rules

```python
if size <= min_bean_size:
    die

if size > target_size * 2.5:
    ramp_probability()
```

---

