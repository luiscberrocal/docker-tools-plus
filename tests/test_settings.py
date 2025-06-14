from pathlib import Path
from unittest.mock import patch

import tomli

from docker_tools_plus import settings


class TestSettings:
    """Tests for the application settings."""

    def test_load_settings_from_toml(self, tmp_path):
        """Test loading settings from a TOML configuration file."""
        # Create a temporary TOML configuration file
        config_path = tmp_path / "configuration.toml"
        config_data = {
            "database_path": str(tmp_path / "custom.db"),
            "log_level": "DEBUG",
            "default_timeout": 60,
        }
        with open(config_path, "wb") as f:
            tomli.dump(config_data, f)

        # Change current directory to the temporary directory
        with patch("docker_tools_plus.settings.Path.cwd", return_value=tmp_path):
            loaded_settings = settings.Settings.load()

        # Verify settings were loaded from the TOML file
        assert loaded_settings.database_path == tmp_path / "custom.db"
        assert loaded_settings.log_level == "DEBUG"
        assert loaded_settings.default_timeout == 60

    def test_default_settings_when_no_toml(self, tmp_path):
        """Test that default settings are used when no TOML file exists."""
        # Change current directory to a temporary directory without configuration.toml
        with patch("docker_tools_plus.settings.Path.cwd", return_value=tmp_path):
            loaded_settings = settings.Settings.load()

        # Verify default settings
        expected_db_path = Path.home() / ".config" / "docker_tools_plus" / "docker_tools_plus.db"
        assert loaded_settings.database_path == expected_db_path
        assert loaded_settings.log_level == "INFO"
        assert loaded_settings.default_timeout == 30

    def test_get_configuration_folder(self):
        """Test the get_configuration_folder method returns the expected path."""
        expected_path = Path.home() / ".config" / "docker_tools_plus"
        assert settings.Settings.get_configuration_folder() == expected_path

    def test_configuration_folder_creation(self, tmp_path):
        """Test that the configuration folder is created if it doesn't exist."""
        # Mock the home directory to a temporary path
        with patch("docker_tools_plus.settings.Path.home", return_value=tmp_path):
            config_folder = settings.Settings.get_configuration_folder()
            assert config_folder.exists()
            assert config_folder == tmp_path / ".config" / "docker_tools_plus"
