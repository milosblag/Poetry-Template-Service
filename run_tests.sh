#!/bin/bash
# Script to run tests

echo "Running exception tests..."
poetry run python -m pytest tests/unit/test_exceptions.py -v > test_results_raw.txt 2>&1

echo "Running main tests..."
poetry run python -m pytest tests/unit/test_main.py -v >> test_results_raw.txt 2>&1

echo "Running coverage tests..."
poetry run python -m pytest --cov=app --cov-report=term-missing >> test_results_raw.txt 2>&1

# Filter out the warnings
grep -v "PytestDeprecationWarning" test_results_raw.txt > test_results.txt
rm test_results_raw.txt

echo "Tests completed. Results saved to test_results.txt" 