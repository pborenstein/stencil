# FastAPI Project Scaffold - Usage Guide

Generate a production-ready FastAPI project with modern Python tooling.

## What It Creates

A complete FastAPI project structure following best practices from temoa and apantli projects:

```
your-project/
├── pyproject.toml          # uv-based project config with FastAPI dependencies
├── config.example.json     # Example configuration file
├── your_package/
│   ├── __init__.py         # Package initialization
│   ├── __version__.py      # Version management via importlib.metadata
│   ├── __main__.py         # CLI entry point with argparse + uvicorn
│   ├── server.py           # FastAPI app with OpenAPI, CORS, lifespan
│   └── config.py           # Configuration loader (JSON/YAML support)
├── .gitignore              # Python/uv/IDE ignores
├── .env.example            # Environment variables template
└── README.md               # Project documentation
```

## Features

**FastAPI Application:**

- OpenAPI documentation at `/docs` (Swagger UI)
- Alternative docs at `/redoc` (ReDoc)
- CORS middleware configured
- Lifespan context manager for startup/shutdown
- Health check endpoint

**CLI Entry Point:**

- Argparse-based command-line interface
- `--host`, `--port`, `--reload`, `--log-level` options
- `--version` flag
- Custom logging configuration
- Network interface discovery

**Configuration Management:**

- Searches multiple locations (XDG standard)
- Supports both JSON and YAML formats
- Environment variable override
- Helpful error messages

**Version Management:**

- Single source of truth in `pyproject.toml`
- Runtime access via `importlib.metadata`
- Development fallback version

**Modern Python Tooling:**

- uv package manager
- pyproject.toml for project config
- Development dependencies (pytest, mypy, ruff)
- Hatchling build backend

## Usage

In Claude Code:

```
/fastapi-scaffold
```

Or:

```
Run the fastapi-scaffold skill
```

You'll be prompted for:

- **Project Name** (e.g., "MyAPI") - display name
- **Package Name** (e.g., "myapi") - Python package name
- **Description** - one-line project description
- **Port** (optional, default: 8000) - server port
- **Python Version** (optional, default: ">=3.11") - minimum Python version

## Quick Start After Generation

```bash
cd your-project

# Install dependencies
uv sync

# Create configuration
cp config.example.json config.json

# Run development server
uv run your-package --reload
```

The server will be available at:

- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## What Gets Generated

### FastAPI Application (`server.py`)

- Lifespan context manager for startup/shutdown
- CORS middleware (allow all origins for development)
- OpenAPI configuration (title, description, version)
- Root endpoint with API info
- Health check endpoint
- Logging configuration

### CLI Entry Point (`__main__.py`)

- Argparse configuration
- Host/port/reload options
- Log level control
- Version display
- Uvicorn runner with custom logging

### Configuration (`config.py`)

- Multi-location search:
  1. `{PACKAGE}_CONFIG_PATH` environment variable
  2. `~/.config/{package}/config.json` (XDG)
  3. `~/.{package}.json`
  4. `./config.json` (development)
- JSON and YAML support
- Type-safe property accessors
- Helpful error messages

### Version Management (`__version__.py`)

- Uses `importlib.metadata.version()` for installed package
- Falls back to development version if not installed
- Single source of truth in `pyproject.toml`

## Project Configuration

The generated project uses `pyproject.toml` with:

**Core dependencies:**

- fastapi >= 0.104.0
- uvicorn[standard] >= 0.24.0
- pydantic >= 2.0
- python-dotenv >= 1.0.0
- pyyaml >= 6.0

**Dev dependencies:**

- pytest >= 7.0
- mypy >= 1.0
- ruff >= 0.1.0

## Next Steps After Generating

1. **Customize configuration:**
   ```bash
   cp config.example.json config.json
   # Edit config.json with your settings
   ```

2. **Add API endpoints:**
   - Edit `{package}/server.py`
   - Add route handlers to the FastAPI app

3. **Add dependencies:**
   ```bash
   # Edit pyproject.toml dependencies
   uv sync
   ```

4. **Set up auto-start service:**
   ```
   /macos-launchd-service
   ```

5. **Initialize git:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: FastAPI project"
   ```

## Comparison with Manual Setup

**Manual approach:**

- Research FastAPI best practices
- Set up project structure
- Configure uvicorn
- Add CORS middleware
- Set up configuration management
- Create CLI with argparse
- Configure logging
- Write README

**Time:** 2-3 hours

**With this skill:**

- Answer 3-4 questions
- Run `uv sync`

**Time:** 2-3 minutes

## Pattern Source

This scaffold extracts common patterns from:

- [temoa](https://github.com/pborenstein/temoa) - Semantic search server
- [apantli](https://github.com/pborenstein/apantli) - LLM proxy

Both are production FastAPI services using uv, uvicorn, and modern Python tooling.

## Why This Pattern?

**FastAPI:**

- Automatic OpenAPI documentation
- Type checking with Pydantic
- Async support
- Fast and modern

**uv:**

- Fast package installation
- Lock file for reproducibility
- No activation needed (`uv run`)
- Modern replacement for pip/venv

**Lifespan:**

- Clean startup/shutdown
- Proper resource management
- State initialization

**Configuration:**

- XDG-compliant paths
- Multiple format support
- Environment-agnostic

## License

Part of the plinth Claude Code plugin. MIT License.
