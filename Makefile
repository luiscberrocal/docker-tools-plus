PYTEST = pytest
RUFF = ruff

.PHONY: test coverage lint clean help dist

help:
	@echo "Available commands:"
	@echo "  test     - Run all tests with coverage (via pytest config)"
	@echo "  coverage - Generate HTML coverage report"
	@echo "  lint     - Run linting checks"
	@echo "  clean    - Clean temporary files"
	@echo "  help     - Show this help"

test:
	$(PYTEST) -v tests/

cov:
	$(PYTEST) --cov=docker_tools_plus --cov-report=html

lint:
	$(RUFF) check docker_tools_plus/ tests/

clean:
	@rm -rf .coverage htmlcov/ .pytest_cache/ .ruff_cache/
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.py[co]" -delete
	@find . -type f -name ".DS_Store" -delete
	@rm -rf ./dist/

dist: clean
	@uv build
	@uv run twine upload dist/*


