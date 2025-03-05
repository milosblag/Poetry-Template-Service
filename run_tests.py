"""
Script to run tests with coverage.
"""
import subprocess
import sys


def run_tests():
    """Run tests with coverage and generate a report."""
    print("Running tests with coverage...")
    
    # Run pytest with coverage
    result = subprocess.run(
        [
            "pytest", 
            "--cov=app", 
            "--cov-report=term", 
            "--cov-report=html:coverage_html",
            "tests/"
        ],
        capture_output=True,
        text=True
    )
    
    # Print output
    print(result.stdout)
    
    if result.stderr:
        print("Errors:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
    
    # Return the exit code
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests()) 