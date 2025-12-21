# 2025-12-21-food-rendering-diagram.md

```mermaid
graph TD
    A[WorldWindow.on_draw] --> B[_draw_food_items]
    B --> C{Iterate food_manager.grid}
    C -- FoodType.COMMON --> D[Draw food (common color)]
    C -- FoodType.DEAD_BEAN --> E[Draw food (dead bean color)]
    D --> F[Scale by value]
    E --> F
    F --> G[Render on window]
```

This diagram illustrates the rendering flow for food and dead bean food in the simulation window.
