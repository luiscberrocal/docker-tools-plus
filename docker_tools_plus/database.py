import re
import sqlite3
from pathlib import Path

from pydantic import BaseModel, Field, validator

from .exceptions import DatabaseError
from .settings import settings


class Cleanup(BaseModel):
    """Pydantic model for cleanup configurations."""

    id: int | None = Field(..., description="Unique identifier for the cleanup")
    name: str = Field(..., min_length=1, max_length=64, description="Name of the cleanup configuration")
    regular_expression: str = Field(..., min_length=1, description="Regex pattern for matching resources")

    @validator("regular_expression")
    def validate_regex(cls, v:str) -> str:  # noqa: N805
        try:
            re.compile(v)
        except re.error as e:
            raise ValueError(f"Invalid regular expression: {e}") from e
        return v


class DatabaseManager:
    """Manager for handling database operations related to cleanups."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._initialize()

    def _initialize(self) -> None:
        """Initialize database and create tables."""
        db_path = Path(self.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with sqlite3.connect(db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS cleanups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        regular_expression TEXT NOT NULL
                    )
                """)
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to initialize database: {e}")

    def get_cleanup_by_name(self, name: str) -> list[Cleanup]:
        """Retrieve cleanups by name pattern."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.execute("SELECT * FROM cleanups WHERE name LIKE ?", (f"%{name}%",))
                return [
                    Cleanup(**dict(zip(["id", "name", "regular_expression"], row, strict=False)))
                    for row in cur.fetchall()
                ]
        except sqlite3.Error as e:
            raise DatabaseError(f"Database query failed: {e}") from e

    def list_cleanups(self) -> list[Cleanup]:
        """List all cleanups."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.execute("SELECT * FROM cleanups")
                return [
                    Cleanup(**dict(zip(["id", "name", "regular_expression"], row, strict=False)))
                    for row in cur.fetchall()
                ]
        except sqlite3.Error as e:
            raise DatabaseError(f"Database query failed: {e}") from e

    def delete_cleanup(self, cleanup_id: int) -> None:
        """Delete a cleanup by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM cleanups WHERE id = ?", (cleanup_id,))
                conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to delete cleanup: {e}") from e

    def create_cleanup(self, name: str, regex: str) -> Cleanup:
        """Create a new cleanup entry."""
        try:
            Cleanup(name=name, regular_expression=regex)  # Validate input
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.execute("INSERT INTO cleanups (name, regular_expression) VALUES (?, ?)", (name, regex))
                cleanup_id = cur.lastrowid
                conn.commit()

                cur = conn.execute("SELECT * FROM cleanups WHERE id = ?", (cleanup_id,))
                row = cur.fetchone()
                return Cleanup(**dict(zip(["id", "name", "regular_expression"], row, strict=False)))
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to create cleanup: {e}") from e
        except ValueError as e:
            raise DatabaseError(f"Failed to create cleanup: {e}") from e


# Create a global instance for the default database
_manager = DatabaseManager(settings.database_path)


# Public functions for backward compatibility
def get_cleanup_by_name(name: str) -> list[Cleanup]:
    return _manager.get_cleanup_by_name(name)


def list_cleanups() -> list[Cleanup]:
    return _manager.list_cleanups()


def delete_cleanup(cleanup_id: int):
    return _manager.delete_cleanup(cleanup_id)


def create_cleanup(name: str, regex: str) -> Cleanup:
    return _manager.create_cleanup(name, regex)
