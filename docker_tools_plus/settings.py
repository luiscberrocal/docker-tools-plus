from pathlib import Path
from typing import Any, ClassVar

import tomli
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings configuration."""

    database_path: Path = Path("cleanups.db")
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
    def load(cls):
        """Load configuration from TOML file if exists."""
        config_path = Path("configuration.toml")
        if config_path.exists():
            with open(config_path, "rb") as f:
                config = tomli.load(f)
                return cls(**config)
        return cls()


settings = Settings.load()
