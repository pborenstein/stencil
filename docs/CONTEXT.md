---
phase: 1
phase_name: Obsidian pilot
updated: 2026-10-03
last_commit: 712326c
last_entry: 4
---

## Current Focus

The skill is installed and live-validated: Gatsby #64317 ran
end-to-end into 002375.xyz (folio), build gate clean, chapter text
byte-identical. The pilot surfaced three CLI/skill contract findings,
queued as tasks; Phase 1 proper (Obsidian ingest + post emit) follows.

## Active Tasks

- [ ] emit-chapters: honor a JSON-level unit `title` over the
      heading-derived default (SKILL.md documents the JSON path)
- [ ] ingest-gutenberg: drop or flag TOC-shell units (Gatsby's
      numeral TOC became 9 empty units, front matter trapped in one)
- [ ] emit-chapters probe: don't lose frontmatter keys when
      chapters/ is empty (folio re-emit probed `title,order` only)
- [ ] Obsidian ingest command + post emitter (Phase 1 checklist in
      [IMPLEMENTATION.md](IMPLEMENTATION.md))

## Blockers

None.

## Context

- Skill installed at `~/.zcode/skills/stencil/`; CLI via
  `uv run --project ~/projects/stencil stencil ...`. Auto-trigger
  untested (the pilot session followed SKILL.md as a document).
- Pilot detail and findings: Entry 4 in
  [chronicles/phase-1-obsidian.md](chronicles/phase-1-obsidian.md).
- Gatsby heading style: indented bare roman numerals on CRLF;
  `--extra-heading '^\s*[IVXLCDM]{1,7}\s*$'` recovers all 9 —
  verify match count in book.txt before trusting it.
- Site work for the pilot is uncommitted in
  `~/projects/mimeo-sites/002375.xyz` (user's call); run artifacts
  in `/tmp/stencil-run/64317/`.

## Next Session

Close the three pilot findings (small, well-scoped CLI work) or go
straight to the Obsidian ingest command; the findings also block
clean retitling flows, so they are the better first move.
