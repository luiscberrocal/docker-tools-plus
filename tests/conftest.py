import pytest
from docker_tools.database import list_cleanups, delete_cleanup


@pytest.fixture(autouse=True)
def clean_database():
    """Ensure clean database state for each test"""
    # Delete all cleanups after each test
    yield
    for cleanup in list_cleanups():
        delete_cleanup(cleanup.id)
