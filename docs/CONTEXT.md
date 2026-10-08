---
phase: 1
phase_name: Obsidian pilot
updated: 2026-10-07
last_commit: c2018ba
last_entry: 6
---

## Current Focus

Skill live-validated on two templates (Gatsby #64317 into 002375.xyz
folio and 002374.xyz chapbook; build gates clean, text byte-identical).
The three pilot findings are template-independent; Phase 1 proper
(Obsidian ingest + post emit) follows them.

## Active Tasks

- [x] emit-chapters: honor a JSON-level unit `title` over the
      heading-derived default (SKILL.md documents the JSON path)
- [x] ingest-gutenberg: drop or flag TOC-shell units (Gatsby's
      numeral TOC became 9 empty units, front matter trapped in one)
- [x] emit-chapters probe: don't lose frontmatter keys when
      chapters/ is empty (folio re-emit probed `title,order` only)
- [x] SKILL.md: note per-template front-matter routing targets
      (folio: about page; chapbook: homepage foreword slot)
- [ ] Obsidian ingest command + post emitter (Phase 1 checklist in
      [IMPLEMENTATION.md](IMPLEMENTATION.md))

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

Close the three CLI findings (small, well-scoped; the title one now
confirmed twice), then start the Obsidian ingest command.
