---
name: fastapi-sweetener
description: Add FastAPI server capabilities to an existing Python project with uvicorn, OpenAPI docs, and configuration management
allowed-tools: Read, Write, Edit, Bash, Glob, AskUserQuestion
---

# FastAPI Sweetener Skill

Add FastAPI server capabilities to an existing Python project, integrating as a CLI subcommand alongside existing functionality.

## Prerequisites

This skill assumes you already have a Python project (typically created with `/plinth:python-project-init`) with:

- Existing `pyproject.toml`
- Package directory with `__init__.py`
- Existing CLI (typically `cli.py`)

## What This Skill Adds

Adds FastAPI server capabilities to your existing project:

- **FastAPI server** with OpenAPI docs (/docs, /redoc)
- **CLI subcommand** - `{package} server` to start the API
- **Configuration management** (JSON/YAML config files)
- **CORS middleware** for web clients
- **Lifespan management** for startup/shutdown
- **Dependencies** - adds fastapi, uvicorn, click to pyproject.toml

## Files Added/Modified

**New files:**

- `{package}/server.py` - FastAPI application
- `{package}/config.py` - Configuration management
- `config.example.json` - Example configuration
- `.env.example` - Environment variable template

**Modified files:**

- `{package}/cli.py` - Adds `server` subcommand (converts to Click if needed)
- `pyproject.toml` - Adds dependencies (fastapi, uvicorn, click, pyyaml)

## Implementation Steps

### Step 1: Detect Project Structure

Use Glob and Read to discover:

1. Find `pyproject.toml` in current directory
2. Extract `project.name` and package name from pyproject.toml
3. Locate package directory (usually `{package}/` or `src/{package}/`)
4. Find existing CLI file (usually `cli.py`)
5. Read `__init__.py` or `__version__.py` to get description

If unable to detect structure, ask user for:
- PACKAGE_NAME
- PROJECT_NAME

### Step 2: Check for Existing Server

Check if server already exists:

```bash
ls {package}/server.py
```

If it exists, ask user if they want to overwrite it.

### Step 3: Gather Configuration

Ask user for (use AskUserQuestion if needed):

**Optional parameters (with defaults):**

1. **SERVER_HOST** (string) - Default: "0.0.0.0"
   - Host to bind server to

2. **SERVER_PORT** (integer) - Default: 8000
   - Port to bind server to

### Step 4: Add Server Files

Create the following files from templates in `skills/fastapi-sweetener/assets/`:

**{package}/server.py** - FastAPI application:

- Read `assets/server.py.template`
- Replace template variables
- Write to `{package}/server.py`

**{package}/config.py** - Configuration management:

- Read `assets/config.py.template`
- Replace template variables
- Write to `{package}/config.py`

**config.example.json** - Example config:

- Read `assets/config.example.json.template`
- Replace SERVER_HOST and SERVER_PORT
- Write to project root `config.example.json`

**.env.example** - Environment template:

- Read `assets/.env.example.template`
- Write to project root `.env.example`

### Step 5: Update CLI to Add Server Subcommand

This is the most critical step. The CLI needs to support subcommands.

**If cli.py uses Click:**

Add a new `@main.command()` for the server:

```python
@main.command()
@click.option('--host', default=None, help='Server host (default: from config)')
@click.option('--port', default=None, type=int, help='Server port (default: from config)')
@click.option('--reload', is_flag=True, help='Enable auto-reload for development')
@click.option('--log-level', default='info',
              type=click.Choice(['critical', 'error', 'warning', 'info', 'debug']),
              help='Logging level')
def server(host, port, reload, log_level):
    """Start the FastAPI server.

    This starts the HTTP server that provides the API.
    The server will be accessible via http://HOST:PORT
    """
    import uvicorn
    from .config import Config

    config = Config()

    # Override config with CLI options if provided
    server_host = host or config.server_host
    server_port = port or config.server_port

    print(f"Starting server at http://{server_host}:{server_port}")
    print(f"OpenAPI docs: http://{server_host}:{server_port}/docs")

    uvicorn.run(
        "{{PACKAGE_NAME}}.server:app",
        host=server_host,
        port=server_port,
        reload=reload,
        log_level=log_level
    )
```

**If cli.py uses argparse:**

