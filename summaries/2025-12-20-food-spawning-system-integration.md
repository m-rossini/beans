# 2025-12-20-food-spawning-system-integration.md

## ADR: Food Spawning System Integration & Final Polish

### Context
The food spawning system was refactored to unify food and dead bean food into a single grid structure, with type-aware decay and cap logic. Dead bean food now ignores the cap and is spawned at the bean's last position and half its size at death, using sprite data from the rendering layer. A persistent `WorldState` object tracks alive and dead beans per step, decoupling simulation and rendering. All configuration files are clean, and the codebase inventory is up to date.

### Decision
- Unified food and dead bean grid with type-aware decay.
- Dead bean food cap is ignored; food is spawned at the correct position/size.
- Dead bean food logic is encapsulated as a private method in the rendering layer.
- Persistent `WorldState` is used for state tracking.
- No introspection is used for bean state/position.
- All new logic follows SOLID and modularity principles.
- All tests pass, and codebase inventory is current.

### Consequences
- Simulation and rendering are decoupled for dead bean food logic.
- State tracking is robust and efficient.
- Configuration and codebase are clean and production-ready.
- Ready for merge and review.

### How to Run
- Use `make test` to run all tests.
- Use `make coverage` for coverage report.
- Use `make` targets for linting and formatting as needed.

### Mermaid Diagram
See [2025-12-20-food-spawning-system-integration-diagram.md](2025-12-20-food-spawning-system-integration-diagram.md) for the architecture diagram.
