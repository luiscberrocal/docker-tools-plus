# Docker Tools CLI

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
uv pip install git+https://github.com/yourusername/docker-tools.git
```

2. **Verify installation**:
```bash
docker-tools --help
```

## Usage

### Create and Execute Cleanup
```bash
docker-tools clean <name>
```
Example flow:
```bash
$ docker-tools clean reconciliation
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
docker-tools list
```
Output:
```
1: reconciliation - reconciliation[a-z_]*_postgres
2: temp-containers - temp_.+
```

### Delete a Cleanup
```bash
docker-tools delete <name>
```
Example:
```bash
$ docker-tools delete temp
Multiple matches found:
1: temp-containers
2: temp-images
Enter the ID to delete: 1
Delete cleanup 'temp-containers' (ID: 1)? [y/N]: y
```

### Show Info
```bash
docker-tools about
```
Output:
```
docker-tools v0.1.0
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
uv pip install -e . --group dev

# Run tests
make test

# Generate coverage report
make coverage

# Lint code
make lint
```

## Database Management

The SQLite database is automatically created at:
- Default: `cleanups.db`
- Custom: Path specified in `configuration.toml`

## Safety Features

1. **Confirmation Prompts** for destructive operations
2. **Separate Resource Types** (containers/volumes/images)
3. **Force Mode** (use with caution):
```bash
docker-tools clean <name> --force
```

⚠️ **Warning**: Regular expressions are powerful - test patterns with `docker ps -a`/`docker volume ls`/`docker image ls` before creating cleanup configurations.
