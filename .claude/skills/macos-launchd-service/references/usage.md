# macOS launchd Service Setup

Automatically generate complete launchd service infrastructure for Python applications on macOS.

## What This Does

Creates a production-ready service that:

- **Auto-starts** on login (`RunAtLoad: true`)
- **Auto-restarts** on crash (`KeepAlive: true`)
- **Logs** stdout/stderr to `~/Library/Logs/`
- **Provides** development mode with auto-reload
- **Includes** log viewing and management helpers

## Generated Files

```
your-project/
├── launchd/
│   ├── install.sh                    # Automated installer
│   ├── uninstall.sh                  # Service uninstaller
│   └── yourapp.plist.template       # Service configuration
├── dev.sh                            # Development mode
└── view-logs.sh                      # Log viewer
```

## Requirements

- macOS 10.10+ with launchd
- Python project using uv package manager
- Virtual environment created (`.venv/`)
- CLI command defined in `pyproject.toml`

## Quick Start

1. **Run the skill** in your project directory
2. **Answer prompts** (project name, port, commands)
3. **Review generated files**
4. **Install service**: `./launchd/install.sh`
5. **Access your app**: `http://localhost:{port}`

## Usage Example

```bash
# In your project directory
claude-code

# Use the skill (exact invocation TBD)
> /macos-launchd-service

# Answer prompts:
Domain: dev.pborenstein
Project name: temoa
Port: 4001
CLI command: temoa server --host 0.0.0.0 --port 4001
Dev command: temoa server --reload
Process name: temoa server

# Files generated!
# Install the service:
./launchd/install.sh

# Your service is now running
```

## What Gets Generated

### install.sh

Automated installer that:

- Detects environment (username, paths, venv)
- Validates dependencies installed
- Generates service plist from template
- Installs to `~/Library/LaunchAgents/`
- Loads and starts service
- Shows access URLs and management commands

### uninstall.sh

Service uninstaller that:

- Checks if service exists
- Shows what will be removed
- Asks for confirmation
- Stops running service if active
- Removes plist file
- Confirms uninstall complete

### {project}.plist.template

Service configuration template with:

- Auto-start on login
- Auto-restart on crash
- Environment variables (PATH with venv)
- Logging configuration
- Working directory

### dev.sh

Development mode script with subcommands:

- `./dev.sh` -- stops service, runs with auto-reload, caffeinate
- `./dev.sh start` -- start the launchd service
- `./dev.sh stop` -- stop the launchd service
- `./dev.sh status` -- show service and port status
- On exit: service stays stopped, no prompt

### view-logs.sh

Log viewer with modes:

```bash
./view-logs.sh          # All logs
./view-logs.sh app      # stdout only
./view-logs.sh error    # stderr only
```

## Service Management

After installation, use `dev.sh` subcommands:

```bash
./dev.sh status   # Show service and port status
./dev.sh stop     # Stop the service
./dev.sh start    # Start the service
./dev.sh          # Dev mode (stops service, runs with reload)
```

**Uninstall**:

```bash
./launchd/uninstall.sh
```

These use the modern `launchctl bootstrap/bootout` API under the hood.

## Development Workflow

**Start development**:

```bash
./dev.sh
```

This stops the production service and runs with auto-reload.

**Stop development** (Ctrl+C):

- Service stays stopped -- no prompt
- Run `./dev.sh start` when you're ready to restore the service

**View logs while developing**:

```bash
# In another terminal
./view-logs.sh
```

## Network Access

Services bind to `0.0.0.0`, making them accessible:

- **Localhost**: `http://localhost:{port}`
- **LAN**: `http://{your-ip}:{port}`
- **Tailscale**: `http://{tailscale-ip}:{port}`

To restrict to localhost only, edit the plist template and change `--host 0.0.0.0` to `--host 127.0.0.1`.

## Troubleshooting

**Service won't start**:

```bash
# Check error logs
tail ~/Library/Logs/yourapp.error.log

# Verify venv exists
ls .venv/bin/python3

# Check if port is in use
lsof -i :{port}
```

**Changes not taking effect**:

After modifying the plist template, reinstall:

```bash
./launchd/install.sh
```

**Permission errors**:

```bash
# Ensure LaunchAgents directory exists
mkdir -p ~/Library/LaunchAgents
```

## Examples

See real-world usage in:

- [temoa](https://github.com/pborenstein/temoa) - Semantic search server on port 4001
- [apantli](https://github.com/pborenstein/apantli) - LLM proxy server on port 4000

## Why launchd?

launchd is macOS's native service manager:

- **Built-in** - No extra dependencies
- **Automatic** - Starts on login, restarts on crash
- **Logging** - Captures stdout/stderr automatically
- **Standard** - Follows macOS conventions
- **Reliable** - System-level service management

## Technical Details

**Service naming**: `{domain}.{project}` (e.g., `dev.pborenstein.temoa`)

- Best practice: Use owned domain in reverse notation
- Default: `dev.{username}` if no owned domain specified
- Examples: `dev.pborenstein`, `com.pborenstein`, `dev.philip`

**Log location**: `~/Library/Logs/{project}.log` and `{project}.error.log`

**Service type**: LaunchAgent (runs as user, not root)

**Configuration**: Uses plist templates with runtime substitution

## See Also

- [SKILL.md](SKILL.md) - Implementation guide for LLMs
- [Apple launchd documentation](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)
