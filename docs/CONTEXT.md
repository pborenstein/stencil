---
phase: 1
phase_name: Obsidian pilot
updated: 2026-10-03
last_commit: 184ff19
last_entry: 5
---

## Current Focus

The skill is installed and live-validated on two templates: Gatsby
#64317 into 002375.xyz (folio) and 002374.xyz (chapbook), both build
gates clean, chapter text byte-identical. The three pilot findings
are confirmed template-independent; Phase 1 proper (Obsidian ingest +
post emit) follows them.

## Active Tasks

- [ ] emit-chapters: honor a JSON-level unit `title` over the
      heading-derived default (SKILL.md documents the JSON path)
- [ ] ingest-gutenberg: drop or flag TOC-shell units (Gatsby's
      numeral TOC became 9 empty units, front matter trapped in one)
- [ ] emit-chapters probe: don't lose frontmatter keys when
      chapters/ is empty (folio re-emit probed `title,order` only)
- [ ] SKILL.md: note per-template front-matter routing targets
      (folio: about page; chapbook: homepage foreword slot)
- [ ] Obsidian ingest command + post emitter (Phase 1 checklist in
      [IMPLEMENTATION.md](IMPLEMENTATION.md))

## Blockers

None.

## Context

- Skill installed at `~/.zcode/skills/stencil/`; CLI via
  `uv run --project ~/projects/stencil stencil ...`.
- Pilot detail: Entries 4–5 in
  [chronicles/phase-1-obsidian.md](chronicles/phase-1-obsidian.md).
- Gatsby headings: indented bare roman numerals on CRLF;
  `--extra-heading '^\s*[IVXLCDM]{1,7}\s*$'` recovers all 9.
- Probe fidelity is good with demo chapters present; degrades only
  when chapters/ is empty.
- Site checkouts hold uncommitted pilot work; artifacts in
  `/tmp/stencil-run/64317/`.

## Next Session

Close the three CLI findings (small, well-scoped; the title one now
confirmed twice), then start the Obsidian ingest command.
