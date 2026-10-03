# Phase 1: Obsidian Pilot

## Entry 3: mimeo-congruent package form; the skill drives the CLI (2026-10-03)

**What**: Restructured the repo from standalone helper scripts into a uv/hatchling Click CLI package following mimeo's code form, via the plinth python-project-init skill. Re-validated the full Gutenberg path through the new command surface.

**Why**: Design principle stated by the user: stencil is skill-based with decisions made by the LLM, but the Python helpers must be CLI-runnable, congruent, and not ad-hoc.

**How**:

- `stencil/` package: `gutenberg.py` and `emit.py` as typed library modules raising `GutenbergError`/`EmitError`; `cli/` subpackage with one Click module per command (`ingest-gutenberg`, `emit-chapters`), mirroring mimeo's cli package
- pyproject.toml with mimeo's tooling values; dev group pytest/mypy/ruff; CLAUDE.md from the plinth template; tests converted to pytest function style plus CliRunner CLI tests (39 passing; mypy and ruff clean)
- `stencil-work/` reduced to SKILL.md, which drives the CLI (`uv run --project ~/projects/stencil stencil ...`); its closing rule encodes the principle: mechanical capabilities land as CLI modules, decisions land in the skill text
- Port caught one real bug: the emit-chapters command function shadowed the library import (would recurse); fixed with an aliased import
- End-to-end through the CLI: Frankenstein on a fresh chapbook copy (28 units, probe, emit, 33 files, annotations rendered); P&P `--extra-heading` (61 units)

**Decisions**:

- DEC-009: mimeo-congruent Click CLI package; the skill drives the CLI (supersedes DEC-003, amends DEC-008)

**Files**: aadffef (`stencil/`, `tests/`, `pyproject.toml`, `CLAUDE.md`, `uv.lock`, `stencil-work/SKILL.md`, docs)
