.PHONY: help setup lint format test coverage clean docker docker-compose

# Default target
help:
	@echo "Available commands:"
	@echo "  make help        - Show this help message"
	@echo "  make setup       - Set up development environment"
	@echo "  make lint        - Run linters (flake8, mypy)"
	@echo "  make format      - Format code (black, isort)"
	@echo "  make test        - Run tests"
	@echo "  make coverage    - Run tests with coverage report"
	@echo "  make clean       - Clean up build artifacts"
	@echo "  make docker      - Build Docker image"
	@echo "  make docker-compose - Run with Docker Compose"

# Set up development environment
setup:
	pip install -r requirements.txt
	pip install -e .
	python scripts/download_models.py

# Run linters
lint:
	flake8 src tests
	mypy src

# Format code
format:
	black src tests
	isort src tests

# Run tests
test:
	pytest tests

# Run tests with coverage
coverage:
	pytest --cov=src tests --cov-report=term --cov-report=html

# Clean up build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build Docker image
docker:
	docker build -t lcm-framework .

# Run with Docker Compose
docker-compose:
	docker-compose up