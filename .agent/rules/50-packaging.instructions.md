---
applyTo: '**'
---
# For package installation
 - It is OK to use pip or poetry to install on demand packages 
 - Once packages are installed, they must be added to the dependencies file used in the project
 - Use the standard way of installing packages for the project, if it uses poetry, use poetry, if it uses pip, use pip, if it is uv use uv, etc.
- For pip, add the packages to requirements.txt or requirements-dev.txt as needed
- Update the lock files if they are used in the project (e.g., poetry.lock, Pipfile.lock, etc.)
- Ensure that any new dependencies do not conflict with existing ones

