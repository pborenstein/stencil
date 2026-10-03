# stencil

stencil installs content into mimeo sites. A site comes from `mimeo`
empty or full of demo content; stencil is how real content gets in:
point it at source material — a Project Gutenberg book, an Obsidian
page, another website — and the appropriately shaped content files
come out the other end.

stencil is **not a mimeo command**. It is an agent skill plus two
deterministic helpers in [`stencil-work/`](stencil-work/) — that
directory (SKILL.md and the scripts together) is the installable skill;
copy or symlink it into `~/.zcode/skills/stencil/`. The agent reads a
prose brief ("make a reading edition of gutenberg 84 in the
frankenstein-test site"), translates it into helper invocations with
explicit arguments, and fills the gaps that need judgment.

## Where judgment lives

The helpers stay dumb and honest. They parse, split, and write — they
never guess. Everything they cannot classify confidently is reported,
not discarded silently, and the agent decides:

- epistolary "Letter N" units become chapters, or an about page, or
  both (the ingest reports them flat)
- what a chapter's display title is (`Chapter 5` is a heading;
  "The Creature Awakens" is writing)
- where a preface goes (ingest reports the preamble before the first
  heading)
- what the annotations say (the agent writes the annotations file;
  the emitter only places the blocks)
- what a post's excerpt, date, and tags are (Obsidian pilot)

## The helpers

Two stdlib-only Python 3 scripts. No dependency on the mimeo package.

### `ingest_gutenberg.py`

Turns a Project Gutenberg plain-text ebook into stencil JSON:

    curl -o book.txt https://www.gutenberg.org/cache/epub/84/pg84.txt
    python3 ingest_gutenberg.py book.txt > ingested.json

Slices on the canonical PG markers, drops the CONTENTS block, splits
on structural headings (Chapter / Letter / Part / Book + number or
roman numeral), reflows hard-wrapped paragraphs. Output:

- `meta` — title, author, release date, language, ebook id + URL
- `preamble` — body text before the first heading (title page,
  preface); reported for the agent to route
- `units` — `[{heading, order, text}]`, the mechanical split
- `license` — the full PG license tail, reflowed
- `warnings` — signals the agent must read before emitting: a
  preamble big enough to hold missed content (a heading style the
  split does not recognize, or a genuine introduction before the
  first heading), duplicate heading labels (one file holding an
  introduction and a translation), or no headings at all

When a warning means the split missed headings, teach it the
edition's style explicitly instead of hand-editing the JSON:

    python3 ingest_gutenberg.py book.txt \
        --extra-heading '^Chapter [IVXLCDM]+\.\]$' > ingested.json

(`--extra-heading` is repeatable. Pride and Prejudice #1342 needs the
one above — its first heading is an illustration caption,
`Chapter I.]`.)

Two validated case studies: Republic #1497's Jowett Introduction
(~98k words, no BOOK headings) lands whole in the preamble with a
warning, and the translation's ten BOOK units split clean; and its
earlier 20-unit output — before the case-insensitive CONTENTS fix —
was silently corrupt, with the Introduction hidden inside a TOC-entry
unit's body. Warnings exist because that failure mode is invisible
without them.

### `emit_chapters.py`

Installs stencil JSON into a chaptered site checkout
(eleventy-chapbook / -folio / -pamphlet or a site grown from one):

    python3 emit_chapters.py SITE/ ingested.json \
        [--replace-demo] [--colophon] [--metadata] [--annotations ann.json]

Nothing about a specific template is hardcoded. The script probes the
site first and imitates what it finds:

- chapter naming convention, from existing chapter filenames
- chapter frontmatter keys, from an existing chapter file
  (only `title` and `order` are filled; deks are writing)
- loose-page navigation order, from pages like `content/about.md`
- `content/_data/metadata.js`

Stages:

- chapters — one file per unit; demo chapters are removed only under
  `--replace-demo`
- `--colophon` — writes `content/colophon.md` with the PG book info
  and the full Project Gutenberg license
- `--metadata` — updates `title`, `description`, `language`,
  `author.name` in `content/_data/metadata.js`. The `url` key belongs
  to `mimeo.template.json` and is never touched
- `--annotations` — interleaves annotation blocks between source
  paragraphs. The annotation file is agent-written:

      [{"chapter": 1, "after_paragraph": 2,
        "summary": "…", "text": "…"}, …]

  `chapter` is the ingest order; `after_paragraph` is 1-based. Blocks
  use the [amalgamedon.com](https://amalgamedon.com) convention —
  collapsed `<details><summary>…</summary>` between paragraphs — so
  the reading surface stays pristine and annotations open on demand.

## The build gate

After emit, run the site's build (`npm run build`, or `./build.sh`
for the pandoc templates). Eleventy and the zod section schemas fail
loudly on wrong shapes, so the build is stencil's acceptance gate; on
failure the agent reads the error, fixes the emit, re-runs.

## Verified example

The full reading-edition path was validated end-to-end (2026-10-03)
against a fresh copy of eleventy-chapbook with Frankenstein, eBook
#84 (448 KB of plain text → 28 units: 4 letters + 24 chapters):

    python3 ingest_gutenberg.py book.txt > ingested.json
    python3 emit_chapters.py SITE/ ingested.json \
        --replace-demo --colophon --metadata --annotations ann.json
    cd SITE && npm install && npm run build

Result: 33 files built clean — 28 chapter pages, colophon in the nav
with the full PG license, `metadata.js` carrying the book title and
author, two `<details>` annotations rendered in place.

The same emit was validated against fresh copies of eleventy-folio
and eleventy-pamphlet (33 files each, probe imitating each template's
own naming). Folio's `chapterNumber`/`dek` frontmatter keys are
deliberately not auto-filled — they are writing. Pointed at
pandoc-resume, the probe refuses: "not a chaptered site", exit 1.

Three books cover the split: Frankenstein #84 (letters + chapters, no
warnings), Pride and Prejudice #1342 (illustration-caption headings,
recovered with `--extra-heading`), Republic #1497 (BOOK + roman
numerals; massive headingless Introduction reported in the preamble).

## Not built yet

- **Obsidian pilot** — ingest an Obsidian page as a blog post:
  wikilinks, callouts, embeds, and images transformed; excerpt/date/
  tags written by the agent. Targets eleventy-prose-blog /
  eleventy-tech-blog (`content/posts/`, `content/pages/`).
- **Site-as-model pilot** — crawl a non-mimeo site, convert pages to
  Markdown, decide the archetype (blog / chapters / sections), emit.
  Uses `mimeo` to create the site first.
- **Landing-page fill** — product/service section schemas are the
  most structured targets; an agent-written sections JSON against the
  zod schemas.

## Development documentation

- [docs/CONTEXT.md](docs/CONTEXT.md) — current session state; read
  this first when picking up work
- [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md) — phase progress
  and task lists
- [docs/DECISIONS.md](docs/DECISIONS.md) — architectural decisions
- [docs/chronicles/](docs/chronicles/) — session history by phase
