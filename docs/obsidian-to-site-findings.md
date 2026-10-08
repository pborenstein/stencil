# Obsidian to site: findings

Written 2026-10-08. This is a record of what the code and the xhosi.com
site do today. It makes no changes and picks no design.

## The question

Philip moves some Obsidian notes onto xhosi.com by copying the file into
`content/chapters/`. Nothing converts the file on the way. Stencil's
Obsidian tools were built for a different path (a note onto a blog site as
a post), so none of them touch the xhosi copy.

## What stencil does with an Obsidian note today

| Step | Command | What it does |
|:-----|:--------|:-------------|
| Read the note | `ingest-obsidian` (`stencil/obsidian.py`) | Splits off the properties block. Turns `[[links]]` into plain text. Turns `![[image.png]]` into a Markdown image. Turns callouts into blockquotes. Removes `%%comments%%` and `^block-id` marks. Lists images and links, and warns about what it could not classify. |
| Write the note | `emit-post` (`stencil/posts.py`) | Writes a post to `content/posts/` (or a loose page to `content/pages/`). Copies found images into the site. |

`emit-post` only works on a site that has `content/posts/`. xhosi.com has
no such directory; its pages live in `content/chapters/`.

## What stencil does with images

| Item | Behavior | Where |
|:-----|:---------|:------|
| Find an image | Looks beside the note, then at the vault root, then anywhere in the vault by file name | `obsidian.py:84-96` |
| Image not found | Warns, and leaves the link as it was | `obsidian.py:132-133` |
| Pick the site image folder | Takes the first that exists of `content/images`, `content/assets`, `content/img`, `public/images`, `src/images`. If none exists, uses `content/images` without saying so | `posts.py:26,54` |
| Pick the public URL | Drops the first part of the folder path, so `content/img` becomes `/img/...` | `posts.py:123` |
| Same file name from two folders | The second overwrites the first, because only the file name is kept | `posts.py:118` |
| Markdown image with a space in the path | Not recorded and not copied | `obsidian.py:33` |
| Raw HTML image tags, PDFs, audio | Not handled | none |

Nothing checks the folder or URL against the site's Eleventy settings.
Only a real build shows whether the URL works.

## What xhosi.com does to a copied file

The build code is in `eleventy.config.js`. The same code was copied into
eleventy-pamphlet (commits e3b089e and 2e141b8).

| Item | Behavior |
|:-----|:---------|
| `draft: true` | Adds "(draft)" to the title. Skips the page in production builds. |
| Star marks at the end of `description` | Removed. |
| Heading ids | Added to every heading. |
| Page order | Newest last git commit first. A `date:` in the file overrides it. In eleventy-pamphlet this is optional (`metadata.sortBy`). |
| Line breaks and raw HTML in Markdown | Allowed. |
| Images | Only `content/img` is copied to the built site. Neither xhosi.com nor eleventy-pamphlet has a `content/img` folder right now. |

## What xhosi.com does not do

| Item | What happens | Example |
|:-----|:-------------|:--------|
| `[[wikilinks]]` | Shown as typed, brackets included | `generative-disability.md` has `[[father-summary-gpt-5.5]]` |
| Image embeds, callouts, comments, block ids | Not converted | None of the five chapters uses them yet |
| Obsidian properties | Stay in the front matter | `type`, `created`, `modified`, `aliases`, `draftSource`, `eras`, `track_count` |
| Bad link text | Not caught | `[\|A Teenager in Love]` in `generative-disability.md` |

## What the stencil image code would do on xhosi.com

If the emit step were pointed at xhosi.com as it is now:

- `content/img` does not exist there, so the probe would fall back to
  `content/images`.
- `content/images` is not copied to the built site, so every image link
  would break.

This is a fact about the folder names today, not a design choice.

## The open question

Two ways to close the gap. No choice has been made.

| Option | What changes | What stays the same |
|:-------|:-------------|:--------------------|
| A | The Eleventy build in eleventy-pamphlet reads raw Obsidian files and converts the syntax at build time. | Files are still copied by hand. Stencil is not used for xhosi. |
| B | Stencil converts the note and writes it into `content/chapters/` before it enters the repo. | The Eleventy build is unchanged. |

Related questions that depend on the choice:

- Where the star-mark removal on `description` lives (the build or stencil).
- Whether the Phase 1 live run in `docs/CONTEXT.md` targets a blog site or
  xhosi.com. Today it names a blog site.
- Whether xhosi.com needs an exception to the content-fixture contract,
  which asks for `title`, `draft` and `order` in front matter.

## How this was checked

- Stencil: `stencil/obsidian.py`, `stencil/posts.py`, `tests/test_obsidian.py`,
  `tests/test_posts.py`, `docs/CONTEXT.md`, `docs/IMPLEMENTATION.md`.
- xhosi.com and eleventy-pamphlet: `eleventy.config.js`, the chapter
  front matter files, and a listing of `content/`.
- No build was run. No image was tested end to end.
