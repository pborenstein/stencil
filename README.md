# stencil

stencil installs content into mimeo sites. A site comes from `mimeo`
empty or full of demo content; stencil is how real content gets in:
point it at source material — a Project Gutenberg book, an Obsidian
page, another website — and the appropriately shaped content files
come out the other end.

stencil is **not a mimeo command**. It is an agent skill plus two
deterministic helpers (this directory). The agent reads a prose brief
("make a reading edition of gutenberg 84 in the frankenstein-test
site"), translates it into helper invocations with explicit
arguments, and fills the gaps that need judgment.

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
