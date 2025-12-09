# 2025-12-09-bean-dynamics-system.md

## ADR: BeanDynamics System Extraction and Integration

### Problem Statement
The bean movement logic was previously tightly coupled within the Bean class, making it difficult to configure, test, and extend. Movement parameters (speed, position, direction) needed to be decoupled and made configurable via BeansConfig, with all updates managed by a dedicated system.

### Decision
- Extracted a new `BeanDynamics` system in `src/beans/dynamics/bean_dynamics.py` to handle speed, position, and direction calculations for beans.
- Refactored `Bean` to delegate movement logic to `BeanDynamics`, using configuration values from BeansConfig.
- Integrated `BeanDynamics` into `World`, so movement updates are managed centrally during simulation steps.
- Updated configuration and validation to ensure all movement parameters are present and validated.
- Added and updated tests to cover BeanDynamics integration with Bean and World, following TDD.
- Documented all configuration parameters with one-line comments for clarity.

### Rationale
- Decoupling movement logic improves modularity, testability, and future extensibility.
- Centralizing movement updates in World enables more flexible simulation control and easier future enhancements.
- Configuration-driven design ensures all movement parameters are easily adjustable and validated.

### Consequences
- Bean movement logic is now fully decoupled and testable.
- All movement parameters are configurable and validated.
- Future enhancements (e.g., new movement strategies) can be added to BeanDynamics without modifying Bean or World.

### How to Run
- Run tests: `make test` or `pytest tests/test_bean_dynamics.py` and related integration tests.
- Run simulation: use `run_window.py` or main entry point as before.

### Diagram
See `2025-12-09-bean-dynamics-system-diagram.md` for a mermaid diagram of the new architecture.

---
