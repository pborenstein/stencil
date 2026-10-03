---
phase: 1
phase_name: Obsidian pilot
updated: 2026-10-03
last_commit: TBD
last_entry: 2
---

## Current Focus

Phase 0 (Foundation) is complete and committed. Phase 1 is the
Obsidian pilot, prefaced by installing the skill and running one real
Gutenberg edition through it.

## Active Tasks

- [ ] Install the skill: `stencil-work/` → `~/.zcode/skills/stencil/`
- [ ] One live Gutenberg edition end-to-end through the installed skill
- [ ] Obsidian ingest helper + post emitter (see Phase 1 checklist in
      [IMPLEMENTATION.md](IMPLEMENTATION.md))

## Blockers

None.

## Context

- `stencil-work/` is the installable skill dir (DEC-008): SKILL.md +
      `ingest_gutenberg.py` + `emit_chapters.py`. 31 tests:
      `python3 -m unittest discover -s tests`.
- Ingest reports `warnings` (DEC-002); `--extra-heading REGEX` teaches
      the split an edition's heading style (DEC-007).
- Validated: Frankenstein #84 across chapbook/folio/pamphlet (33 files
      each), P&P #1342 (61 units via `--extra-heading`), Republic #1497
      (Jowett Introduction reported in the preamble; the pre-fix
      20-unit output was silently corrupt). pandoc-resume refused
      cleanly.
- pamphlet's homepage title is page frontmatter, not `metadata.js` —
      the skill's sweep step covers it.
- Remote: `github.com/pborenstein/stencil`. The mimeo checkout is
      clean; stencil work happens here only.

## Next Session

Install the skill and drive one real Gutenberg edition through it as
the live test, then start the Obsidian pilot per the Phase 1 checklist.
