# Beans

A Python project scaffolded according to Python packaging standards.

## Features

- Modern Python project structure with `src/` layout
- PEP 517/518 compliant build system using `pyproject.toml`
- Comprehensive testing setup with pytest
- Code quality tools (black, flake8, mypy, isort)
- Pre-configured development environment

## Installation

### For Users

```bash
pip install beans
```

### For Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/beans.git
cd beans
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode with dev dependencies:
```bash
pip install -e ".[dev]"
# Or using requirements files:
pip install -r requirements-dev.txt
```

## Usage

```python
from beans import example

# Your code here
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
# Format code with black
black src/ tests/

# Sort imports
isort src/ tests/
```

### Type Checking

```bash
mypy src/
```

### Linting

```bash
flake8 src/ tests/
```

## Project Structure

```
beans/
├── src/
│   └── beans/           # Main package code
│       └── __init__.py
├── tests/               # Test files
│   └── test_example.py
├── docs/                # Documentation
├── pyproject.toml       # Project configuration and dependencies
├── setup.py             # Backward compatibility setup
├── requirements.txt     # Production dependencies
├── requirements-dev.txt # Development dependencies
├── .gitignore          # Git ignore rules
├── README.md           # This file
├── LICENSE             # License file
└── CONTRIBUTING.md     # Contribution guidelines
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- Your Name - Initial work

## Acknowledgments

- Thanks to all contributors
