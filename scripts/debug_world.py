from beans.world import World
from config.loader import BeansConfig, WorldConfig

world_cfg = WorldConfig(
    male_sprite_color="blue",
    female_sprite_color="red",
    male_female_ratio=1.0,
    width=100,
    height=100,
    population_density=0.01,
    placement_strategy="random",
    population_estimator="density",
)
beans_cfg = BeansConfig(speed_min=-5, speed_max=5, max_age_rounds=100, initial_energy=1.0, energy_gain_per_step=0.0, energy_cost_per_speed=10.0, initial_bean_size=5)

w = World(config=world_cfg, beans_config=beans_cfg)
print(f"Initial beans: {len(w.beans)}")
for i, b in enumerate(w.beans):
    print(f"Bean {i}: energy={b.energy:.3f}, speed={b.speed:.3f}, size={b.size:.3f}")

for step in range(1, 11):
    w.step(dt=1.0)
    print(f"After step {step}: beans={len(w.beans)}, dead={len(w.dead_beans)}")
    for i, b in enumerate(w.beans):
        print(f"  Alive {i}: energy={b.energy:.3f}, speed={b.speed:.3f}, size={b.size:.3f}")
    for rec in w.dead_beans:
        print(f"  Dead: id={rec.bean.id}, reason={rec.reason}, energy={rec.bean.energy:.3f}, size={rec.bean.size:.3f}")
