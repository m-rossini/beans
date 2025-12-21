# 2025-12-21-food-rendering-adr.md

## Title
Food and Dead Bean Food Rendering in Simulation Window

## Status
Accepted

## Context
Previously, food and dead bean food items were not visible in the simulation window, despite being present in the simulation state. This led to confusion and made it difficult to visually track food consumption and bean death events.

## Decision
- Implemented rendering logic in the `WorldWindow` class to display both food and dead bean food.
- Used the `FoodType` enum to distinguish between food types, ensuring type safety and correct color assignment.
- The rendering method iterates over the food grid, drawing each item with the appropriate color and scaling based on its type and value.
- All changes were made following strict TDD, with high-level tests verifying correct rendering and type usage.

## Consequences
- Food and dead bean food are now clearly visible in the simulation window, improving simulation transparency and debugging.
- The use of enums and type-safe checks reduces the risk of rendering bugs due to type mismatches.
- The solution is modular and testable, with rendering logic encapsulated in a private method.

## How to Run
- Run the simulation as usual; food and dead bean food will be rendered automatically.
- To test, use `make test` to ensure all rendering and food management tests pass.

## Diagram
See [2025-12-21-food-rendering-diagram.md](2025-12-21-food-rendering-diagram.md) for a mermaid diagram of the rendering flow.
