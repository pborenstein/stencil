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

## Entry 2: Phase 0 closed -- hardening, tests, skill, and the three-book validation (2026-10-03)

**What**: Hardened the ingest from second-book validation, gave both helpers a 31-test suite, wrote the agent skill, validated all three chaptered templates, brought everything into this repo, and closed Phase 0. The mimeo checkout's `stencil/` copy is deleted; mimeo is clean.

**Why**: The helpers had been validated against one book on one template. Real Gutenberg editions vary structurally, and the probe/imitate design claimed more templates than had been tested.

**How**:

- Second-book validation found two structural cases: Pride and Prejudice #1342 sets its first heading as an illustration caption (`Chapter I.]`), and Republic #1497's case-insensitive CONTENTS fix revealed the earlier 20-unit output was silently corrupt (Jowett's ~98k-word Introduction hidden inside a TOC-entry unit's body)
- Responses per DEC-002: a `warnings` field in the ingest JSON (oversized preamble, duplicate heading labels, no headings) and `--extra-heading REGEX` to teach the split an edition's heading style explicitly; with it, P&P recovers all 61 chapters
- Same Frankenstein emit validated on fresh folio and pamphlet copies (33 files each, probe imitating each naming); pandoc-resume refused cleanly ("not a chaptered site", exit 1)
- `stencil-work/SKILL.md` written: brief-to-invocation workflow, warnings playbook with both case studies, agent-owned judgment calls, build-gate loop; `stencil-work/` is the installable skill dir
- `.gitignore` added; remote wired (github.com/pborenstein/stencil)

**Decisions**:

- DEC-007: the split is teachable by explicit regex, never by heuristics
- DEC-008: `stencil-work/` is the installable skill directory

**Files**: 89aa8f1 (`stencil-work/`, `tests/`, `.gitignore`, README, docs)

