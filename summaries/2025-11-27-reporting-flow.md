# Reporting Flow Update

## Overview
- Added a dedicated `reporting` package that owns the `SimulationReport` interface and the default `ConsoleSimulationReport` implementation.
- Updated `WorldWindow` to accept injected reporters, defaulting to the console report, and invoke them when the zero-bean prompt is confirmed.
- Extended `tests/test_rendering_window.py` with a regression test that stubs a reporter and exercises the empty-world prompt.

## Design Decisions
- Keeping the report contract outside of the rendering package reduces coupling and allows future consumers (CLI, web, etc.) to share the same interface.
- `WorldWindow` keeps its paused/prompt logic but now simply broadcasts to any configured reporters rather than hard-coding console output.
- The behavioral test works through the prompt cycle (world with zero beans, prompt becomes active, Y key triggers the stub reporter) to validate the contract without touching UI internals.

## Challenges
- Ensuring the new package stayed importable from both runtime and tests required the `src` layout patch and clean imports; there were no additional dependency changes.

## Running the code and tests
1. Launch the simulation as normal; when the world runs out of beans the prompt now pauses and waits for Y/N before invoking all reporters.
2. `make test TEST_SPECIFIC=tests/test_rendering_window.py` (already run and passing at the time of this summary).

[Reporting Flow Diagram](./2025-11-27-reporting-flow-diagram.md)
