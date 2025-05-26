import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from docker_tools.cli import cli
from docker_tools.database import create_cleanup, list_cleanups
import subprocess

class TestCLICommands:
    @pytest.fixture(autouse=True)
    def runner(self):
        return CliRunner()

    def test_about_command(self, runner):
        result = runner.invoke(cli, ["about"])
        assert "docker-tools v0.1.0" in result.output
        assert "Database location" in result.output
        assert "CLI tool for managing Docker" in result.output

class TestCleanCommand:
    def test_new_cleanup_creation(self, runner):
        # Test new config creation flow
        test_inputs = ["test-regex"]
        with patch("click.prompt", side_effect=test_inputs):
            result = runner.invoke(cli, ["clean", "test-app"])
            assert "Created new cleanup config" in result.output
            assert "test-app" in result.output
            assert "test-regex" in result.output

    def test_existing_cleanup_selection(self, runner):
        create_cleanup("test-app", "existing-regex")
        result = runner.invoke(cli, ["clean", "test-app"])
        assert "Using existing cleanup" in result.output
        assert "existing-regex" in result.output

    def test_multiple_cleanup_selection(self, runner):
        create_cleanup("duplicate", "regex1")
        create_cleanup("duplicate", "regex2")
        test_inputs = ["2"]
        with patch("click.prompt", side_effect=test_inputs):
            result = runner.invoke(cli, ["clean", "duplicate"])
            assert "regex2" in result.output

    @patch("subprocess.run")
    def test_cleanup_execution(self, mock_run, runner):
        create_cleanup("test", "test-.*")
        test_inputs = ["y", "y", "y"]
        with patch("click.confirm", side_effect=test_inputs):
            result = runner.invoke(cli, ["clean", "test"])
            assert mock_run.call_count == 3
            assert "containers" in result.output
            assert "volumes" in result.output
            assert "images" in result.output

class TestListCommand:
    def test_empty_list(self, runner):
        result = runner.invoke(cli, ["list"])
        assert "No cleanups found" in result.output

    def test_populated_list(self, runner):
        create_cleanup("app1", "regex1")
        create_cleanup("app2", "regex2")
        result = runner.invoke(cli, ["list"])
        assert "app1" in result.output
        assert "app2" in result.output
        assert "regex1" in result.output
        assert "regex2" in result.output

class TestDeleteCommand:
    def test_successful_deletion(self, runner):
        cleanup = create_cleanup("delete-me", "regex")
        with patch("click.confirm", return_value=True):
            result = runner.invoke(cli, ["delete", "delete-me"])
            assert "deleted successfully" in result.output
            assert len(list_cleanups()) == 0

    def test_cancel_deletion(self, runner):
        create_cleanup("keep-me", "regex")
        with patch("click.confirm", return_value=False):
            result = runner.invoke(cli, ["delete", "keep-me"])
            assert "deleted" not in result.output
            assert len(list_cleanups()) == 1

    def test_multiple_matches_deletion(self, runner):
        create_cleanup("duplicate", "r1")
        create_cleanup("duplicate", "r2")
        test_inputs = ["1", "y"]
        with patch("click.prompt", side_effect=test_inputs):
            result = runner.invoke(cli, ["delete", "duplicate"])
            assert "Deleted cleanup 'duplicate'" in result.output
            assert len(list_cleanups()) == 1

class TestErrorHandling:
    def test_invalid_id_selection(self, runner):
        create_cleanup("test1", "r1")
        create_cleanup("test2", "r2")
        with patch("click.prompt", return_value=999):
            result = runner.invoke(cli, ["clean", "test"])
            assert "Invalid ID" in result.output

    @patch("docker_tools.database.get_cleanup_by_name")
    def test_database_error(self, mock_db, runner):
        mock_db.side_effect = Exception("DB failure")
        result = runner.invoke(cli, ["clean", "test"])
        assert "Error occurred" in result.output
        assert "DB failure" in result.output

    @patch("subprocess.run")
    def test_docker_command_failure(self, mock_run, runner):
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd")
        create_cleanup("fail", "regex")
        with patch("click.confirm", return_value=True):
            result = runner.invoke(cli, ["clean", "fail"])
            assert "Failed to clean" in result.output
