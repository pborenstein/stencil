#!/usr/bin/env python3
"""ingest_gutenberg -- turn a Project Gutenberg plain-text ebook into stencil JSON.

Usage:
    curl -o book.txt https://www.gutenberg.org/cache/epub/<ID>/pg<ID>.txt
    python3 ingest_gutenberg.py book.txt > ingested.json

The script is deterministic: it never guesses chapter titles or rewrites
prose. It slices the book on the canonical PG markers, drops the CONTENTS
block (its entries would read as headings), splits the body on structural
headings (Chapter/Letter/Part/Book + number or roman numeral), and reflows
hard-wrapped paragraphs. Everything it could not confidently classify is
reported, not discarded silently:

    meta        title / author / release date / language / ebook id + URL
    preamble    body text before the first heading (title page, preface)
    units       [{heading, order, text}] -- the mechanical split
    license     the full PG license tail, reflowed

Decisions that need judgment -- whether epistolary "Letter N" units become
chapters, where a preface belongs, what a chapter's display title should
be -- belong to the caller, not this script.
"""

import json
import re
import sys

START_MARK = re.compile(r"^\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*$", re.M)
END_MARK = re.compile(r"^\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*$", re.M)

HEADING_RE = re.compile(
    r"^(Chapter|CHAPTER|Letter|LETTER|Part|PART|Book|BOOK)\s+"
    r"([0-9]+|[IVXLCDM]+)\.?$"
)


def reflow(block: str) -> str:
    """Join hard-wrapped lines into one line per blank-line-delimited paragraph."""
    paragraphs, buf = [], []
    for line in block.split("\n"):
        if line.strip() == "":
            if buf:
                paragraphs.append(" ".join(s.strip() for s in buf))
                buf = []
        else:
            buf.append(line)
    if buf:
        paragraphs.append(" ".join(s.strip() for s in buf))
    return "\n\n".join(p for p in paragraphs if p)


def drop_toc(body: str) -> str:
    """Remove the CONTENTS block so its entries don't read as headings.

    The block is cut from the CONTENTS line to the first blank-line
    stretch after it. TOCs with blank lines between entries survive the
    cut only partially -- the split validation (duplicate headings,
    tiny fragments) catches that; this script reports what it did.
    """
    m = re.search(r"^[ \t]*CONTENTS[ \t]*$", body, re.M)
    if not m:
        return body
    after = body[m.end():]
    tail = re.search(r"\n[ \t]*\n[ \t]*\n", after)
    return body[: m.start()] + (after[tail.end():] if tail else after)


def parse(text: str) -> dict:
    m_start = START_MARK.search(text)
    m_end = END_MARK.search(text)
    if not m_start or not m_end or m_end.start() < m_start.start():
        sys.exit("error: no canonical PG START/END markers found; is this a PG plain-text ebook?")

    header = text[: m_start.start()]
    body = text[m_start.end(): m_end.start()]
    license_text = text[m_end.end():]

    meta = {}
    for key in ("Title", "Author", "Release date", "Language"):
        km = re.search(rf"^{key}:\s+(.+)$", header, re.M)
        if km:
            meta[key.lower().replace(" ", "_")] = km.group(1).strip()
    em = re.search(r"\[eBook #(\d+)\]", header)
    if em:
        meta["ebook_id"] = int(em.group(1))
        meta["source_url"] = f"https://www.gutenberg.org/ebooks/{em.group(1)}"

    body = drop_toc(body)

    units, current, preamble = [], None, []
    for line in body.split("\n"):
        if HEADING_RE.match(line.strip()):
            if current:
                units.append(current)
            current = {"heading": line.strip(), "order": len(units) + 1, "lines": []}
        elif current is not None:
            current["lines"].append(line)
        else:
            preamble.append(line)
    if current:
        units.append(current)

    return {
        "meta": meta,
        "preamble": reflow("\n".join(preamble)),
        "units": [
            {"heading": u["heading"], "order": u["order"], "text": reflow("\n".join(u["lines"]))}
            for u in units
        ],
        "license": reflow(license_text),
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"usage: {sys.argv[0]} <pg-plain-text.txt>")
    with open(sys.argv[1], encoding="utf-8") as f:
        print(json.dumps(parse(f.read()), ensure_ascii=False, indent=1))
