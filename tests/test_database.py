import sqlite3
import pytest

from docker_tools.database import Cleanup, DatabaseManager


@pytest.fixture
def db_manager(tmp_path):
    db_path = tmp_path / "test.db"
    manager = DatabaseManager(str(db_path))
    return manager


class TestDatabaseInitialization:
    def test_table_creation(self, db_manager):
        # Verify table structure
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.execute("PRAGMA table_info(cleanups)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}

        assert columns == {"id": "INTEGER", "name": "TEXT", "regular_expression": "TEXT"}


class TestCreateCleanup:
    def test_basic_creation(self, db_manager):
        cleanup = db_manager.create_cleanup("test", "test.*")
        assert isinstance(cleanup, Cleanup)
        assert cleanup.name == "test"
        assert cleanup.regular_expression == "test.*"

    def test_id_auto_increment(self, db_manager):
        first = db_manager.create_cleanup("first", ".*")
        second = db_manager.create_cleanup("second", ".*")
        assert second.id == first.id + 1


class TestGetCleanupByName:
    @pytest.fixture(autouse=True)
    def setup_data(self, db_manager):
        db_manager.create_cleanup("apple", "a.*")
        db_manager.create_cleanup("banana", "b.*")
        db_manager.create_cleanup("orange", "o.*")

    def test_exact_match(self, db_manager):
        results = db_manager.get_cleanup_by_name("apple")
        assert len(results) == 1
        assert results[0].name == "apple"

    def test_partial_match(self, db_manager):
        results = db_manager.get_cleanup_by_name("ana")
        assert len(results) == 1
        assert results[0].name == "banana"

    def test_case_insensitivity(self, db_manager):
        results = db_manager.get_cleanup_by_name("APPLE")
        assert len(results) == 1

    def test_no_matches(self, db_manager):
        results = db_manager.get_cleanup_by_name("xyz")
        assert len(results) == 0


class TestListCleanups:
    def test_empty_database(self, db_manager):
        assert db_manager.list_cleanups() == []

    def test_full_listing(self, db_manager):
        names = ["first", "second", "third"]
        for name in names:
            db_manager.create_cleanup(name, ".*")

        results = db_manager.list_cleanups()
        assert len(results) == 3
        assert {c.name for c in results} == set(names)


class TestDeleteCleanup:
    @pytest.fixture
    def sample_cleanup(self, db_manager):
        return db_manager.create_cleanup("test", "test.*")

    def test_successful_deletion(self, db_manager, sample_cleanup):
        initial_count = len(db_manager.list_cleanups())
        db_manager.delete_cleanup(sample_cleanup.id)
        assert len(db_manager.list_cleanups()) == initial_count - 1

    def test_nonexistent_id(self, db_manager):
        initial_count = len(db_manager.list_cleanups())
        db_manager.delete_cleanup(999)
        assert len(db_manager.list_cleanups()) == initial_count


class TestEdgeCases:
    def test_duplicate_names(self, db_manager):
        db_manager.create_cleanup("dupe", "d1")
        db_manager.create_cleanup("dupe", "d2")
        results = db_manager.get_cleanup_by_name("dupe")
        assert len(results) == 2
        assert {c.regular_expression for c in results} == {"d1", "d2"}

    def test_special_characters(self, db_manager):
        special_name = "test@cleanup!123"
        special_regex = "^[a-z0-9_]+$"
        cleanup = db_manager.create_cleanup(special_name, special_regex)

        results = db_manager.get_cleanup_by_name(special_name)
        assert results[0].regular_expression == special_regex

    def test_long_strings(self, db_manager):
        long_name = "a" * 255
        long_regex = "b" * 500
        cleanup = db_manager.create_cleanup(long_name, long_regex)

        result = db_manager.get_cleanup_by_name(long_name)[0]
        assert result.name == long_name
        assert result.regular_expression == long_regex
