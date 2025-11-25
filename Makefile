# Makefile for common development tasks

# Force using Windows Command Prompt for make recipes so we match user environment
SHELL := cmd.exe

.PHONY: help install install-dev test lint format type-check clean build

LOGGING_LEVEL ?= INFO

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package
	pip install -e .

install-dev:  ## Install the package with development dependencies
	pip install -e ".[dev]"

test:  ## Run tests with pytest (full suite)
	set PYTHONPATH=src && set LOGGING_LEVEL=$(LOGGING_LEVEL) && python -m pytest -v -s

test-cov:  ## Run tests with coverage report
	set PYTHONPATH=src && set LOGGING_LEVEL=$(LOGGING_LEVEL) && python -m coverage run --source=src/beans,src/config,src/rendering -m pytest -v -s
	set PYTHONPATH=src && python -m coverage report -m --skip-empty
	set PYTHONPATH=src && python -m coverage html

TEST_SPECIFIC ?= tests/test_config.py

test-specific:  ## Run a specific test file only. Use TEST_SPECIFIC=path to override.
	set PYTHONPATH=src && set LOGGING_LEVEL=$(LOGGING_LEVEL) && python -m pytest -v -s $(TEST_SPECIFIC)

test-sequence: test-specific test  ## Run a specific test first, then the full test suite
	@echo Completed test sequence (specific then full suite)

lint:  ## Run flake8 linter
	flake8 src/ tests/

format:  ## Format code with black and isort
	black src/ tests/
	isort src/ tests/

format-check:  ## Check code formatting without making changes
	black --check src/ tests/
	isort --check-only src/ tests/

type-check:  ## Run mypy type checker
	mypy src/

clean:  ## Remove build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build the package
	python -m build

all: format lint type-check test  ## Run all checks (format, lint, type-check, test)

run:  ## Run the main application. Use CONFIG=path/to/config.json LOGGING_LEVEL=level DEBUG_MODULE=module to override.
	set PYTHONPATH=src && python scripts/run_window.py $(CONFIG) --logging-level $(LOGGING_LEVEL) $(if $(DEBUG_MODULE),--debug-module $(DEBUG_MODULE))
