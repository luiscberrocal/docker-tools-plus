"""Test suite for docker-tools.

Testing Setup:
1. Install dependencies:
   ```bash
   uv pip install -e . --group dev
   ```

2. Run tests with coverage:
   ```bash
   pytest -v --cov=docker_tools
   ```

Common Test Commands:
- Run all tests: `pytest -v`
- Run specific test file: `pytest -v tests/test_database.py`
- Run specific test class: `pytest -v tests/test_database.py::TestDatabaseInitialization`
- Run with coverage: `pytest --cov=docker_tools --cov-report=term-missing`
- Generate HTML report: `pytest --cov=docker_tools --cov-report=html`

Test Configuration (from pyproject.toml):
- Looks in "tests" directory
- Finds files matching "test_*.py"
- Shows coverage with missing lines by default

Database Test Notes:
- Uses temporary database files
- Tests are isolated and independent
- Automatic cleanup after each test
"""
