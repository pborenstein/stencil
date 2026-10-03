# Stencil Development Guide

Development guide for AI-assisted sessions on this project.

## Project Overview

Install content into mimeo sites from source material (Project Gutenberg
books today; Obsidian pages and site-as-model later).

### Key Principles

- Skill-based: judgment decisions are made by the LLM; the Python
  helpers are deterministic and never guess
- Helpers are CLI-runnable and congruent with mimeo's code form --
  not ad-hoc scripts
- Helpers report what they cannot classify; the agent decides
- The site build is the acceptance gate

### Technology Stack

- **Language**: Python >=3.11
- **Package Manager**: uv
- **Testing**: pytest
- **Type Checking**: mypy
- **Linting**: ruff

## Python Environment

### Setup

```bash
# Install dependencies
uv sync

# Verify installation
uv run python --version
uv run stencil --help
```

### Running Commands

```bash
# Run the CLI
uv run stencil [args]

# Run tests
uv run pytest

# Type checking
uv run mypy stencil

# Linting
uv run ruff check stencil
```

## Architecture

- `stencil/gutenberg.py` -- PG plain text to stencil JSON (parse,
  reflow, drop_toc); warnings carry what the split could not classify
- `stencil/emit.py` -- chapter emitter: probe the site, imitate its
  conventions, write chapters/colophon/metadata/annotations
- `stencil/cli/` -- Click commands, one module per command, mirroring
  mimeo's cli package
- `stencil-work/SKILL.md` -- the agent skill that drives the CLI; the
  decisions (letter routing, display titles, preamble routing,
  annotation text) live there, not in the code
- `tests/` -- pytest suite; `tests/utils.py` holds the site fixture

## Development Workflow

### Session Pickup

At the start of each session: read `docs/CONTEXT.md` first, then the
current phase in `docs/IMPLEMENTATION.md`. Use the `session-pickup`
skill to automate this.

### Session Wrapup

Update tracking docs, add a chronicle entry, document decisions in
`docs/DECISIONS.md`, commit. Use the `session-wrapup` skill.

### Planning Approach

"Plan like waterfall, implement in agile" -- detailed upfront planning
in IMPLEMENTATION.md, iterative implementation, decisions logged with
rationale.

## Documentation System

| File | Purpose |
|------|---------|
| `docs/CONTEXT.md` | Current session state (hot state, 30-50 lines) |
| `docs/IMPLEMENTATION.md` | Phase-based implementation plan and task tracking |
| `docs/DECISIONS.md` | Architectural decision registry |
| `docs/chronicles/phase-X-name.md` | Detailed session-by-session history |

## Code Style

- Follow PEP 8; type hints on all functions; docstrings for public APIs
- Library modules raise typed exceptions; the CLI converts them to
  Click errors and nonzero exits
- Write tests for new functionality; the site build remains the
  end-to-end gate

## What NOT to Do

- Don't put judgment (titles, deks, annotation text, preamble routing)
  into the helpers
- Don't run python directly -- this is a uv shop, always `uv run`
- Don't add emojis to files
- Don't use pip or poetry (use uv only)
