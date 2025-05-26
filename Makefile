PYTHON = python
PYTEST = pytest
RUFF = ruff
COVERAGE = coverage

.PHONY: test coverage lint clean help

help:
	@echo "Available commands:"
	@echo "  test     - Run all tests with verbose output"
	@echo "  coverage - Generate HTML coverage report"
	@echo "  lint     - Run linting checks with ruff"
	@echo "  clean    - Clean up temporary files"
	@echo "  help     - Show this help message"

test:
	$(PYTEST) -v tests/

test-unit:
	$(PYTEST) -v -m unit tests/

test-integration:
	$(PYTEST) -v -m integration tests/

test-database:
	$(PYTEST) -v -m database tests/test_database.py

coverage:
	$(PYTEST) --cov=docker_tools --cov-report=html
	@echo "Coverage report generated at htmlcov/index.html"

lint:
	$(RUFF) check docker_tools/ tests/

clean:
	@rm -rf .coverage
	@rm -rf htmlcov/
	@rm -rf .pytest_cache/
	@rm -rf .ruff_cache/
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name ".DS_Store" -delete
	@echo "Cleaned up temporary files!"
