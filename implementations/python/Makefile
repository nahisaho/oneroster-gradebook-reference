# OneRoster Gradebook Service - Python/FastAPI Implementation
# Makefile for development and testing

.PHONY: help install dev test test-coverage format lint clean docker-build docker-up docker-down docker-logs docker-test

help: ## Show this help message
	@echo "OneRoster Gradebook Service - Python Implementation"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with Poetry
	poetry install

dev: ## Run development server
	poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests
	poetry run pytest tests/ -v

test-coverage: ## Run tests with coverage report
	poetry run pytest tests/ -v --cov=src --cov-report=html --cov-report=term

format: ## Format code with black and isort
	poetry run black src/ tests/
	poetry run isort src/ tests/

lint: ## Run linters (ruff and mypy)
	poetry run ruff check src/ tests/
	poetry run mypy src/

clean: ## Clean up cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete

docker-build: ## Build Docker containers
	docker-compose build

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker container logs
	docker-compose logs -f app

docker-test: ## Run tests in Docker container
	docker-compose exec app poetry run pytest tests/ -v

docker-shell: ## Open shell in Docker container
	docker-compose exec app /bin/bash

db-shell: ## Open PostgreSQL shell
	docker-compose exec db psql -U oneroster_user -d oneroster_gradebook

all: install format lint test ## Run all checks (install, format, lint, test)
