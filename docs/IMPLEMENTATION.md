# Implementation

Phase progress for stencil. Session pickup reads [CONTEXT.md](CONTEXT.md) first; decision rationale lives in [DECISIONS.md](DECISIONS.md); session history lives in [chronicles/](chronicles/).

## Phase Overview

| # | Name | Status | Commits |
|---|------|--------|---------|
| 0 | Foundation | Current | f77f3e8-HEAD |
| 1 | Obsidian pilot | Planned | - |
| 2 | Site-as-model pilot | Planned | - |
| 3 | Landing-page fill | Planned | - |

Status values are plain text: `Complete`, `Current`, `Planned`. Find the current phase with `grep -n "| Current |" docs/IMPLEMENTATION.md`.

## Current Phase: 0 - Foundation

**Goal**: A standalone stencil repo holding the Gutenberg reading-edition path (ingest + emit + build gate) and the agent skill that drives it.

### Done

- [x] `ingest_gutenberg.py` written: PG plain text to stencil JSON (`meta`, `preamble`, `units`, `license`)
- [x] `emit_chapters.py` written: stencil JSON into a chaptered site checkout, with `--replace-demo`, `--colophon`, `--metadata`, `--annotations`
- [x] End-to-end validation (2026-10-03): Frankenstein, eBook #84, against a fresh eleventy-chapbook; 28 units, 33 files built clean
- [x] README describing the design, helpers, build gate, and unbuilt pilots
- [x] Repo initialized (f77f3e8, README only)
- [x] Project tracking established (docs/)

### Repo setup

- [ ] Decide where the helpers live: they currently sit untracked in `/Users/philip/projects/mimeo/stencil/` alongside an identical README; this repo tracks only the README
- [ ] Bring `ingest_gutenberg.py` and `emit_chapters.py` into this repo (or document why not) and reconcile the README's "this directory" wording
- [ ] Remove or redirect the copy in the mimeo checkout once the helpers have one home
- [ ] Add a git remote (none configured)
- [ ] Add `.gitignore` (`.DS_Store`, `__pycache__/`, scratch `book.txt` / `ingested.json`)

### Agent skill

- [ ] Write the skill itself (SKILL.md): how a prose brief maps to helper invocations
- [ ] Document the judgment calls the agent owns: Letter units, display titles, preamble routing, annotation text
- [ ] Document the build-gate loop: emit, build, read error, fix emit, re-run

### Helper hardening

- [ ] Tests for `ingest_gutenberg.py`: PG marker slicing, CONTENTS drop, heading split, paragraph reflow
- [ ] Tests for `emit_chapters.py`: site probing, each stage flag, `url` key left untouched
- [ ] Validate against a second book with different structure (Part/Book headings, no letters)
- [ ] Validate against eleventy-folio and eleventy-pamphlet, and the pandoc templates (`./build.sh`)
- [ ] Confirm that everything ingest cannot classify shows up in its report

### Notes

- The verified example covers eleventy-chapbook only; the other chaptered templates are claimed by the README but unvalidated.
- Phase 0 closes when the helpers and skill are tracked here and the Gutenberg path has test coverage.

## Completed Phases

None yet.

## Future Phases

### Phase 1: Obsidian pilot

- Ingest an Obsidian page as a blog post
- Transform wikilinks, callouts, embeds, and images
- Agent writes excerpt, date, and tags
- Targets eleventy-prose-blog / eleventy-tech-blog (`content/posts/`, `content/pages/`)
- New ingest helper and a post emitter that probes the site as `emit_chapters.py` does

### Phase 2: Site-as-model pilot

- Crawl a non-mimeo site
- Convert pages to Markdown
- Agent decides the archetype: blog / chapters / sections
- Use `mimeo` to create the site first, then emit

### Phase 3: Landing-page fill

- Target product/service section schemas (the most structured targets)
- Agent-written sections JSON validated against the zod schemas
- Build gate remains the acceptance test
