# Docker Tools Plus

[![PyPI version](https://img.shields.io/pypi/v/docker-tools-plus)](https://pypi.org/project/docker-tools-plus/)

A command-line tool for managing Docker container cleanups using predefined regular expression patterns.

## Features

- 🐳 Create named cleanup configurations with regular expressions
- 🗑️ Clean containers, volumes, and images matching patterns
- 💾 SQLite database for persistent configuration storage
- 🔍 Interactive prompts for multiple matches
- 🛡️ Safety confirmations before destructive operations

## Installation

1. **Install using uv**:
```bash
uv pip install git+https://github.com/yourusername/docker-tools-plus.git
```

2. **Verify installation**:
```bash
docker-tools-plus --help
```

## Usage

### Create and Execute Cleanup
```bash
docker-tools-plus clean <name> [--force]
```
- Use `--force` to skip all confirmation prompts
- Automatically cleans all resource types without asking

Example flow without `--force`:
```bash
$ docker-tools-plus clean reconciliation
No cleanup found matching 'reconciliation'
Please enter a regular expression: reconciliation[a-z_]*_postgres

Created new cleanup config:
ID: 1 | Name: reconciliation | Pattern: reconciliation[a-z_]*_postgres

Clean containers? [Y/n]: y
Clean volumes? [Y/n]: y
Clean images? [Y/n]: y
```

Example with `--force`:
```bash
$ docker-tools-plus clean reconciliation --force
Created new cleanup config:
ID: 1 | Name: reconciliation | Pattern: reconciliation[a-z_]*_postgres
Cleaning containers... done
Cleaning volumes... done
Cleaning images... done
```

### List All Cleanups
```bash
docker-tools-plus list
```
Output:
```
1: reconciliation - reconciliation[a-z_]*_postgres
2: temp-containers - temp_.+
```

### Delete a Cleanup
```bash
docker-tools-plus delete <name>
```
Example:
```bash
$ docker-tools-plus delete temp
Multiple matches found:
1: temp-containers
2: temp-images
Enter the ID to delete: 1
Delete cleanup 'temp-containers' (ID: 1)? [y/N]: y
```

### Show Info
```bash
docker-tools-plus about
```
Displays application information in a formatted panel with:
- Application name and version (centered)
- Database location with file existence indicator (✓ if exists, ✗ if missing)
- Description

Example panel:
```
┌ About ───────────────────────────────────────────────────┐
│                                                          │
│             docker-tools v0.4.2                          │
│                                                          │
│  Database location: /path/to/cleanups.db ✓               │
│                                                          │
│  CLI tool for managing Docker container cleanups          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Reset Database
```bash
docker-tools-plus reset
```
Creates a timestamped backup of the current database and creates a new blank one. Requires confirmation unless `--force` is used.

Example:
```bash
$ docker-tools-plus reset
This will rename your current database and create a new blank one. Continue? [y/N]: y
Renamed existing database to cleanups_20240614_123456.db
Created new blank database successfully.
```

## Configuration

Create `configuration.toml` to customize:
```toml
[database]
path = "custom_cleanups.db"
```

## Development

```bash
# Install dev dependencies
uv pip install -e '.[dev]'


# Run tests
make test

# Generate coverage report
make cov

# Lint code
make lint
```

## Database Management

The default application path is `~/.config/docker-tools-plus/`. 

This path will probably not work on Windows, so you can specify a custom path in `configuration.toml`:

The SQLite database is automatically created at:
- Default: `docker_tools_plus.db`
- Custom: Path specified in `configuration.toml`

## Safety Features

1. **Confirmation Prompts** for destructive operations
   - Always asks before cleaning each resource type (containers/volumes/images)
   - Can be skipped with `--force` option
2. **Separate Resource Types** (containers/volumes/images)
3. **Force Mode** (use with caution):
   - Skips all confirmation prompts
   - Automatically cleans all resource types
   - Requires explicit `--force` flag:
```bash
docker-tools-plus clean <name> --force
```

⚠️ **Warning**: Regular expressions are powerful - test patterns with `docker ps -a`/`docker volume ls`/`docker image ls` before creating cleanup configurations.
