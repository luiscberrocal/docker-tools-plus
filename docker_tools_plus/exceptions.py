class DockerToolsError(Exception):
    """Base exception for docker-tools errors."""

    pass


class InvalidCleanupError(DockerToolsError):
    """Raised when a cleanup configuration is invalid."""

    pass


class InvalidRegularExpressionError(DockerToolsError):
    """Raised when a regular expression is invalid."""

    pass


class DatabaseError(DockerToolsError):
    """Raised for database-related errors."""

    pass


class DockerCommandError(DockerToolsError):
    """Raised when a Docker command fails."""

    pass
