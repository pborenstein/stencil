---
phase: 0
phase_name: Foundation
updated: 2026-10-03
last_commit: f77f3e8
last_entry: 1
---

## Current Focus

Turning stencil into a standalone repo. The Gutenberg reading-edition path works and is validated, but this repo tracks only the README so far.

## Active Tasks

- [ ] Decide where the helpers live and bring `ingest_gutenberg.py` / `emit_chapters.py` into this repo
- [ ] Write the agent skill (SKILL.md) that maps a prose brief to helper invocations
- [ ] Add `.gitignore` and a git remote
- [ ] Add tests for the two helpers

## Blockers

None.

## Context

- The helpers exist only as untracked files in `/Users/philip/projects/mimeo/stencil/`, next to a README identical to this repo's. The README says "this directory", which is not yet true here.
- Validation so far: Frankenstein (PG #84) against eleventy-chapbook only. Folio, pamphlet, and the pandoc templates are unvalidated.
- Helpers are stdlib-only Python 3; no venv needed to run them (DEC-003).
- The tracking docs are uncommitted as of this update.

## Next Session

Settle the helper location question first; everything else in Phase 0 (skill, tests, further validation) depends on the code being tracked here. Then see the Phase 0 checklist in `docs/IMPLEMENTATION.md`.
