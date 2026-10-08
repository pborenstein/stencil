"""Post emitter: install an ingested page into a blog-style mimeo site.

Like the chapter emitter, nothing about a template is hardcoded
(DEC-004). The probe reads the site checkout and the emitter imitates
what it finds:

- post filename convention (date-prefixed or plain slug), from an
  existing file in ``content/posts/``
- post frontmatter keys, from the same file
- whether ``content/pages/`` exists (loose pages such as About)
- where images live, from the first conventional directory present

Excerpt, date, and tags are writing (DEC-006): this module copies
them from the JSON's ``meta`` when the agent supplied them, and
reports every probed key it had no value for instead of inventing one.
"""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path

from .emit import EmitError, slugify

IMAGE_DIRS = ("content/images", "content/assets", "content/img",
              "public/images", "src/images")
DATED_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$")


def probe_posts(site: Path) -> dict:
    """Probe a blog-style site checkout for its post conventions.

    Raises:
        EmitError: If ``content/posts/`` does not exist.
    """
    pdir = site / "content" / "posts"
    if not pdir.is_dir():
        raise EmitError(
            f"{pdir} does not exist -- not a blog-style site "
            "(no content/posts/ to imitate)."
        )
    samples = sorted(pdir.glob("*.md"))
    naming, keys = "{slug}.md", ["title", "date"]
    if samples:
        text = samples[0].read_text(encoding="utf-8")
        if DATED_RE.match(samples[0].name):
            naming = "{date}-{slug}.md"
        keys = []
        if text.startswith("---"):
            fm = text.split("---")[1]
            keys = [ln.split(":")[0].strip() for ln in fm.strip().splitlines()
                    if ":" in ln and not ln.startswith((" ", "\t"))]
    image_dir = next((d for d in IMAGE_DIRS if (site / d).is_dir()), IMAGE_DIRS[0])
    return {
        "naming": naming,
        "frontmatter_keys": keys,
        "pages_dir": (site / "content" / "pages").is_dir(),
        "image_dir": image_dir,
        "demo_posts": [p.name for p in samples],
    }


def _fm_value(key: str, title: str, date: str, meta: dict) -> str | None:
    """Render one frontmatter line's value, or None when no value exists."""
    fm = meta.get("frontmatter", {})
    if key == "title":
        return json.dumps(title, ensure_ascii=False)
    if key == "date":
        return date
    val = meta.get(key, fm.get(key))
    if val in (None, "", []):
        return None
    return json.dumps(val, ensure_ascii=False)


def emit_post(site: Path, page: dict, pr: dict, as_page: bool = False,
              replace_demo: bool = False) -> dict:
    """Write one post (or loose page) and copy its local images.

    Args:
        site: Site checkout root.
        page: Ingested page JSON (``meta``, ``text``, ``images``).
        pr: Result of :func:`probe_posts`.
        as_page: Write to ``content/pages/`` instead of ``content/posts/``.
        replace_demo: Delete the probed demo posts first (posts only).

    Returns:
        ``{"path": str, "missing": [keys with no value], "images": [copied names]}``.

    Raises:
        EmitError: If ``as_page`` is set and the site has no ``content/pages/``.
    """
    meta = page["meta"]
    title = meta["title"]
    when = str(meta.get("date") or meta.get("frontmatter", {}).get("date")
               or datetime.now().astimezone().date().isoformat())
    if as_page:
        if not pr["pages_dir"]:
            raise EmitError("site has no content/pages/ -- cannot emit a loose page")
        outdir = site / "content" / "pages"
        fname = f"{slugify(title)}.md"
        keys = [k for k in pr["frontmatter_keys"] if k not in ("date", "excerpt", "tags")]
    else:
        outdir = site / "content" / "posts"
        fname = pr["naming"].format(date=when, slug=slugify(title))
        keys = pr["frontmatter_keys"]
        if replace_demo:
            for name in pr["demo_posts"]:
                (outdir / name).unlink()

    text = page["text"]
    copied: list[str] = []
    for img in page.get("images", []):
        src = img.get("found")
        if not src:
            continue
        name = Path(src).name
        dest = site / pr["image_dir"]
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest / name)
        copied.append(name)
        public = "/" + pr["image_dir"].split("/", 1)[1] + "/" + name
        ref = img["ref"].replace(" ", "%20")
        text = text.replace(f"]({ref})", f"]({public})")

    fm: list[str] = []
    missing: list[str] = []
    for k in keys:
        v = _fm_value(k, title, when, meta)
        if v is None:
            missing.append(k)
        else:
            fm.append(f"{k}: {v}")
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / fname).write_text("---\n" + "\n".join(fm) + "\n---\n\n" + text + "\n",
                                encoding="utf-8")
    return {"path": str((outdir / fname).relative_to(site)), "missing": missing,
            "images": copied}
