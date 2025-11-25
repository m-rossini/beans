# 2025-11-25 Population Estimation Refactor

## Context
Splitting the bean placement strategy from population estimation provides a clear separation of concerns and allows future experimentation with alternate estimation heuristics without touching placement behavior or world initialization logic.

## Decision
- Introduced a dedicated `PopulationEstimator` abstraction and `DensityPopulationEstimator`, moved the area-density math from the placement strategy into this new component, and added a factory to create estimators by name.
- `WorldConfig` now carries a `population_estimator` selector (defaulting to the density estimator) so `World` can keep the estimation step independent of the chosen placement strategy.
- Added `SoftLogPopulationEstimator`, which softly log-scales bean counts up to the density default, along with focused tests that prove the logarithmic growth and factory selection.
- Updated `World` and the tests to rely on the new estimator, keeping bean creation logic driven by estimator output while preserving existing ratio enforcement.

## Consequences
- Population estimation can now evolve independently from placement strategies, making alternative heuristics or data-driven estimators easy to plug in.
- Tests ensure the estimator contract stays stable, including guard rails for invalid inputs so we return zero-sized populations when the density math would compute zero or negative counts.

## Testing
- `make test-specific TEST_SPECIFIC=tests/test_population_estimation.py`

## Diagram
- [Population Estimation Overview](2025-11-25-population-estimation-diagram.md)
