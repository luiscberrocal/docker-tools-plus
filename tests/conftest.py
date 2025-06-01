import pytest


@pytest.fixture(autouse=True)
def clean_database():
    """Ensure clean database state for each test"""
    from docker_tools.database import init_db

    init_db()
