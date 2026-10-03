#!/usr/bin/env python3
"""emit_chapters -- install stencil JSON into a chaptered mimeo site.

Usage:
    python3 emit_chapters.py SITE/ ingested.json \
        [--replace-demo] [--colophon] [--metadata] [--annotations ann.json]

SITE is a checkout of a chaptered site (eleventy-chapbook / -folio /
-pamphlet, or a site grown from one). The script PROBES the site first and
imitates what it finds, so nothing about a specific template is hardcoded:

    - chapter naming convention, from the existing chapter filenames
    - chapter frontmatter keys, from an existing chapter file
    - loose-page navigation order, from pages like content/about.md
    - content/_data/metadata.js (JS module, edited by key)

Emits one file per ingested unit. Only fills frontmatter keys it recognizes
(title, order); display titles, deks and descriptions are writing, not
parsing -- the caller (model layer) edits those afterwards.

Optional stages:
    --colophon     write content/colophon.md carrying the PG book info
                   and the full Project Gutenberg license tail
    --metadata     update title / description / language / author.name in
                   content/_data/metadata.js. The url key belongs to
                   mimeo.template.json and is never touched.
    --annotations  interleave <details><summary>…</summary>…</details>
                   blocks between source paragraphs (the amalgamedon.com
                   convention). The annotation file is written by the
                   model layer; this script only places the blocks:

                   [{"chapter": 1, "after_paragraph": 2,
                     "summary": "…", "text": "…"}, …]

                   chapter is the ingest order; after_paragraph is 1-based.
"""

import json
import re
import sys
from pathlib import Path

LANG_MAP = {"english": "en", "german": "de", "french": "fr", "spanish": "es",
            "italian": "it", "dutch": "nl", "portuguese": "pt"}


def slugify(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "untitled"


def js_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


# ---------------------------------------------------------------- probe

def probe(site: Path) -> dict:
    chdir = site / "content" / "chapters"
    demos = sorted(chdir.glob("*.md"))
    if not demos:
        naming, keys = "{order:02d}-{slug}.md", ["title", "order"]
    else:
        m = re.match(r"^([a-z]+)(\d+)-(.+)\.md$", demos[0].name)
        if m:
            prefix, digits, _ = m.groups()
            naming = f"{prefix}{{order:0{len(digits)}d}}-{{slug}}.md"
        else:
            naming = "{order:02d}-{slug}.md"
        keys = []
        text = demos[0].read_text(encoding="utf-8")
        if text.startswith("---"):
            fm = text.split("---")[1]
            keys = [ln.split(":")[0].strip() for ln in fm.strip().splitlines() if ":" in ln]

    nav_orders = []
    for p in sorted((site / "content").glob("*.md")):
        m = re.search(r"^\s+order:\s*(\d+)\s*$", p.read_text(encoding="utf-8"), re.M)
        if m:
            nav_orders.append(int(m.group(1)))

    return {
        "naming": naming,
        "frontmatter_keys": keys,
        "demo_chapters": [p.name for p in demos],
        "nav_next_order": max(nav_orders) + 1 if nav_orders else 1,
        "metadata_js": (site / "content" / "_data" / "metadata.js").exists(),
    }


# ---------------------------------------------------------------- emit

def emit_chapters(site: Path, units: list, pr: dict, replace_demo: bool) -> None:
    chdir = site / "content" / "chapters"
    if replace_demo:
        for name in pr["demo_chapters"]:
            (chdir / name).unlink()
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
        print("chapter:", fname)


def emit_colophon(site: Path, ingested: dict, pr: dict) -> None:
    meta = ingested["meta"]
    lines = ["---", "title: Colophon", "eleventyNavigation:",
             f"  key: Colophon", f"  order: {pr['nav_next_order']}", "---", "",
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
    (site / "content" / "colophon.md").write_text("\n".join(lines), encoding="utf-8")
    print("page: content/colophon.md")


def update_metadata_js(site: Path, ingested: dict) -> None:
    path = site / "content" / "_data" / "metadata.js"
    src = path.read_text(encoding="utf-8")
    meta = ingested["meta"]
    desc = f"Reading edition of {meta.get('title', 'this work')}"
    if meta.get("author"):
        desc += f" by {meta['author']}"
    desc += "."
    changed = []

    def set_flat(key: str, value: str) -> None:
        nonlocal src
        esc = js_escape(value)
        new = re.sub(rf'^(\s*{key}:\s*)"[^"]*"(,?)\s*$',
                     rf'\g<1>"{esc}"\g<2>', src, flags=re.M)
        if new != src:
            src = new
            changed.append(key)

    set_flat("title", meta.get("title", ""))
    set_flat("description", desc)
    if meta.get("language", "").lower() in LANG_MAP:
        set_flat("language", LANG_MAP[meta["language"].lower()])

    if meta.get("author"):
        am = re.search(r"\bauthor:\s*\{[^}]*\}", src)
        if am:
            block = am.group(0)
            new_block = re.sub(r'(\bname:\s*)"[^"]*"', rf'\g<1>"{js_escape(meta["author"])}"', block)
            if new_block != block:
                src = src.replace(block, new_block)
                changed.append("author.name")

    path.write_text(src, encoding="utf-8")
    print("metadata.js:", ", ".join(changed) if changed else "no keys matched (nothing written)")


def apply_annotations(units: list, ann_path: str) -> None:
    anns = json.load(open(ann_path, encoding="utf-8"))
    for a in sorted(anns, key=lambda a: (a["chapter"], -a["after_paragraph"])):
        u = units[a["chapter"] - 1]
        paras = u["text"].split("\n\n")
        block = (f'<details>\n<summary>{a["summary"]}</summary>\n\n'
                 f'{a["text"]}\n\n</details>')
        paras.insert(a["after_paragraph"], block)
        u["text"] = "\n\n".join(paras)
    print(f"annotations: {len(anns)} placed")


# ---------------------------------------------------------------- main

def main() -> None:
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)
    site = Path(args[0])
    ingested = json.load(open(args[1], encoding="utf-8"))
    pr = probe(site)
    print("probe:", json.dumps(pr))

    if "--annotations" in args:
        apply_annotations(ingested["units"], args[args.index("--annotations") + 1])
    emit_chapters(site, ingested["units"], pr, "--replace-demo" in args)
    if "--colophon" in args:
        emit_colophon(site, ingested, pr)
    if "--metadata" in args:
        if pr["metadata_js"]:
            update_metadata_js(site, ingested)
        else:
            print("metadata.js: not found, skipped")


if __name__ == "__main__":
    main()
