import click
import logging
import subprocess
from typing import List
from . import __version__
from .database import (
    Cleanup,
    get_cleanup_by_name,
    list_cleanups,
    delete_cleanup,
    create_cleanup,
    init_db
)
from .settings import settings
from .exceptions import DockerToolsError

logger = logging.getLogger(__name__)

@click.group()
def cli():
    """Docker cleanup management tool"""
    init_db()

@cli.command()
@click.argument('name')
@click.option('--force', is_flag=True, help="Skip confirmation prompts")
def clean(name, force):
    """Execute cleanup by name.
    
    If no exact match is found, you'll be prompted to create a new configuration.
    """
    try:
        cleanups: List[Cleanup] = get_cleanup_by_name(name)
        
        if not cleanups:
            click.echo(f"No cleanup found matching '{name}'")
            regex = click.prompt("Please enter a regular expression for the cleanup")
            cleanup = create_cleanup(name, regex)
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
        click.secho(f"Error: {e}", fg='red')

def _execute_cleanup(cleanup: Cleanup, force: bool):
    """Run docker cleanup commands based on the selected configuration"""
    commands = {
        'containers': f"docker ps -a | grep -E '{cleanup.regular_expression}' | awk '{{print $1}}' | xargs docker rm",
        'volumes': f"docker volume ls | grep -E '{cleanup.regular_expression}' | awk '{{print $2}}' | xargs docker volume rm",
        'images': f"docker image ls | grep -E '{cleanup.regular_expression}' | awk '{{print $3}}' | xargs docker image rm"
    }
    
    for resource, cmd in commands.items():
        if force or click.confirm(f"Clean {resource} using pattern '{cleanup.regular_expression}'?", default=True):
            try:
                subprocess.run(cmd, shell=True, check=True)
                click.echo(f"Successfully cleaned {resource}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Error cleaning {resource}: {e}")
                click.secho(f"Failed to clean {resource}", fg='red')

@cli.command(name='list')
def list_cleanups():
    """List all registered cleanups"""
    try:
        cleanups = list_cleanups()
        if not cleanups:
            click.echo("No cleanups found")
            return
        for cleanup in cleanups:
            click.echo(f"{cleanup.id}: {cleanup.name} - {cleanup.regular_expression}")
    except DockerToolsError as e:
        logger.error(str(e))
        click.secho(f"Error: {e}", fg='red')

@cli.command()
@click.argument('name')
def delete(name):
    """Delete a cleanup configuration"""
    try:
        cleanups = get_cleanup_by_name(name)
        
        if not cleanups:
            click.secho(f"No cleanups found matching '{name}'", fg='red')
            return
        
        if len(cleanups) > 1:
            click.echo("Multiple matches found:")
            for cleanup in cleanups:
                click.echo(f"{cleanup.id}: {cleanup.name}")
            selected_id = click.prompt("Enter the ID to delete", type=int)
            selected = next((c for c in cleanups if c.id == selected_id), None)
            if not selected:
                click.secho("Invalid ID", fg='red')
                return
        else:
            selected = cleanups[0]
        
        if click.confirm(f"Delete cleanup '{selected.name}' (ID: {selected.id})?", default=False):
            delete_cleanup(selected.id)
            click.secho("Cleanup deleted successfully", fg='green')
    except DockerToolsError as e:
        logger.error(str(e))
        click.secho(f"Error: {e}", fg='red')

@cli.command()
def about():
    """Show application information"""
    click.echo(f"docker-tools v{__version__}")
    click.echo(f"Database location: {settings.database_path}")
    click.echo("CLI tool for managing Docker container cleanups")

if __name__ == '__main__':
    cli()
