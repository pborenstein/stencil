# Implementation

Phase progress for stencil. Session pickup reads [CONTEXT.md](CONTEXT.md) first; decision rationale lives in [DECISIONS.md](DECISIONS.md); session history lives in [chronicles/](chronicles/).

## Phase Overview

| # | Name | Status | Commits |
|---|------|--------|---------|
| 0 | Foundation | Complete | f77f3e8-HEAD |
| 1 | Obsidian pilot | Current | - |
| 2 | Site-as-model pilot | Planned | - |
| 3 | Landing-page fill | Planned | - |

Status values are plain text: `Complete`, `Current`, `Planned`. Find the current phase with `grep -n "| Current |" docs/IMPLEMENTATION.md`.

## Current Phase: 1 - Obsidian pilot

Phase 0 closed per its stated exit condition (helpers and skill tracked
here, Gutenberg path test-covered). Before starting Phase 1 proper,
install the skill and run one real Gutenberg edition through it:
copy or symlink `stencil-work/` to `~/.zcode/skills/stencil/` and drive
a session with it — the live run is the skill's first real test.

- [x] Restructure to mimeo-congruent package form (DEC-009): uv/hatchling
      package, `stencil/` with `gutenberg.py`/`emit.py` + `cli/` (one
      Click module per command), pytest/mypy/ruff, 39 tests; CLI
      re-validated end-to-end (Frankenstein on chapbook, 33 files; P&P
      `--extra-heading`, 61 units); CLAUDE.md written;
      `stencil-work/` reduced to SKILL.md driving the CLI
- [x] Install the skill (`stencil-work/` → `~/.zcode/skills/stencil/`;
      the CLI is importable via `uv run --project ~/projects/stencil`)
- [x] One live Gutenberg edition end-to-end through the installed skill
      (2026-10-03: Gatsby #64317 → 002375.xyz on folio and 002374.xyz on
      chapbook, build gates clean, chapter text byte-identical; findings
      below and in Entries 4–5)
- [x] Vendor handoff and plinth skills into `.claude/skills/` for cloud
      sessions (DEC-010, 2026-10-07)
- [ ] emit-chapters honors a JSON-level unit `title` over the
      heading-derived default — SKILL.md's documented rename path; the
      pilot had to set incipit titles on emitted files instead
- [ ] Ingest drops or flags TOC-shell units: Gatsby's bare-numeral TOC
      matched the heading style, was not dropped, and became 9 empty
      units (front matter trapped in the last)
- [ ] Probe fallback when chapters/ is empty: the Gatsby re-emit probed
      `title,order` only, losing folio's `chapterNumber,dek` keys
- [x] Ingest helper for an Obsidian page (wikilinks, callouts, embeds,
      images)
- [x] Post emitter probing `content/posts/` + `content/pages/` the way
      `emit_chapters.py` probes chapters
- [x] Agent-written excerpt / date / tags for a post

## Completed Phases

### Phase 0: Foundation

### Done

- [x] `ingest_gutenberg.py` written: PG plain text to stencil JSON (`meta`, `preamble`, `units`, `license`)
- [x] `emit_chapters.py` written: stencil JSON into a chaptered site checkout, with `--replace-demo`, `--colophon`, `--metadata`, `--annotations`
- [x] End-to-end validation (2026-10-03): Frankenstein, eBook #84, against a fresh eleventy-chapbook; 28 units, 33 files built clean
- [x] README describing the design, helpers, build gate, and unbuilt pilots
- [x] Repo initialized (f77f3e8, README only)
- [x] Project tracking established (docs/)

### Repo setup

- [x] Helpers live in `stencil-work/` (brought in from the mimeo checkout 2026-10-03)
- [x] `SKILL.md` lives beside the helpers, so `stencil-work/` is the installable skill dir; README's "this directory" wording reconciled
- [x] Copy removed from the mimeo checkout (untracked there; deleted 2026-10-03)
- [x] Add a git remote (origin: `github.com/pborenstein/stencil`)
- [x] Add `.gitignore` (`.DS_Store`, `__pycache__/`, scratch `book.txt` / `ingested.json`)

### Agent skill

- [x] Write the skill itself (`stencil-work/SKILL.md`): how a prose brief maps to helper invocations
- [x] Document the judgment calls the agent owns: Letter units, display titles, preamble routing, annotation text, homepage demo title sweep
- [x] Document the build-gate loop: emit, build, read error, fix emit, re-runs

### Helper hardening

- [x] Tests for `ingest_gutenberg.py`: PG marker slicing, CONTENTS drop, heading split, paragraph reflow (plus warnings, `--extra-heading`, case-insensitive Contents)
- [x] Tests for `emit_chapters.py`: site probing, each stage flag, `url` key left untouched
- [x] Validate against a second book with different structure — two: Pride and Prejudice #1342 (no letters; illustration-caption headings → `--extra-heading` recovers all 61 chapters) and Republic #1497 (BOOK + roman; Jowett Introduction reported whole in the preamble)
- [x] Validate against eleventy-folio and eleventy-pamphlet (33 files each, probe imitating each naming); pandoc-resume refusal confirmed ("not a chaptered site", exit 1)
- [x] Confirm that everything ingest cannot classify shows up in its report — the `warnings` field: oversized preamble, duplicate heading labels, no headings

### Notes

- 31 tests, all passing (`python3 -m unittest discover -s tests`).
- The case-insensitive CONTENTS fix revealed that Republic's earlier
  20-unit output was silently corrupt (the Introduction hid inside a
  TOC-entry unit's body); the honest 10-unit + warning output is the
  correct one. Warnings exist because that failure mode is invisible
  without them.
- pamphlet's homepage title is page frontmatter (`content/index.md`
  `title: Pamphlet`), not `metadata.js` — the skill's sweep step
  covers it; the emitter rightly does not.
- Phase 0 closed with the work committed and the remote wired; the
  live-run items moved to the top of Phase 1.

## Future Phases

### Phase 2: Site-as-model pilot

- Crawl a non-mimeo site
- Convert pages to Markdown
- Agent decides the archetype: blog / chapters / sections
- Use `mimeo` to create the site first, then emit

### Phase 3: Landing-page fill

- Target product/service section schemas (the most structured targets)
- Agent-written sections JSON validated against the zod schemas
- Build gate remains the acceptance test
