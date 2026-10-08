---
name: stencil
description: Install content into mimeo sites from source material — turn a Project Gutenberg book into a chaptered reading or annotated edition, and similar content-population work. Use when the user asks to populate, fill, or fill in a mimeo site, make a reading or annotated edition, or install chapters from a source text.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# stencil

stencil populates mimeo sites. The CLI does the deterministic work;
you do the judgment work. Never hand-edit what a command can compute,
and never let a command guess what only you should decide.

The CLI lives in the stencil repo (`~/projects/stencil`, congruent
with mimeo's code form). Invoke it as `uv run --project
~/projects/stencil stencil <command>` — or plain `stencil <command>`
when the package is on PATH. The repo's CLAUDE.md documents the
development form; this skill documents the driving form.

## Workflow

1. **Understand the brief.** It names (or implies) a source, a target
   site checkout, and an intent (reading edition, annotated edition).
   Resolve all three before running anything. If the site does not
   exist yet, it is created with `mimeo` first — outside this skill.

2. **Fetch the source.** For Project Gutenberg:

       curl -o book.txt https://www.gutenberg.org/cache/epub/<ID>/pg<ID>.txt

3. **Ingest:**

       stencil ingest-gutenberg book.txt > ingested.json

4. **Read the report before emitting.** This step is the product.
   - `warnings` is your to-do list. Every warning means a decision:
     - *preamble holds N words* — open the preamble. Either front
       matter to route (a preface becomes a chapter or an about page;
       the Jowett Republic's ~98k-word Introduction is a famous case),
       or a heading style the split missed. If the latter, find the
       actual heading line in book.txt and re-ingest with
       `--extra-heading REGEX` (repeatable). Pride and Prejudice #1342
       sets its first heading as an illustration caption,
       `Chapter I.]`; `--extra-heading '^Chapter [IVXLCDM]+\.\]$'`
       recovers all 61 chapters.
     - *duplicate heading labels* — one file holds two sections that
       reuse labels (TOC not dropped, or introduction + translation).
       Identify which units belong to which before emitting.
     - *no structural headings* — poetry/essay. Do not emit chapters;
       tell the user what you found and propose alternatives (single
       page, or a split you design by hand).
   - Route the `preamble`: title pages usually become nothing (the
     metadata carries the title); prefaces and introductions usually
     become a chapter or an about page. Edit `ingested.json` to add
     units or move text — you are the model layer; the JSON is yours.
   - Front matter lands in a different place on each template; look
     at the site before choosing. On eleventy-folio, a preface or
     introduction belongs on the about page (`content/about.md`). On
     eleventy-chapbook, it belongs in the homepage foreword slot
     (`content/index.md`). If the template has neither, make it a
     leading chapter. Probe the site (read `content/*.md`) rather than
     assuming the template.
   - Decide display titles. `Chapter 1` is a heading, not a title.
     Rename titles in the JSON when the brief wants real ones (for
     folio, `chapterNumber` roman numerals and `dek` subtitles are
     writing too — fill them by editing the emitted files).

5. **Emit** (site checkout path first):

       stencil emit-chapters SITE/ ingested.json \
           [--replace-demo] [--colophon] [--metadata] \
           [--annotations annotations.json]

   - `--replace-demo` deletes the template's demo chapters first.
     Content that is not demo chapters is never touched; adding to a
     site that already has real chapters needs no flag.
   - `--colophon` writes `content/colophon.md` with the PG book info
     and full license, in site navigation after the existing pages.
   - `--metadata` sets title / description / language / author.name in
     `content/_data/metadata.js`. The `url` key belongs to
     `mimeo.template.json` and is never touched.
   - For an annotated edition, you write `annotations.json` yourself:

         [{"chapter": <ingest order>, "after_paragraph": <1-based>,
           "summary": "<one-line label>", "text": "<the note>"}]

     Blocks render as collapsed `<details><summary>` between source
     paragraphs (the amalgamedon.com convention). Read the chapter
     text from `ingested.json` to choose positions and write notes the
     reader will want, not plot summary. In a reading edition the
     source text stays byte-identical, so `git diff` proves the
     annotations changed nothing — run that check and say so.

6. **Sweep the leftovers.** After emit, look for demo values the
   emitter rightly did not touch: `content/index.md` frontmatter
   `title` (pamphlet hardcodes `Pamphlet` there), about-page demo
   prose, folio `chapterNumber`/`dek`. Fix what the brief implies.

7. **Build gate.** Run the site's build: `npm run build` in SITE/
   (`npm install` first if needed). On failure: read the Eleventy
   error, fix the content or the emit inputs, re-run. Do not report
   success without a passing build. On success, report what was
   installed (units, pages, warnings resolved, annotations placed)
   and anything left for the user (uncommitted changes, open
   judgment calls you made).

## Obsidian pages

For an Obsidian page, ingest with:

    stencil ingest-obsidian PAGE.md [--vault VAULT/] > page.json

The helper flattens wikilinks to display text, turns image embeds into
Markdown images, turns callouts into blockquotes, and strips comments.
Read its `warnings` and `links` first: note embeds are left as text
and need your call (inline the note, link it, or drop it); unresolved
wikilinks are listed so you can decide which become real links. Images
are listed in `images` with their source paths.

## Posts and loose pages

To install an ingested page into a blog-style site (one with
`content/posts/`):

    stencil emit-post SITE/ page.json [--page] [--replace-demo]

`--page` writes to `content/pages/` (About and similar) instead. The
command probes the site, so its output line `probe:` shows the
filename pattern and frontmatter keys it will imitate.

Excerpt, date, and tags are yours to write, never the CLI's. Before
emitting, edit `page.json` `meta`:

- `excerpt`: one or two sentences in the page's own voice that make a
  reader want the post; not a summary of every point, and not the
  first paragraph pasted. Skip it only if the site's posts have none.
- `date`: `YYYY-MM-DD`. Use the page's front matter date when it has
  one; otherwise ask the brief. If neither names a date, leave it out
  and the CLI uses today's date, which you should mention in your
  report.
- `tags`: a short list (2-5) that reuses tags already on the site's
  posts before inventing new ones. Check with
  `grep -h '^tags' SITE/content/posts/*.md` or read a few.

Front matter the page already carries (`tags`, `date`) is used as
written; override it in `meta` only when the brief says to. After
emit, read the `no value for keys:` line: each key listed is one the
site's posts carry that you left empty. Fill it or say why it stays
empty. Images the page references are copied to the site's image
directory; the build gate shows whether the references resolve.

## Judgment calls you own

- Letter units: chapters, an about-page frame note, or both.
- Preamble routing: preface → chapter or about page; title page → drop.
- Display titles, deks, chapterNumber labels.
- Annotation content and placement.
- Post excerpt, date, and tags.
- The homepage demo title sweep (step 6).

## What the CLI owns

- Marker slicing, TOC dropping, heading split, paragraph reflow,
  metadata parsing (`ingest-gutenberg`).
- Site probing for posts and pages (`emit-post`), image copying.
- Site probing (naming, frontmatter keys, nav order), file emission,
  colophon, metadata.js edits, annotation placement
  (`emit-chapters`).

If the CLI lacks something you need, prefer its explicit knobs
(`--extra-heading`) over post-hoc sed on its output; only edit the
JSON (step 4), never the emitted files, except for writing (titles,
deks) the brief asks for. New capabilities that are mechanical belong
in the CLI (one module per command, mimeo's form); new decisions
belong here.
