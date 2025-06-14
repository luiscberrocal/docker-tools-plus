import pytest
import sqlite3
from docker_tools_plus.database import DatabaseManager, CleanupSchema
from docker_tools_plus.exceptions import DatabaseError

class TestDatabaseManager:
    @pytest.fixture
    def manager(self, tmp_path):
        """Create a DatabaseManager with a temporary database."""
        db_path = tmp_path / "test.db"
        return DatabaseManager(str(db_path))

    def test_create_cleanup(self, manager):
        """Test creating a cleanup configuration."""
        cleanup = manager.create_cleanup("test", "pattern")
        assert isinstance(cleanup, CleanupSchema)
        assert cleanup.name == "test"
        assert cleanup.regular_expression == "pattern"

    def test_get_cleanup_by_name(self, manager):
        """Test retrieving cleanups by name pattern."""
        manager.create_cleanup("test1", "pattern1")
        manager.create_cleanup("test2", "pattern2")
        manager.create_cleanup("other", "pattern3")
        
        results = manager.get_cleanup_by_name("test")
        assert len(results) == 2
        assert {r.name for r in results} == {"test1", "test2"}

    def test_list_cleanups(self, manager):
        """Test listing all cleanups."""
        assert manager.list_cleanups() == []
        
        manager.create_cleanup("test1", "pattern1")
        manager.create_cleanup("test2", "pattern2")
        
        results = manager.list_cleanups()
        assert len(results) == 2
        assert {r.name for r in results} == {"test1", "test2"}

    def test_delete_cleanup(self, manager):
        """Test deleting a cleanup by ID."""
        cleanup = manager.create_cleanup("test", "pattern")
        manager.delete_cleanup(cleanup.id)
        assert manager.list_cleanups() == []

    def test_create_cleanup_invalid_regex(self, manager):
        """Test creating cleanup with invalid regex."""
        with pytest.raises(ValueError, match="Invalid regular expression"):
            manager.create_cleanup("test", "invalid[regex")

    def test_get_cleanup_by_name_no_match(self, manager):
        """Test getting cleanups when no matches exist."""
        manager.create_cleanup("test", "pattern")
        assert manager.get_cleanup_by_name("nomatch") == []

    def test_delete_nonexistent_cleanup(self, manager):
        """Test deleting a cleanup that doesn't exist."""
        # Should not raise any errors
        manager.delete_cleanup(999)

    def test_database_error_handling(self, manager, monkeypatch):
        """Test database error handling."""
        # Monkeypatch to simulate database error
        def mock_connect(*args, **kwargs):
            raise sqlite3.Error("Mocked database error")
        
        monkeypatch.setattr("sqlite3.connect", mock_connect)
        
        with pytest.raises(DatabaseError, match="Mocked database error"):
            manager.create_cleanup("test", "pattern")
