# Contributing to Beans

Thank you for your interest in contributing to Beans! We welcome contributions from everyone.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment (see README.md)
4. Create a new branch for your changes

## Development Process

### Setting Up Your Environment

```bash
# Clone your fork
git clone https://github.com/yourusername/beans.git
cd beans

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Making Changes

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and ensure they follow our coding standards
3. Write or update tests as needed
4. Run the test suite to ensure everything passes

### Code Style

We use several tools to maintain code quality:

- **Black** for code formatting (line length: 88)
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Before submitting your changes, run:

```bash
# Format code
black src/ tests/
isort src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/

# Run tests
pytest
```

### Testing

- Write tests for all new features and bug fixes
- Ensure all tests pass before submitting a pull request
- Aim for high test coverage
- Use pytest for writing tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=beans --cov-report=html
```

### Commit Messages

- Use clear and descriptive commit messages
- Start with a verb in the present tense (e.g., "Add", "Fix", "Update")
- Keep the first line under 50 characters
- Add a detailed description if necessary

Example:
```
Add user authentication feature

- Implement login/logout functionality
- Add password hashing
- Create user session management
```

### Submitting a Pull Request

1. Push your changes to your fork:
```bash
git push origin feature/your-feature-name
```

2. Go to the original repository on GitHub and create a pull request
3. Provide a clear description of your changes
4. Link any related issues
5. Wait for review and address any feedback

## Code Review Process

- All submissions require review before being merged
- Reviewers may ask for changes or clarification
- Once approved, a maintainer will merge your pull request

## Reporting Bugs

When reporting bugs, please include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Your environment (OS, Python version, etc.)
- Any relevant error messages or logs

## Feature Requests

We welcome feature requests! Please:

- Check if the feature has already been requested
- Provide a clear use case
- Explain why this feature would be useful
- Be open to discussion about implementation

## Questions?

If you have questions about contributing, feel free to:

- Open an issue for discussion
- Reach out to the maintainers

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on what is best for the community
- Show empathy towards others

Thank you for contributing to Beans!
