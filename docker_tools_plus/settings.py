from pathlib import Path
from typing import Any, ClassVar

import tomli
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings configuration."""

    database_path: Path = Field(description="Path to the SQLite database file")
    log_level: str = "INFO"
    default_timeout: int = Field(30, gt=0, description="Default timeout in seconds for Docker operations")

    logging_config: ClassVar[dict[str, Any]] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}},
        "handlers": {
            "default": {
                "level": "INFO",
                "formatter": "standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            }
        },
        "loggers": {"docker_tools_plus": {"handlers": ["default"], "level": "INFO", "propagate": False}},
    }

    @classmethod
    def load(cls) -> "Settings":
        """Load configuration from TOML file if exists."""
        config_path = Path("configuration.toml")
        if config_path.exists():
            with open(config_path, "rb") as f:
                config = tomli.load(f)
                return cls(**config)

        database_path = cls.get_configuration_folder() / "docker_tools_plus.db"
        return cls(database_path=database_path)

    @classmethod
    def get_configuration_folder(cls) -> Path:
        """Get the folder where configuration files are stored."""
        folder = Path().home() / ".config" / "docker_tools_plus"
        folder.mkdir(parents=True, exist_ok=True)
        return folder


settings = Settings.load()
