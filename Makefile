.PHONY: help install run test clean docker-up docker-down docker-logs

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt

run:  ## Run the application locally
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:  ## Run tests with coverage
	pytest

test-verbose:  ## Run tests with verbose output
	pytest -v -s

coverage:  ## Generate coverage report
	pytest --cov=app --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

docker-up:  ## Start all Docker containers
	docker-compose up -d

docker-down:  ## Stop all Docker containers
	docker-compose down

docker-logs:  ## Show Docker logs
	docker-compose logs -f

docker-rebuild:  ## Rebuild and restart containers
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

docker-shell:  ## Open shell in API container
	docker-compose exec api /bin/bash

clean:  ## Clean up cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	rm -rf *.egg-info

lint:  ## Run code linters
	@echo "Running flake8..."
	flake8 app tests --max-line-length=100 --ignore=E501,W503 || true
	@echo "Running black..."
	black --check app tests || true

format:  ## Format code with black
	black app tests

migrate-init:  ## Initialize database migrations
	alembic init migrations

migrate-create:  ## Create a new migration
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

migrate-up:  ## Apply migrations
	alembic upgrade head

migrate-down:  ## Rollback last migration
	alembic downgrade -1

worker:  ## Run Celery worker locally
	celery -A app.workers.celery_worker worker --loglevel=info

beat:  ## Run Celery beat locally
	celery -A app.workers.celery_worker beat --loglevel=info

flower:  ## Run Flower monitoring
	celery -A app.workers.celery_worker flower --port=5555

db-shell:  ## Connect to PostgreSQL database
	docker-compose exec postgres psql -U priceuser -d pricedb

redis-cli:  ## Connect to Redis CLI
	docker-compose exec redis redis-cli
