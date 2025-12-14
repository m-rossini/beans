---
applyTo: '**'
---
# Python Development Guidelines
This file outlines STRICT abnd HARD rules that must be followed to the letter when using agents to code.
Below is a list of different files covering different topics that MUST be followed


(VERY IMPORTANT) NEVER EVER USE INSTROSPECTION TO SOLVE ANY PROBLEM UNLESS EXPLICITLY ASKED TO DO SO IN THE INSTRUCTIONS
Avoid commenting code whenever possible

## General Instructions
Follow the instructions on this section and the instructions on each file.

- When python, ensure you are on the correct environment
- When Asked a question, never change or add code, always ANSWER and give an educated answer with pros and cons of your choice
- When in doubt, ask clarification questions. Do not assume, ask.
- Stick to the request, do not go beyond what is asked.
- Always use the commands in the make file. If they are not there please suggest adding them
- I am usinf ruff for linting and format checking, ensur eyou follow the rules in project.toml
- For pythong ALWAYS activate the proper enviuronment in each new shell, if you use powersheel use the correct scripts

## Procedures
- Always plan first
- Divide the problem in phases and steps inside phases
- If current branch is main, create a new branch to implement the plan
- Implement each phase following TDD
- Ask if you can commit and once commited, you move to the next phase.
- No need to ask permission between steps in the same phase, only to commit and change phase
- Each cycle of TDD and Implementation that is successful ALL tests must run and pass
- Tests must run as make, first specific tests and once all pass, make test for all tests
- After all tests pass, commit the changes with a concise message of what was done
- After each phase commit and ask to proceed with the next phase
- After all phases are done, create a PULL REQUEST and ask for a code review


## Architecture & Design
[See design.instructions.md](./20-design.instructions.md)

## Coding Standards & Best Practices
[See coding_standards.instructions.md](./30-coding_standards.instructions.md)

## Testing Guidelines
[See testing.instructions.md](./40-testing.instructions.md) 

## Package Management & Dependencies
[See package_management.instructions.md](./50-package_management.instructions.md)   

## Post Work Guidelines
[See post_work.instructions.md](./60-post-work.instructions.md)
