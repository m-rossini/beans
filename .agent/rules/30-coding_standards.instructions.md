---
applyTo: '**'
---
# Coding Standards and Best Practices

- When generating code, please go step by step, make one change at a time
- DO NOT MAKE UP FACTS. If you don't know, say "I don't know".
- Avoid over engineering. Keep it simple.
- Avoid introspective code unless absolutely necessary, especially to check attribuite existence
- Always go STEP BY STEP, change the minimum amount of code and files possible to achieve the goal
- Use Extreme programming practices, specially pair programming and TDD, and I am the other pair programmer
- ALWAYS ask me to review the code
- Use TDD approach, ensure test fails, fix code, ensure test passes, show me each step
- After each step ask me for commit, do not mention tests run and passed statistics on commits, descriptions should be business related
- DO NOT write code in __init__.py files unless absolutely necessary

## Defensive Code
- Defensivec code can bloat and make things difficult
- It is better to let the code fail fast and loudly than to try to handle every possible edge case
- NEVER EVER use try/except to handle logic flow
- Do not use isinstace for basic types are number or striung, let code fail if wrong type is passed
- When using configuration files, and having default values, do not check for existence of keys, just access them directly, let the code fail if they do not exist

## Naming Conventions
- Use `snake_case` for function and variable names
- Use `PascalCase` for class names
- Use `UPPER_SNAKE_CASE` for constants
- Use descriptive names that convey the purpose of the variable, function, or class

## Imports
- Use standard library imports first
- Do not * imports
- NEVER, EVER do LOCAL imports, always on the top of the file
- Group imports in the following order: standard library, third-party packages, local application imports
- Separate each group with a blank line

## Type Hints
- Use type hints for all function and method signatures
- Use `Optional` from `typing` for parameters that can be `None`
- Use `Union` from `typing` for parameters that can be of multiple types

## Exception Handling
- Use specific exceptions rather than catching all exceptions with a bare `except`
- Always log exceptions with relevant context before re-raising them
- NEVER EVER suppress exceptions without handling them
- NEVER EVER swallow exceptions

## Logging
- Use the `logging` module for logging
- Use appropriate logging levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
- Include relevant context in log messages
- Logging statements should be concise and to the point
- Log messages should include class::method for easier tracing or file::function if not in class
- Log messages of debug level should always have >>>>> just before the message


