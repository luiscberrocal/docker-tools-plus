import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from docker_tools_plus.cli import cli
from docker_tools_plus.database import Cleanup
from docker_tools_plus.settings import settings


class TestCLI:
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        self.runner = CliRunner()
        # Patch the database functions
        self.db_patchers = {
            "get_cleanup_by_name": patch("docker_tools_plus.cli.get_cleanup_by_name"),
            "create_cleanup": patch("docker_tools_plus.cli.create_cleanup"),
            "list_cleanups": patch("docker_tools_plus.cli.list_cleanups"),
            "delete_cleanup": patch("docker_tools_plus.cli.delete_cleanup"),
        }
        self.mocks = {name: patcher.start() for name, patcher in self.db_patchers.items()}
        # Patch logger
        self.logger_patcher = patch("docker_tools_plus.cli.logger")
        self.mock_logger = self.logger_patcher.start()
        # Patch subprocess
        self.subprocess_patcher = patch("docker_tools_plus.cli.subprocess")
        self.mock_subprocess = self.subprocess_patcher.start()
        # Patch settings
        self.settings_patcher = patch("docker_tools_plus.cli.settings")
        self.mock_settings = self.settings_patcher.start()
        self.mock_settings.database_path = "/test/db/path"

        yield

        for patcher in self.db_patchers.values():
            patcher.stop()
        self.logger_patcher.stop()
        self.subprocess_patcher.stop()
        self.settings_patcher.stop()

    def test_about(self):
        result = self.runner.invoke(cli, ["about"])
        assert "docker-tools" in result.output
        assert "Database location: /test/db/path" in result.output

    def test_clean_no_match_creates_new(self):
        self.mocks["get_cleanup_by_name"].return_value = []
        mock_cleanup = MagicMock(spec=Cleanup)
        mock_cleanup.id = 1
        mock_cleanup.name = "test"
        mock_cleanup.regular_expression = "test.*"
        self.mocks["create_cleanup"].return_value = mock_cleanup

        # Simulate user input for regex prompt
        inputs = ["test.*"]
        result = self.runner.invoke(cli, ["clean", "test"], input="\n".join(inputs))

        assert "No cleanup found matching 'test'" in result.output
        self.mocks["create_cleanup"].assert_called_once_with("test", "test.*")
        assert "Successfully cleaned" in result.output

    def test_clean_single_match(self):
        mock_cleanup = MagicMock(spec=Cleanup)
        mock_cleanup.id = 1
        mock_cleanup.name = "test"
        mock_cleanup.regular_expression = "test.*"
        self.mocks["get_cleanup_by_name"].return_value = [mock_cleanup]

        result = self.runner.invoke(cli, ["clean", "test", "--force"])

        assert mock_cleanup.regular_expression in result.output
        assert self.mock_subprocess.run.call_count == 3

    def test_clean_multiple_matches(self):
        mock_cleanups = [
            MagicMock(spec=Cleanup, id=1, name="test", regular_expression="test1.*"),
            MagicMock(spec=Cleanup, id=2, name="test", regular_expression="test2.*")
        ]
        self.mocks["get_cleanup_by_name"].return_value = mock_cleanups

        # Simulate user selecting ID 2
        inputs = ["2"]
        result = self.runner.invoke(cli, ["clean", "test"], input="\n".join(inputs))

        assert "Multiple cleanups found" in result.output
        self.mocks["get_cleanup_by_name"].assert_called_once_with("test")
        assert "test1.*" in result.output
        assert "test2.*" in result.output
        assert "Cleaning using pattern 'test2.*'" in result.output

    def test_list_cleanups(self):
        mock_cleanups = [
            MagicMock(spec=Cleanup, id=1, name="test1", regular_expression="test1.*"),
            MagicMock(spec=Cleanup, id=2, name="test2", regular_expression="test2.*")
        ]
        self.mocks["list_cleanups"].return_value = mock_cleanups

        result = self.runner.invoke(cli, ["list"])

        assert "1: test1 - test1.*" in result.output
        assert "2: test2 - test2.*" in result.output

    def test_list_no_cleanups(self):
        self.mocks["list_cleanups"].return_value = []
        result = self.runner.invoke(cli, ["list"])
        assert "No cleanups found" in result.output

    def test_delete_single_match(self):
        mock_cleanup = MagicMock(spec=Cleanup, id=1, name="test")
        self.mocks["get_cleanup_by_name"].return_value = [mock_cleanup]

        # Confirm deletion
        inputs = ["y"]
        result = self.runner.invoke(cli, ["delete", "test"], input="\n".join(inputs))

        assert "Delete cleanup 'test' (ID: 1)?" in result.output
        self.mocks["delete_cleanup"].assert_called_once_with(1)
        assert "Cleanup deleted successfully" in result.output

    def test_delete_multiple_matches(self):
        mock_cleanups = [
            MagicMock(spec=Cleanup, id=1, name="test"),
            MagicMock(spec=Cleanup, id=2, name="test")
        ]
        self.mocks["get_cleanup_by_name"].return_value = mock_cleanups

        # Select ID 2 and confirm deletion
        inputs = ["2", "y"]
        result = self.runner.invoke(cli, ["delete", "test"], input="\n".join(inputs))

        assert "Multiple matches found" in result.output
        self.mocks["delete_cleanup"].assert_called_once_with(2)

    def test_clean_error_handling(self):
        self.mocks["get_cleanup_by_name"].side_effect = Exception("DB error")
        result = self.runner.invoke(cli, ["clean", "test"])
        assert "Error: DB error" in result.output

    def test_clean_execution_error(self):
        mock_cleanup = MagicMock(spec=Cleanup, regular_expression="test.*")
        self.mocks["get_cleanup_by_name"].return_value = [mock_cleanup]
        self.mock_subprocess.run.side_effect = subprocess.CalledProcessError(1, "cmd")

        result = self.runner.invoke(cli, ["clean", "test", "--force"])

        assert "Failed to clean" in result.output
        assert self.mock_logger.error.call_count == 3
