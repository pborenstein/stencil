"""Chapter emitter: install stencil JSON into a chaptered mimeo site.

Nothing about a specific template is hardcoded (DEC-004). The probe
reads the site checkout and the emitter imitates what it finds:

- chapter naming convention, from the existing chapter filenames
- chapter frontmatter keys, from an existing chapter file
  (only ``title`` and ``order`` are filled; deks are writing)
- loose-page navigation order, from pages like ``content/about.md``
- ``content/_data/metadata.js`` (JS module, edited by key; the ``url``
  key belongs to ``mimeo.template.json`` and is never touched)

Annotations are agent-written (DEC-006); this module only places the
collapsed ``<details><summary>`` blocks between source paragraphs.
"""

import re
import subprocess
from pathlib import Path

LANG_MAP = {"english": "en", "german": "de", "french": "fr", "spanish": "es",
            "italian": "it", "dutch": "nl", "portuguese": "pt"}


class EmitError(Exception):
    """Raised when the target site is not a chaptered site."""


def slugify(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "untitled"


def js_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _committed_chapter(site: Path) -> tuple[str, str] | None:
    """Return (name, text) of the first chapter committed at the site's HEAD.

    A chapters/ dir emptied by ``--replace-demo`` (or by hand) still has
    its template's chapters in git; they are the only remaining record
    of the template's frontmatter keys. None if the site is not a git
    checkout or HEAD holds no chapters.
    """
    def git(*args: str) -> str | None:
        try:
            r = subprocess.run(["git", "-C", str(site), *args], capture_output=True,
                               text=True, encoding="utf-8", check=True)
        except (OSError, subprocess.CalledProcessError):
            return None
        return r.stdout

    listing = git("ls-tree", "--name-only", "HEAD", "content/chapters/")
    names = sorted(n.rsplit("/", 1)[-1] for n in (listing or "").splitlines()
                   if n.endswith(".md"))
    if not names:
        return None
    text = git("show", f"HEAD:content/chapters/{names[0]}")
    return (names[0], text) if text is not None else None


def probe(site: Path) -> dict:
    """Probe a chaptered site checkout for its local conventions.

    Args:
        site: Path to the site checkout root.

    Returns:
        A dict with ``naming``, ``frontmatter_keys``,
        ``demo_chapters``, ``nav_next_order``, and ``metadata_js``.

    Raises:
        EmitError: If ``content/chapters/`` does not exist -- the
            pandoc templates take a single root file and are not
            chapter targets.
    """
    chdir = site / "content" / "chapters"
    if not chdir.is_dir():
        raise EmitError(
            f"{chdir} does not exist -- not a chaptered site "
            "(eleventy-chapbook / -folio / -pamphlet, or a site grown from one). "
            "The pandoc templates take a single root file and are not chapter targets."
        )
    demos = sorted(chdir.glob("*.md"))
    if demos:
        sample: tuple[str, str] | None = (demos[0].name,
                                          demos[0].read_text(encoding="utf-8"))
    else:
        sample = _committed_chapter(site)
    if sample is None:
        naming, keys = "{order:02d}-{slug}.md", ["title", "order"]
    else:
        name, text = sample
        m = re.match(r"^([a-z]+)(\d+)-(.+)\.md$", name)
        if m:
            prefix, digits, _ = m.groups()
            naming = f"{prefix}{{order:0{len(digits)}d}}-{{slug}}.md"
        else:
            naming = "{order:02d}-{slug}.md"
        keys = []
        if text.startswith("---"):
            fm = text.split("---")[1]
            keys = [ln.split(":")[0].strip() for ln in fm.strip().splitlines() if ":" in ln]

    nav_orders = []
    for p in sorted((site / "content").glob("*.md")):
        m = re.search(r"^\s+order:\s*(\d+)\s*$", p.read_text(encoding="utf-8"), re.MULTILINE)
        if m:
            nav_orders.append(int(m.group(1)))

    return {
        "naming": naming,
        "frontmatter_keys": keys,
        "demo_chapters": [p.name for p in demos],
        "nav_next_order": max(nav_orders) + 1 if nav_orders else 1,
        "metadata_js": (site / "content" / "_data" / "metadata.js").exists(),
    }


def emit_chapters(site: Path, units: list, pr: dict, replace_demo: bool) -> list[str]:
    """Write one file per unit, imitating the probed naming convention.

    Demo chapters are removed only when ``replace_demo`` is set;
    non-demo content is never touched.
    """
    chdir = site / "content" / "chapters"
    if replace_demo:
        for name in pr["demo_chapters"]:
            (chdir / name).unlink()
    written = []
    for u in units:
        fname = pr["naming"].format(order=u["order"], slug=slugify(u["heading"]))
        fm = []
        for k in pr["frontmatter_keys"]:
            if k == "title":
                fm.append(f'title: "{u["heading"]}"')
            elif k == "order":
                fm.append(f"order: {u['order']}")
        (chdir / fname).write_text(
            "---\n" + "\n".join(fm) + "\n---\n\n" + u["text"] + "\n", encoding="utf-8"
        )
        written.append(fname)
    return written


def emit_colophon(site: Path, ingested: dict, pr: dict) -> Path:
    """Write ``content/colophon.md`` with the PG book info and full license."""
    meta = ingested["meta"]
    lines = ["---", "title: Colophon", "eleventyNavigation:",
             "  key: Colophon", f"  order: {pr['nav_next_order']}", "---", "",
             "# [{{ title }}](/)", ""]
    if meta.get("source_url"):
        lines.append(f"This edition was installed from "
                     f"[Project Gutenberg eBook #{meta['ebook_id']}]({meta['source_url']}).")
        lines.append("")
    lines.append("## The book")
    lines.append("")
    for label, key in (("Title", "title"), ("Author", "author"),
                       ("Release date", "release_date"), ("Language", "language")):
        if meta.get(key):
            lines.append(f"- **{label}:** {meta[key]}")
    lines += ["", "## Project Gutenberg license", "", ingested["license"], ""]
    path = site / "content" / "colophon.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def update_metadata_js(site: Path, ingested: dict) -> list[str]:
    """Update title / description / language / author.name in metadata.js.

    The ``url`` key belongs to ``mimeo.template.json`` and is never
    touched. Returns the list of keys actually changed.
    """
    path = site / "content" / "_data" / "metadata.js"
    src = path.read_text(encoding="utf-8")
    meta = ingested["meta"]
    desc = f"Reading edition of {meta.get('title', 'this work')}"
    if meta.get("author"):
        desc += f" by {meta['author']}"
    desc += "."
    changed: list[str] = []

    def set_flat(key: str, value: str) -> None:
        nonlocal src
        esc = js_escape(value)
        new = re.sub(rf'^(\s*{key}:\s*)"[^"]*"(,?)\s*$',
                     rf'\g<1>"{esc}"\g<2>', src, flags=re.MULTILINE)
        if new != src:
            src = new
            changed.append(key)

    set_flat("title", str(meta.get("title", "")))
    set_flat("description", desc)
    if str(meta.get("language", "")).lower() in LANG_MAP:
        set_flat("language", LANG_MAP[str(meta["language"]).lower()])

    if meta.get("author"):
        am = re.search(r"\bauthor:\s*\{[^}]*\}", src)
        if am:
            block = am.group(0)
            new_block = re.sub(r'(\bname:\s*)"[^"]*"',
                               rf'\g<1>"{js_escape(str(meta["author"]))}"', block)
            if new_block != block:
                src = src.replace(block, new_block)
                changed.append("author.name")

    path.write_text(src, encoding="utf-8")
    return changed


def apply_annotations(units: list, annotations: list) -> int:
    """Interleave collapsed details blocks between source paragraphs.

    ``chapter`` is the ingest order; ``after_paragraph`` is 1-based.
    Returns the number of annotations placed.
    """
    for a in sorted(annotations, key=lambda a: (a["chapter"], -a["after_paragraph"])):
        u = units[a["chapter"] - 1]
        paras = u["text"].split("\n\n")
        block = (f'<details>\n<summary>{a["summary"]}</summary>\n\n'
                 f'{a["text"]}\n\n</details>')
        paras.insert(a["after_paragraph"], block)
        u["text"] = "\n\n".join(paras)
    return len(annotations)
