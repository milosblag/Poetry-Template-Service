.PHONY: help install run test lint format clean security-clean docker-build docker-run docker-scan docker-check

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make run          - Run the application"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linting"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean up temporary files and security reports"
	@echo "  make security-clean - Clean up security reports only"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container"
	@echo "  make docker-scan  - Scan Docker image for vulnerabilities"
	@echo "  make docker-check - Check Docker connectivity and diagnose issues"

install:
	poetry install

run:
	poetry run python run.py

test:
	poetry run python run_tests.py

lint:
	poetry run flake8 app
	-poetry run mypy app

format:
	poetry run black app tests
	poetry run isort app tests

security-clean:
	rm -f security-report-*.md security-report-*.html scan-results.json trivy-*.json trivy-*.sarif
	rm -rf security-reports

clean: security-clean
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
	find . -type d -name "coverage_html" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .mypy_cache/

docker-build:
	docker build -t hello-world-api .

docker-run:
	docker run -p 8000:8000 hello-world-api 

docker-scan:
	./docker_vulnerability_scanner.sh

docker-check:
	./docker_connectivity_check.sh 