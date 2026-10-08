---
phase: 1
phase_name: Obsidian pilot
updated: 2026-10-08
last_commit: 0c5187c
last_entry: 7
---

## Current Focus

Phase 1 code and skill text are complete: `ingest-obsidian`,
`emit-post`, and the skill sections for front-matter routing and
agent-written excerpt/date/tags are merged. What remains is a live
run of an Obsidian page onto a real blog-style site (build gate), plus
the chronicle entry and phase close-out.

## Active Tasks

- [x] Pilot findings closed (unit title override, TOC-shell units,
      empty-chapters probe, front-matter routing note)
- [x] `ingest-obsidian` and `emit-post` (DEC-004 form)
- [x] Skill text for excerpt, date, tags
- [ ] Live run: one Obsidian page onto a blog-style site; confirm
      the inferred image directory and public image URL against a
      real build, then close Phase 1

## Blockers

None.

## Context

- Skill at `~/.zcode/skills/stencil/`; CLI: `uv run --project ~/projects/stencil stencil ...`
- Pilot detail: Entries 4–5 in
  [chronicles/phase-1-obsidian.md](chronicles/phase-1-obsidian.md).
- handoff/plinth skills vendored in `.claude/skills/` for cloud
  sessions (DEC-010); canonical copies in `~/projects/claude-plugins`.
- Idea, not a task: epub export from the ingest JSON (reading notes:
  amoxtli vault, `Reading long prose in a browser`).
- Gatsby headings: indented bare roman numerals on CRLF;
  `--extra-heading '^\s*[IVXLCDM]{1,7}\s*$'` recovers all 9.
- Site checkouts hold uncommitted pilot work; run artifacts in
  `/tmp/stencil-run/64317/`.

## Next Session

Run the live Obsidian-to-blog pass, fix what the build gate finds,
write the chronicle entry, and close Phase 1.
