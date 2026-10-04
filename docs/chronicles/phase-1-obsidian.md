# Phase 1: Obsidian Pilot

## Entry 5: Second template, same book — chapbook confirms the findings (2026-10-03)

**What**: Re-ran Gatsby #64317 end-to-end into 002374.xyz (chapbook), reusing the worked `ingested.json`. Build gate clean (14 files), chapter text byte-identical. No stencil code changed.

**Why**: Establish that the skill workflow and the emit probe hold on a second template, and whether the Entry 4 findings are template-specific.

**How**:

- Probe imitated chapbook conventions correctly on its own: `chNN-slug.md` naming, `title,order,description` keys, no `chapterNumber` invented. Demo `description` key left unset — inventing nine one-liners is content, not mechanics
- JSON-title mismatch re-confirmed as template-independent; incipit titles applied by editing emitted files, same workaround as folio
- Chapbook's homepage foreword slot (demo text literally asks for "epigraph, dedication, or opening passage") is the natural front-matter routing target: dedication as the drop-cap line, epigraph as a verse blockquote. Better fit than folio's about-page routing — routing targets are per-template, a skill-text concern
- Chapbook ships an empty metadata `subtitle` — no sweep needed there, unlike folio

**Findings**: all three Entry 4 findings stand unchanged. New minor: front-matter routing targets differ per template (folio: about page; chapbook: homepage foreword) — belongs in SKILL.md, not the CLI.

**Decisions**: none.

**Files**: site work uncommitted in `~/projects/mimeo-sites/002374.xyz`; run artifacts in `/tmp/stencil-run/64317/`

## Entry 4: Gatsby through the installed skill — the live run works; three contract findings (2026-10-03)

**What**: Installed the skill (`stencil-work/` → `~/.zcode/skills/stencil/`) and drove one live edition end-to-end: The Great Gatsby (#64317) into 002375.xyz (folio). Fetch, ingest, warnings worked in the JSON, emit with `--replace-demo --colophon --metadata`, sweep, build gate clean (14 files); all 9 chapters verified byte-identical to the ingested text. No stencil-repo code changed — the run's value is what it surfaced.

**Why**: Phase 1's stated preface: the live run is the skill's first real test.

**How**:

- Gatsby heads chapters with indented bare roman numerals on CRLF lines; first ingest reported "no structural headings". `--extra-heading '^\s*[IVXLCDM]{1,7}\s*$'` (whitespace-tolerant anchors) recovered all 9 — after grep-verifying exactly 18 matching lines (9 TOC + 9 headings, nothing else)
- Second ingest warned "duplicate heading labels": the numeral TOC matched the heading style, was not dropped, and became 9 empty unit shells with the dedication + epigraph (37 words) trapped in the last. Model-layer fix in the JSON: drop shells, rescue front matter (routed to the about page), renumber 1–9
- Untitled chapters got incipit titles — verbatim opening words, clause-boundary cuts, sentence case + ellipsis, word-by-word verified against the source
- The session predates skill auto-discovery, so the run followed SKILL.md read as a document; auto-trigger is still untested

**Findings** (queued as Phase 1 tasks):

- emit-chapters ignores a JSON-level unit `title` and derives it from the heading; SKILL.md tells the agent to rename titles in the JSON — contract mismatch
- Emitting into an empty chapters/ dir loses the template's frontmatter keys (probe fell back to `title,order`; folio's `chapterNumber,dek` gone until re-added by hand)
- folio's metadata `subtitle` is outside `--metadata`'s documented keys — swept by hand, same class as pamphlet's hardcoded index title (Phase 0 note)

**Decisions**: none new; the run exercised DEC-009's form as built.

**Files**: skill at `~/.zcode/skills/stencil/`; site work uncommitted in `~/projects/mimeo-sites/002375.xyz` (9 incipit-titled chapters `01-i.md`…`09-ix.md`, colophon, metadata, about); run artifacts in `/tmp/stencil-run/64317/`

## Entry 3: mimeo-congruent package form; the skill drives the CLI (2026-10-03)

**What**: Restructured the repo from standalone helper scripts into a uv/hatchling Click CLI package following mimeo's code form, via the plinth python-project-init skill. Re-validated the full Gutenberg path through the new command surface.

**Why**: Design principle stated by the user: stencil is skill-based with decisions made by the LLM, but the Python helpers must be CLI-runnable, congruent, and not ad-hoc.

**How**:

- `stencil/` package: `gutenberg.py` and `emit.py` as typed library modules raising `GutenbergError`/`EmitError`; `cli/` subpackage with one Click module per command (`ingest-gutenberg`, `emit-chapters`), mirroring mimeo's cli package
- pyproject.toml with mimeo's tooling values; dev group pytest/mypy/ruff; CLAUDE.md from the plinth template; tests converted to pytest function style plus CliRunner CLI tests (39 passing; mypy and ruff clean)
- `stencil-work/` reduced to SKILL.md, which drives the CLI (`uv run --project ~/projects/stencil stencil ...`); its closing rule encodes the principle: mechanical capabilities land as CLI modules, decisions land in the skill text
- Port caught one real bug: the emit-chapters command function shadowed the library import (would recurse); fixed with an aliased import
- End-to-end through the CLI: Frankenstein on a fresh chapbook copy (28 units, probe, emit, 33 files, annotations rendered); P&P `--extra-heading` (61 units)

**Decisions**:

- DEC-009: mimeo-congruent Click CLI package; the skill drives the CLI (supersedes DEC-003, amends DEC-008)

**Files**: aadffef (`stencil/`, `tests/`, `pyproject.toml`, `CLAUDE.md`, `uv.lock`, `stencil-work/SKILL.md`, docs)
