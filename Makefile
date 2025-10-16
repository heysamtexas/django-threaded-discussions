.PHONY: help test test-verbose lint format typecheck check install clean

help:
	@echo "Django Discussions - Development Commands"
	@echo ""
	@echo "  make test          Run all tests"
	@echo "  make test-verbose  Run tests with verbose output"
	@echo "  make lint          Run ruff linting"
	@echo "  make format        Auto-format code with ruff"
	@echo "  make typecheck     Run mypy type checking"
	@echo "  make check         Run all quality checks (lint + typecheck + test)"
	@echo "  make install       Install package with dev dependencies"
	@echo "  make clean         Remove build artifacts"

test:
	PYTHONPATH=. uv run python tests/manage.py test

test-verbose:
	PYTHONPATH=. uv run python tests/manage.py test --verbosity=2

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

typecheck:
	uv run mypy src/

check: lint typecheck test
	@echo "✅ All checks passed!"

install:
	uv sync --extra dev

clean:
	rm -rf dist/ build/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.db" -delete
	find . -type f -name "*.sqlite3" -delete
