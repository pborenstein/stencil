# Phase 0: Foundation

## Entry 1: Gutenberg reading-edition path and repo setup (2026-10-03)

**What**: Built and validated the Gutenberg reading-edition path (ingest, emit, build gate), wrote the README, initialized the repo, and set up project tracking. Retroactive entry reconstructed from the README and the filesystem.

**Why**: mimeo sites arrive empty or with demo content; stencil is how real content gets in. A Gutenberg book into a chaptered site was the first path to prove the agent-plus-helpers design.

**How**:

- `ingest_gutenberg.py` slices on the PG markers, drops CONTENTS, splits on Chapter / Letter / Part / Book headings, reflows paragraphs, and outputs `meta`, `preamble`, `units`, `license`
- `emit_chapters.py` probes the site checkout and writes chapters, with optional colophon, metadata, and annotation stages
- Validated with Frankenstein (eBook #84) against a fresh eleventy-chapbook: 28 units (4 letters + 24 chapters), 33 files built clean, two annotations rendered
- Repo initialized with the README only (f77f3e8); the two helpers remain untracked in `/Users/philip/projects/mimeo/stencil/`
- Tracking files created under `docs/`

**Decisions**:

- DEC-001: agent skill plus helpers, not a mimeo command
- DEC-002: helpers never guess; unclassified material is reported
- DEC-003: stdlib-only Python 3, no mimeo dependency
- DEC-004: emitter probes the site and imitates it
- DEC-005: the site build is the acceptance gate
- DEC-006: agent-written annotations as collapsed details blocks

**Files**: `README.md` (f77f3e8), `docs/`
