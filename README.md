# Docker Tools Plus

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
docker-tools-plus clean <name>
```
Example flow:
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
Output:
```
docker-tools-plus v0.1.0
Database location: /path/to/cleanups.db
CLI tool for managing Docker container cleanups
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
2. **Separate Resource Types** (containers/volumes/images)
3. **Force Mode** (use with caution):
```bash
docker-tools-plus clean <name> --force
```

⚠️ **Warning**: Regular expressions are powerful - test patterns with `docker ps -a`/`docker volume ls`/`docker image ls` before creating cleanup configurations.
