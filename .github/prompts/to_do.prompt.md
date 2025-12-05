---
agent: agent
---
# TODO List
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
- Energy systemn is already a module and can be replaced