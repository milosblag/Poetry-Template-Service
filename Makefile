.PHONY: help install run test lint format clean docker-build docker-run

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make run          - Run the application"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linting"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean up temporary files"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container"

install:
	poetry install

run:
	poetry run python run.py

test:
	poetry run python run_tests.py

lint:
	poetry run flake8 app
	poetry run mypy app

format:
	poetry run black app tests
	poetry run isort app tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.eggs" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage_html" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .mypy_cache/

docker-build:
	docker build -t hello-world-api .

docker-run:
	docker run -p 8000:8000 hello-world-api 