Convert to Click. This is a significant change but necessary for subcommands:

1. Read existing `cli.py`
2. Identify the main() function
3. Rewrite to use Click groups:
   - Convert `ArgumentParser()` to `@click.group()`
   - Convert existing logic to `@main.command()` named appropriately
   - Add the `server` subcommand as shown above
4. Use Edit tool to update the file

### Step 6: Update pyproject.toml Dependencies

Add required dependencies to pyproject.toml:

Use Edit tool to add to the `dependencies` array:

```toml
dependencies = [
    # ... existing deps ...
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "click>=8.0",
    "pyyaml>=6.0",
]
```

### Step 7: Install Dependencies

Run uv sync to install new dependencies:

```bash
uv sync
```

### Step 8: Create Config File

Guide user to create config from example:

```bash
cp config.example.json config.json
```

### Step 9: Verification & Next Steps

Provide verification commands:

```bash
# Verify CLI still works
uv run {package} --version

# Start development server
uv run {package} server --reload

# Open in browser
open http://localhost:{port}/docs
```

Tell user:

1. Server added as `{package} server` subcommand
2. Configure via `config.json` (copy from config.example.json)
3. Add API endpoints to `{package}/server.py`
4. OpenAPI docs available at `/docs` and `/redoc`
5. Use `/plinth:macos-launchd-service` to set up auto-start

## Template Variable Reference

| Variable | Example | Source |
|----------|---------|--------|
| `{{PROJECT_NAME}}` | "Temoa" | From pyproject.toml or user input |
| `{{PACKAGE_NAME}}` | "temoa" | Detected from directory structure |
| `{{PACKAGE_NAME_UPPER}}` | "TEMOA" | Derived from PACKAGE_NAME |
| `{{DESCRIPTION}}` | "Semantic search" | From __init__.py or user input |
| `{{SERVER_HOST}}` | "0.0.0.0" | User input or default |
| `{{SERVER_PORT}}` | "8000" | User input or default |

## Example Execution

**User request:** "Add FastAPI to my CLI project"

**Detected:**
- PROJECT_NAME: "MyProject" (from pyproject.toml)
- PACKAGE_NAME: "myproject" (from directory structure)
- Existing cli.py with Click

**User provides:**
- SERVER_PORT: 8080 (default: 8000)

**Result:**

Files added:
- `myproject/server.py`
- `myproject/config.py`
- `config.example.json`
- `.env.example`

Files modified:
- `myproject/cli.py` (added `server` command)
- `pyproject.toml` (added fastapi, uvicorn, etc.)

Usage:
```bash
myproject --help          # Shows all subcommands
myproject server          # Starts FastAPI on port 8080
myproject server --reload # Development mode with auto-reload
```

## Idempotency

The skill should be safe to run multiple times:

- Check if `server.py` exists before creating
- Ask user before overwriting existing files
- Only add dependencies if not already present
- Don't duplicate CLI commands

## Common Issues

### CLI Not Using Click

If the existing CLI uses argparse, the skill will convert it to Click. This is necessary for subcommands. The conversion:

- Preserves existing CLI functionality
- Moves it to a default command or appropriately named subcommand
- Adds the `server` subcommand

Warn the user about this change.

### Port Already in Use

If the default port is occupied, user can override:

```bash
myproject server --port 8001
```

### Missing Config File

Server requires `config.json`. If missing:

```bash
cp config.example.json config.json
```

Edit values as needed.

## What NOT to Do

- Don't create this from scratch - requires existing project
- Don't skip the CLI conversion if needed - subcommands require Click
- Don't overwrite server.py without asking
- Don't add emojis to any files
- Don't run python directly - always use `uv run`
- Don't modify README.md or documentation files (user does this)

## Post-Addition Customization

After adding FastAPI, users typically:

1. Edit `config.json` with their specific configuration
2. Add API endpoints to `server.py`
3. Update tests to include API endpoint tests
4. Set up launchd service using `/plinth:macos-launchd-service`
5. Document API endpoints in README.md

## Integration with Other Skills

Works well with:

- `/plinth:python-project-init` - Creates the base project first
- `/plinth:macos-launchd-service` - Auto-start the server
- `/plinth:session-wrapup` - Document the addition
