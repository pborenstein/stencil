"""Gutenberg plain-text ingest.

Turns a Project Gutenberg plain-text ebook into stencil JSON: slices
on the canonical PG markers, drops the CONTENTS block (its entries
would read as headings), splits the body on structural headings
(Chapter/Letter/Part/Book + number or roman numeral), and reflows
hard-wrapped paragraphs.

Everything this module cannot confidently classify is reported, not
discarded silently (DEC-002): ``warnings`` carries the signals the
agent must read before emitting -- a preamble big enough to hold
missed content, duplicate heading labels (one file holding an
introduction and a translation), or no headings at all. When a
warning means the split missed headings, teach it the edition's style
explicitly with extra heading regexes (DEC-007) rather than editing
the JSON by hand.

Decisions that need judgment -- whether epistolary "Letter N" units
become chapters, where a preface belongs, what a chapter's display
title should be -- belong to the caller, not this module.
"""

import re

START_MARK = re.compile(r"^\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*$", re.MULTILINE)
END_MARK = re.compile(r"^\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*$", re.MULTILINE)

HEADING_RE = re.compile(
    r"^(Chapter|CHAPTER|Letter|LETTER|Part|PART|Book|BOOK)\s+"
    r"([0-9]+|[IVXLCDM]+)\.?$"
)


class GutenbergError(Exception):
    """Raised when the input is not a recognizable PG plain-text ebook."""


def reflow(block: str) -> str:
    """Join hard-wrapped lines into one line per blank-line-delimited paragraph."""
    paragraphs: list[str] = []
    buf: list[str] = []
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

    The block is cut from the CONTENTS line (any case) to the first
    blank-line stretch after it. TOCs with blank lines between entries
    survive the cut only partially -- the split validation (duplicate
    headings, tiny fragments) catches that; the warnings report what
    happened.
    """
    m = re.search(r"^[ \t]*[Cc][Oo][Nn][Tt][Ee][Nn][Tt][Ss][ \t]*$", body, re.MULTILINE)
    if not m:
        return body
    after = body[m.end():]
    tail = re.search(r"\n[ \t]*\n[ \t]*\n", after)
    return body[: m.start()] + (after[tail.end():] if tail else after)


def parse(text: str, extra_headings: list[str] | None = None) -> dict:
    """Parse a PG plain-text ebook into stencil JSON.

    Args:
        text: The full ebook text, UTF-8.
        extra_headings: Additional regexes teaching the split an
            edition's heading style (DEC-007), e.g.
            ``r"^Chapter [IVXLCDM]+\\.]$"`` for illustration-caption
            headings.

    Returns:
        A dict with ``meta``, ``preamble``, ``units``, ``license``,
        and ``warnings``.

    Raises:
        GutenbergError: If the canonical PG START/END markers are
            missing or out of order.
    """
    m_start = START_MARK.search(text)
    m_end = END_MARK.search(text)
    if not m_start or not m_end or m_end.start() < m_start.start():
        raise GutenbergError("no canonical PG START/END markers found; is this a PG plain-text ebook?")

    header = text[: m_start.start()]
    body = text[m_start.end(): m_end.start()]
    license_text = text[m_end.end():]

    meta: dict[str, str | int] = {}
    for key in ("Title", "Author", "Release date", "Language"):
        km = re.search(rf"^{key}:\s+(.+)$", header, re.MULTILINE)
        if km:
            meta[key.lower().replace(" ", "_")] = km.group(1).strip()
    em = re.search(r"\[eBook #(\d+)\]", header)
    if em:
        meta["ebook_id"] = int(em.group(1))
        meta["source_url"] = f"https://www.gutenberg.org/ebooks/{em.group(1)}"

    body = drop_toc(body)

    extra_res = [re.compile(rx) for rx in (extra_headings or [])]

    def is_heading(line: str) -> bool:
        s = line.strip()
        return bool(HEADING_RE.match(s)) or any(rx.match(s) for rx in extra_res)

    units: list[dict] = []
    current: dict | None = None
    preamble: list[str] = []
    for line in body.split("\n"):
        if is_heading(line):
            if current:
                units.append(current)
            current = {"heading": line.strip(), "order": len(units) + 1, "lines": []}
        elif current is not None:
            current["lines"].append(line)
        else:
            preamble.append(line)
    if current:
        units.append(current)

    warnings: list[str] = []
    preamble_text = reflow("\n".join(preamble))
    preamble_words = len(preamble_text.split())
    if not units:
        warnings.append(
            "no structural headings found; the whole body sits in the preamble "
            "(poetry/essay, or a heading style the split does not recognize)"
        )
    elif preamble_words > 500:
        warnings.append(
            f"preamble holds {preamble_words} words; likely content the split "
            "missed (a heading style the split does not recognize -- some "
            "editions set headings as bracketed illustration captions -- or "
            "a genuine introduction/preface before the first heading)"
        )
    dup = sorted({u["heading"] for u in units
                  if [x["heading"] for x in units].count(u["heading"]) > 1})
    if dup:
        warnings.append(
            f"duplicate heading labels: {', '.join(dup)} -- an introduction or "
            "second part inside one file often repeats the book/chapter labels"
        )

    return {
        "meta": meta,
        "preamble": preamble_text,
        "units": [
            {"heading": u["heading"], "order": u["order"], "text": reflow("\n".join(u["lines"]))}
            for u in units
        ],
        "license": reflow(license_text),
        "warnings": warnings,
    }
