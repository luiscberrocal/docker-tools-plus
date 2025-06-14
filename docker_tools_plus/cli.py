import datetime
import logging
import subprocess
from pathlib import Path

import click
from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel

from . import __version__
from .database import CleanupSchema, _manager, create_cleanup, delete_cleanup, get_cleanup_by_name, list_cleanups
from .exceptions import DatabaseError, DockerToolsError, InvalidRegularExpressionError
from .settings import settings

logger = logging.getLogger(__name__)


@click.group()
def cli() -> None:
    """Docker cleanup management tool."""


@cli.command()
@click.argument("name")
@click.option("--force", is_flag=True, help="Skip confirmation prompts")
def clean(name, force) -> None:
    """Execute cleanup by name.

    If no exact match is found, you'll be prompted to create a new configuration.
    """
    try:
        cleanups: list[CleanupSchema] = get_cleanup_by_name(name)

        if not cleanups:
            click.echo(f"No cleanup found matching '{name}'")
            regex = click.prompt("Please enter a regular expression for the cleanup")
            try:
                cleanup = create_cleanup(name, regex)
            except InvalidRegularExpressionError as e:
                logger.error(str(e))
                click.secho(f"Error creating cleanup: {e}", fg="red")
                return
        elif len(cleanups) > 1:
            click.echo("Multiple cleanups found:")
            for c in cleanups:
                click.echo(f"{c.id}: {c.name} ({c.regular_expression})")
            selected_id = click.prompt("Enter the ID to use", type=int)
            cleanup = next(c for c in cleanups if c.id == selected_id)
        else:
            cleanup = cleanups[0]

        _execute_cleanup(cleanup, force)
    except DockerToolsError as e:
        logger.error(str(e))
        click.secho(f"Error: {e}", fg="red")


def _execute_cleanup(cleanup: CleanupSchema, force: bool) -> None:
    """Run docker cleanup commands based on the selected configuration."""
    commands = {
        "containers": f"docker ps -a | grep -E '{cleanup.regular_expression}' | awk '{{print $1}}' | xargs docker rm",
        "volumes": f"docker volume ls | grep -E '{cleanup.regular_expression}' | awk '{{print $2}}' | xargs docker volume rm",
        "images": f"docker image ls | grep -E '{cleanup.regular_expression}' | awk '{{print $3}}' | xargs docker image rm",
    }

    for resource, cmd in commands.items():
        if force or click.confirm(f"Clean {resource} using pattern '{cleanup.regular_expression}'?", default=True):
            try:
                subprocess.run(cmd, shell=True, check=True)
                click.echo(f"Successfully cleaned {resource}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Error cleaning {resource}: {e}")
                click.secho(f"Failed to clean {resource}.", fg="red")


@cli.command(name="list")
def list_cleanups() -> None:
    """List all registered cleanups."""
    try:
        cleanups = _manager.list_cleanups()
        if not cleanups:
            click.echo("No cleanups found")
            return
        for cleanup in cleanups:
            click.echo(f"{cleanup.id}: {cleanup.name} - {cleanup.regular_expression}")
    except DockerToolsError as e:
        logger.error(str(e))
        click.secho(f"Error: {e}", fg="red")


@cli.command()
@click.argument("name")
def delete(name) -> None:
    """Delete a cleanup configuration."""
    try:
        cleanups = get_cleanup_by_name(name)

        if not cleanups:
            click.secho(f"No cleanups found matching '{name}'", fg="red")
            return

        if len(cleanups) > 1:
            click.echo("Multiple matches found:")
            for cleanup in cleanups:
                click.echo(f"{cleanup.id}: {cleanup.name}")
            selected_id = click.prompt("Enter the ID to delete", type=int)
            selected = next((c for c in cleanups if c.id == selected_id), None)
            if not selected:
                click.secho("Invalid ID", fg="red")
                return
        else:
            selected = cleanups[0]

        if click.confirm(f"Delete cleanup '{selected.name}' (ID: {selected.id})?", default=False):
            delete_cleanup(selected.id)
            click.secho("Cleanup deleted successfully", fg="green")
    except DockerToolsError as e:
        logger.error(str(e))
        click.secho(f"Error: {e}", fg="red")


@cli.command()
def about() -> None:
    """Show application information in a rich panel."""
    console = Console()
    db_path = Path(settings.database_path).absolute()
    db_exists = db_path.exists()
    status = "[green]✓[/green]" if db_exists else "[red]✗[/red]"
    version_line = Align.center(f"[bold]docker-tools[/bold] [green]v{__version__}[/green]", pad=False)
    db_line = f"[bold]Database location:[/bold] [yellow]{db_path}[/yellow] {status}"
    description_line = "[italic]CLI tool for managing Docker container cleanups[/italic]"
    group = Group(version_line, db_line, description_line)
    panel = Panel.fit(
        group,
        title="[bold green]About[/bold green]",
        border_style="blue",
        padding=(1, 2),
    )
    console.print(panel)


@cli.command()
@click.option("--force", is_flag=True, help="Skip confirmation prompts")
def reset(force: bool) -> None:
    """Reset database by renaming current one and creating a new blank database."""
    db_path = Path(settings.database_path).absolute()

    if not db_path.exists():
        click.echo("No database found. Nothing to reset.")
        return

    if not force and not click.confirm(
        "This will rename your current database and create a new blank one. Continue?",
        default=False,
    ):
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.parent / f"{db_path.stem}_{timestamp}{db_path.suffix}"

    try:
        db_path.rename(backup_path)
        click.echo(f"Renamed existing database to {backup_path.name}")
    except OSError as e:
        click.secho(f"Failed to rename database: {e}", fg="red")
        return

    try:
        # Reinitialize database manager to create new blank database
        _manager._initialize()
        click.secho("Created new blank database successfully.", fg="green")
    except DatabaseError as e:
        click.secho(f"Failed to create new database: {e}", fg="red")


if __name__ == "__main__":
    cli()
