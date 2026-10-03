---
phase: 1
phase_name: Obsidian pilot
updated: 2026-10-03
last_commit: 553ed20
last_entry: 3
---

## Current Focus

The repo now has mimeo's code form (DEC-009): a uv/hatchling
package with a Click CLI, driven by the SKILL.md judgment layer.
Phase 1 (Obsidian pilot) is open, prefaced by installing the skill
and a live Gutenberg run.

## Active Tasks

- [ ] Install: `stencil-work/` → `~/.zcode/skills/stencil/`; CLI via
      `uv run --project ~/projects/stencil stencil ...`
- [ ] One live Gutenberg edition end-to-end through the installed skill
- [ ] Obsidian ingest command + post emit (Phase 1 checklist in
      [IMPLEMENTATION.md](IMPLEMENTATION.md))

## Blockers

None.

## Context

- Code form (DEC-009): `stencil/gutenberg.py` + `stencil/emit.py`
      (typed exceptions) under `stencil/cli/` (one Click module per
      command, mimeo's form). `uv run stencil ingest-gutenberg ...`,
      `uv run stencil emit-chapters ...`. 39 tests; mypy and ruff
      clean; CLAUDE.md documents the form.
- Skill layer: `stencil-work/SKILL.md` drives the CLI; decisions
      (letters, titles, preamble routing, annotations) live there.
- Ingest `warnings` + `--extra-heading` (DEC-007) unchanged in
      behavior; validated again through the CLI (Frankenstein 28
      units on chapbook, 33 files; P&P 61 units).
- DEC-003 superseded, DEC-008 amended by DEC-009.

## Next Session

Commit the restructure (uncommitted in the working tree), install
the skill, drive one real Gutenberg edition through it, then start
the Obsidian pilot.
