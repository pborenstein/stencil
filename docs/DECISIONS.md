# Decisions

Architectural decisions for this project. Search with `grep -i "keyword" docs/DECISIONS.md`.

DEC-001 through DEC-006 were documented retroactively on 2026-10-03 from the README. Where the README does not record the alternatives that were weighed, the entry says so.

## Active Decisions

### DEC-001: stencil is an agent skill plus helpers, not a mimeo command (2026-10-03)

**Status**: Active

**Context**: mimeo sites arrive empty or full of demo content, and real content has to get in from varied sources (Gutenberg books, Obsidian pages, other websites). Shaping that content requires judgment that a CLI subcommand cannot supply.

**Decision**: stencil is an agent skill plus deterministic helper scripts. The agent reads a prose brief, translates it into helper invocations with explicit arguments, and fills the gaps that need judgment.

**Alternatives considered**: A `mimeo` subcommand (rejected: the README states stencil is not a mimeo command).

**Consequences**: stencil has no CLI of its own beyond the helpers. Behavior depends on the skill's instructions as well as the code, so the skill text is part of the product.

---

### DEC-002: Helpers never guess; unclassified material is reported (2026-10-03)

**Status**: Active

**Context**: Source material is ambiguous: epistolary "Letter N" units, chapter display titles, prefaces before the first heading.

**Decision**: Helpers parse, split, and write. Anything they cannot classify confidently is reported in their output rather than discarded or guessed at, and the agent decides. Example: ingest reports Letter units flat and reports the preamble separately for the agent to route.

**Alternatives considered**: Not recorded in the README. The implied alternative is heuristics inside the helpers.

**Consequences**: Helper output is deterministic and testable. The agent owns: Letter-unit routing, display titles, preamble placement, annotation text, and (Obsidian pilot) excerpt/date/tags.

---

### DEC-003: Helpers are stdlib-only Python 3 with no mimeo dependency (2026-10-03)

**Status**: Active

**Context**: The helpers run against arbitrary site checkouts and should work without an install step.

**Decision**: Helpers are single-file Python 3 scripts using only the standard library. They do not import the mimeo package.

**Alternatives considered**: Not recorded in the README.

**Consequences**: No venv or dependency management needed to run them. Parsing that a library would normally handle (frontmatter, `metadata.js` edits) is done by hand in the scripts.

---

### DEC-004: The emitter probes the site and imitates what it finds (2026-10-03)

**Status**: Active

**Context**: Chaptered sites come from several templates (eleventy-chapbook, -folio, -pamphlet) or have grown away from one, each with its own filename and frontmatter conventions.

**Decision**: `emit_chapters.py` hardcodes nothing about a specific template. It probes the checkout for the chapter naming convention, chapter frontmatter keys, loose-page navigation order, and `content/_data/metadata.js`, then imitates them. Only `title` and `order` are filled in frontmatter. The `url` key in `metadata.js` belongs to `mimeo.template.json` and is never touched.

**Alternatives considered**: Not recorded in the README. The implied alternative is per-template emit logic.

**Consequences**: New chaptered templates should work without code changes, provided the site has an existing chapter file to imitate. A site with no example chapter gives the probe nothing to read.

---

### DEC-005: The site build is the acceptance gate (2026-10-03)

**Status**: Active

**Context**: stencil needs a way to know an emit produced correctly shaped content.

**Decision**: After emit, run the site's own build (`npm run build`, or `./build.sh` for the pandoc templates). Eleventy and the zod section schemas fail loudly on wrong shapes. On failure the agent reads the error, fixes the emit, and re-runs.

**Alternatives considered**: Not recorded in the README. The implied alternative is a validator inside stencil.

**Consequences**: stencil carries no schema knowledge of its own and stays in sync with the templates for free. Validation requires an installed, buildable site.

---

### DEC-006: Annotations are agent-written and emitted as collapsed details blocks (2026-10-03)

**Status**: Active

**Context**: Reading editions want annotations without cluttering the text.

**Decision**: The agent writes an annotations JSON file (`chapter`, `after_paragraph`, `summary`, `text`); the emitter only places the blocks. `chapter` is the ingest order and `after_paragraph` is 1-based. Blocks follow the amalgamedon.com convention: a collapsed `<details><summary>` between source paragraphs.

**Alternatives considered**: Not recorded in the README.

**Consequences**: The reading surface stays unchanged until an annotation is opened. Annotation positions are tied to ingest paragraph numbering, so re-ingesting with different reflow rules can shift them.

---

### DEC-007: The split is teachable by explicit regex, never by heuristics (2026-10-03)

**Status**: Active

**Context**: Pride and Prejudice #1342 sets its first chapter heading as an illustration caption (`Chapter I.]` closing a multi-line `[Illustration:` block). The split family (Chapter/Letter/Part/Book + number) cannot recognize it, and Chapter I landed in the reported preamble.

**Decision**: `ingest_gutenberg.py` accepts `--extra-heading REGEX` (repeatable). When a warning shows missed headings, the agent finds the edition's actual heading line and teaches the splitter explicitly, instead of the script guessing at more heading styles.

**Alternatives considered**: Broadening the built-in heading family (rejected: guessing inside the helper violates DEC-002); hand-editing the JSON (rejected: loses the provenance of a repeatable command).

**Consequences**: Edition quirks stay visible as warnings until an agent teaches them; the heading family stays small and testable. Each quirky edition adds a documented regex, not code.

---

### DEC-008: `stencil-work/` is the installable skill directory (2026-10-03)

**Status**: Active

**Context**: The executor is an agent skill plus helpers (DEC-001). The skill text and the helpers must stay in sync, and skills install by directory into `~/.zcode/skills/`.

**Decision**: `stencil-work/` holds `SKILL.md` next to the two helper scripts; installing the skill is copying or symlinking that one directory. The README documents this.

**Alternatives considered**: SKILL.md at the repo root with a build/install step (rejected: two sources of truth for one skill).

**Consequences**: The repo layout mirrors the installed layout. Tests import the helpers from `stencil-work/`, so drift between repo and installed skill shows up immediately.

---

## Superseded/Deprecated

None.
