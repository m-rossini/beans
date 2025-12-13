from config.loader import DEFAULT_WORLD_CONFIG, DEFAULT_BEANS_CONFIG
from beans.world import World

# Create a small world and run a few steps, printing bean speeds
world = World(DEFAULT_WORLD_CONFIG, DEFAULT_BEANS_CONFIG)
print(f"Initial beans: {len(world.beans)}")
for r in range(3):
    print(f"--- Round {r+1} ---")
    for bean in list(world.beans):
        state = world._update_bean(bean)
        print(f"Bean {bean.id}: age={state.age}, speed={state.speed:.3f}, energy={state.energy:.3f}, size={state.size:.3f}")
    # call update on beans to increment ages and apply survive logic
    world.step(1.0)
