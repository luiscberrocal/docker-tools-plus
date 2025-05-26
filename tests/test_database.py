import pytest
from docker_tools.database import (
    Cleanup,
    init_db,
    create_cleanup,
    get_cleanup_by_name,
    list_cleanups,
    delete_cleanup
)
from docker_tools.settings import settings
import sqlite3

class TestDatabaseInitialization:
    def test_table_creation(self):
        # Verify table structure
        with sqlite3.connect(settings.database_path) as conn:
            cursor = conn.execute("PRAGMA table_info(cleanups)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            
        assert columns == {
            'id': 'INTEGER',
            'name': 'TEXT',
            'regular_expression': 'TEXT'
        }

class TestCreateCleanup:
    def test_basic_creation(self):
        cleanup = create_cleanup("test", "test.*")
        assert isinstance(cleanup, Cleanup)
        assert cleanup.name == "test"
        assert cleanup.regular_expression == "test.*"
        
    def test_id_auto_increment(self):
        first = create_cleanup("first", ".*")
        second = create_cleanup("second", ".*")
        assert second.id == first.id + 1

class TestGetCleanupByName:
    @pytest.fixture(autouse=True)
    def setup_data(self):
        create_cleanup("apple", "a.*")
        create_cleanup("banana", "b.*")
        create_cleanup("orange", "o.*")

    def test_exact_match(self):
        results = get_cleanup_by_name("apple")
        assert len(results) == 1
        assert results[0].name == "apple"

    def test_partial_match(self):
        results = get_cleanup_by_name("ana")
        assert len(results) == 1
        assert results[0].name == "banana"

    def test_case_insensitivity(self):
        results = get_cleanup_by_name("APPLE")
        assert len(results) == 1

    def test_no_matches(self):
        results = get_cleanup_by_name("xyz")
        assert len(results) == 0

class TestListCleanups:
    def test_empty_database(self):
        assert list_cleanups() == []

    def test_full_listing(self):
        names = ["first", "second", "third"]
        for name in names:
            create_cleanup(name, ".*")
            
        results = list_cleanups()
        assert len(results) == 3
        assert {c.name for c in results} == set(names)

class TestDeleteCleanup:
    @pytest.fixture
    def sample_cleanup(self):
        return create_cleanup("test", "test.*")

    def test_successful_deletion(self, sample_cleanup):
        initial_count = len(list_cleanups())
        delete_cleanup(sample_cleanup.id)
        assert len(list_cleanups()) == initial_count - 1

    def test_nonexistent_id(self):
        initial_count = len(list_cleanups())
        delete_cleanup(999)
        assert len(list_cleanups()) == initial_count

class TestEdgeCases:
    def test_duplicate_names(self):
        create_cleanup("dupe", "d1")
        create_cleanup("dupe", "d2")
        results = get_cleanup_by_name("dupe")
        assert len(results) == 2
        assert {c.regular_expression for c in results} == {"d1", "d2"}

    def test_special_characters(self):
        special_name = "test@cleanup!123"
        special_regex = "^[a-z0-9_]+$"
        cleanup = create_cleanup(special_name, special_regex)
        
        results = get_cleanup_by_name(special_name)
        assert results[0].regular_expression == special_regex

    def test_long_strings(self):
        long_name = "a" * 255
        long_regex = "b" * 500
        cleanup = create_cleanup(long_name, long_regex)
        
        result = get_cleanup_by_name(long_name)[0]
        assert result.name == long_name
        assert result.regular_expression == long_regex
