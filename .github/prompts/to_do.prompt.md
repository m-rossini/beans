---
agent: agent
---

# TODO List

1. Package world update method in high abstractions level such as calculate_energy and then call lower level methods inside.
1. ✅ Energy System should be a world configuraiton

## Beans should be pluggable and have different types:
- Human
- Random Action
- Deterministic
- RL ML
- LLM Based

## Tests Should be Menaingful
- Review existing tests and check if they are testing behavior or just implementation

## Logging Improvements
- Make logging statements have the right amount of chevrons
- Make LOG DEBUG level suitable for tracing and experimenting, so it can be parsed and used to draw behaviour graphics and diagrams

## Modularization
- Ensure speed calculations can be implemented as interface and concrete classes
- Ensure agent implementations can be plugged in and swapped out easily
- Ensure death strategys can be implemented as interface and concrete classes
- Ensure health system is modular and can be replaced
- Create a Survival system module, which is for now the current existing one in bean
- Ensure all Systems are defined at configuration time


