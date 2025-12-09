---
agent: agent
---

# TODO List

1. ✅ Package world update method in high abstractions level such as calculate_energy and then call lower level methods inside.
1. ✅ Energy System should be a world configuraiton
1. ✅ Ensure speed calculations can be implemented as interface and concrete classes - Speed System.Fix Initial Speed

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
- Ensure agent implementations can be plugged in and swapped out easily
- Ensure health system is modular and can be replaced
- Create a Survival system module, which is for now the current existing one in bean
- Implement a matting system
  - age constrained
  - energy constrained
  - size constrained
  
- Ensure all Systems are defined at configuration time

## Experimentation
- Create tests to experiment with tunning parameters and compare results:
  - min_speed_factor, speed_min, speed_max