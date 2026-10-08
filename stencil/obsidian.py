"""Obsidian page ingest.

Turns one Obsidian page into stencil JSON: splits YAML front matter,
converts Obsidian-only syntax to plain Markdown a mimeo site can
render, and reports what it did and what it could not classify
(DEC-002).

Conversions (all deterministic):

- ``[[Target]]`` / ``[[Target|Alias]]`` / ``[[Target#Heading]]`` become
  their display text; each is recorded in ``links`` so the agent can
  decide which should become real links
- ``![[image.png]]`` / ``![[image.png|300]]`` become
  ``![](image.png)``; standard ``![alt](path)`` images are kept; every
  local image is recorded in ``images`` with whether it was found
- ``![[Other note]]`` (a note embed) is replaced by a link-text
  placeholder and warned about -- transclusion needs a decision
- callouts (``> [!type] Title``) become blockquotes with a bold label
- ``%%comments%%`` are stripped
- ``^block-id`` anchors at line ends are stripped

Titles, excerpts, dates, and tags are writing and belong to the
agent; this module only surfaces what the page already declares.
"""

import re
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".avif"}

EMBED_RE = re.compile(r"!\[\[([^\]|]+?)(?:\|([^\]]*))?\]\]")
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+?)(?:#([^\]|]*))?(?:\|([^\]]*))?\]\]")
MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
CALLOUT_RE = re.compile(r"^(>\s*)\[!([A-Za-z-]+)\][+-]?[ \t]*(.*)$")
COMMENT_RE = re.compile(r"%%.*?%%", re.DOTALL)
BLOCK_ID_RE = re.compile(r"[ \t]+\^[A-Za-z0-9-]+[ \t]*$", re.MULTILINE)
FRONT_RE = re.compile(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", re.DOTALL)


class ObsidianError(Exception):
    """Raised when the input is not a readable Obsidian page."""


def parse_frontmatter(block: str) -> dict:
    """Parse the simple YAML subset Obsidian properties use.

    Supports ``key: value``, inline lists ``[a, b]``, and block lists
    (``key:`` followed by ``- item`` lines). Values it cannot read stay
    as raw strings.
    """
    fm: dict = {}
    key: str | None = None
    for line in block.splitlines():
        item = re.match(r"^\s+-\s+(.*)$", line)
        if item and key is not None:
            if not isinstance(fm.get(key), list):
                fm[key] = []
            fm[key].append(_scalar(item.group(1)))
            continue
        kv = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not kv:
            continue
        key, val = kv.group(1), kv.group(2).strip()
        if val == "":
            fm[key] = []
        elif val.startswith("[") and val.endswith("]"):
            fm[key] = [_scalar(v) for v in val[1:-1].split(",") if v.strip()]
        else:
            fm[key] = _scalar(val)
    return {k: v for k, v in fm.items() if v != []}


def _scalar(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def _is_image(ref: str) -> bool:
    return Path(ref.split("#")[0]).suffix.lower() in IMAGE_EXTS


def _find(ref: str, page: Path, vault: Path | None) -> Path | None:
    """Locate a referenced file beside the page, then anywhere in the vault."""
    for base in (page.parent, vault):
        if base is None:
            continue
        cand = base / ref
        if cand.is_file():
            return cand
    if vault is not None:
        hits = sorted(vault.rglob(Path(ref).name))
        if hits:
            return hits[0]
    return None


def parse(text: str, page: Path, vault: Path | None = None) -> dict:
    """Parse one Obsidian page into stencil JSON.

    Args:
        text: The page text, UTF-8.
        page: Path of the page (used for the fallback title and for
            locating images).
        vault: Optional vault root; images and links are also looked
            up there.

    Returns:
        A dict with ``meta``, ``text``, ``images``, ``links``, and
        ``warnings``.
    """
    text = text.replace("\r\n", "\n")
    warnings: list[str] = []
    fm: dict = {}
    m = FRONT_RE.match(text)
    if m:
        fm = parse_frontmatter(m.group(1))
        text = text[m.end():]

    text = COMMENT_RE.sub("", text)
    text = BLOCK_ID_RE.sub("", text)

    images: list[dict] = []
    links: list[dict] = []

    def add_image(ref: str, kind: str) -> None:
        if re.match(r"^[a-z]+://", ref):
            return
        found = _find(ref, page, vault)
        images.append({"ref": ref, "kind": kind, "found": str(found) if found else None})
        if found is None:
            warnings.append(f"image not found: {ref}")

    def embed(mo: re.Match[str]) -> str:
        ref, extra = mo.group(1).strip(), (mo.group(2) or "").strip()
        if _is_image(ref):
            add_image(ref, "embed")
            alt = "" if re.fullmatch(r"\d+(x\d+)?", extra) else extra
            return f"![{alt}]({ref.replace(' ', '%20')})"
        warnings.append(f"note/file embed left as text, needs a decision: ![[{ref}]]")
        return ref

    text = EMBED_RE.sub(embed, text)
    for mo in MD_IMAGE_RE.finditer(text):
        add_image(mo.group(2), "markdown")

    def wikilink(mo: re.Match[str]) -> str:
        target, heading, alias = mo.group(1).strip(), mo.group(2), mo.group(3)
        resolved = _find(target + ".md", page, vault) is not None if vault else None
        links.append({"target": target, "heading": heading, "alias": alias,
                      "resolved": resolved})
        return (alias or target).strip()

    text = WIKILINK_RE.sub(wikilink, text)

    out: list[str] = []
    in_callout = False
    for line in text.split("\n"):
        cm = CALLOUT_RE.match(line)
        if cm:
            in_callout = True
            label = cm.group(3).strip() or cm.group(2).capitalize()
            out.append(f"{cm.group(1)}**{label}**")
        else:
            if in_callout and not line.startswith(">"):
                in_callout = False
            out.append(line)
    text = "\n".join(out).strip()

    title = fm.get("title")
    h1 = re.match(r"^#[ \t]+(.+?)[ \t]*\n+", text + "\n")
    if not title and h1:
        title = h1.group(1)
        text = text[h1.end():].lstrip("\n")
        warnings.append("title taken from the leading H1 and removed from the text")
    if not title:
        title = page.stem
        warnings.append("no title in front matter or H1; using the filename")

    unresolved = [lk["target"] for lk in links if lk["resolved"] is False]
    if unresolved:
        warnings.append("wikilinks with no matching note in the vault, "
                        "rendered as plain text: " + ", ".join(sorted(set(unresolved))))

    return {
        "meta": {"title": title, "source": page.name,
                 "frontmatter": {k: v for k, v in fm.items() if k != "title"}},
        "text": text,
        "images": images,
        "links": links,
        "warnings": warnings,
    }
