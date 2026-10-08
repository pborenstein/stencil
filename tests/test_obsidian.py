"""Tests for the Obsidian page ingest."""

import json

from click.testing import CliRunner

from stencil.cli import main
from stencil.obsidian import parse, parse_frontmatter

PAGE = """---
title: On Walking
tags: [walk, essay]
aliases:
  - Walking
date: 2026-01-02
---
Intro with [[Other Note]] and [[Other Note|an alias]] and [[Note#Part]].
%%hidden%% visible ^abc123

![[pic.png]]
![[pic.png|300]]
![[Some Note]]
![alt](pic.png)

> [!tip] Careful
> Mind the step.

> [!note]
> Plain.
"""


def test_frontmatter_lists_and_scalars():
    fm = parse_frontmatter("title: \"A\"\ntags: [a, b]\naliases:\n  - x\n  - y\n")
    assert fm == {"title": "A", "tags": ["a", "b"], "aliases": ["x", "y"]}


def test_parse_converts_syntax(tmp_path):
    (tmp_path / "pic.png").write_bytes(b"x")
    (tmp_path / "Other Note.md").write_text("x", encoding="utf-8")
    page = tmp_path / "walking.md"
    r = parse(PAGE, page, tmp_path)
    t = r["text"]
    assert r["meta"]["title"] == "On Walking"
    assert r["meta"]["frontmatter"]["tags"] == ["walk", "essay"]
    assert "Intro with Other Note and an alias and Note." in t
    assert "hidden" not in t and "^abc123" not in t
    assert t.count("![](pic.png)") == 2
    assert "> **Careful**" in t and "> **Note**" in t
    assert "[!tip]" not in t
    assert all(i["found"] for i in r["images"])
    assert any("embed left as text" in w for w in r["warnings"])
    assert any("wikilinks with no matching note" in w for w in r["warnings"])
    assert {lk["target"]: lk["resolved"] for lk in r["links"]}["Other Note"] is True


def test_missing_image_and_title_fallbacks(tmp_path):
    page = tmp_path / "slug.md"
    r = parse("# Heading Title\n\nBody ![[gone.png]]\n", page)
    assert r["meta"]["title"] == "Heading Title"
    assert r["text"].startswith("Body")
    assert any("image not found: gone.png" in w for w in r["warnings"])
    r2 = parse("Just text\n", page)
    assert r2["meta"]["title"] == "slug"


def test_cli_writes_json(tmp_path):
    page = tmp_path / "p.md"
    page.write_text(PAGE, encoding="utf-8")
    result = CliRunner().invoke(main, ["ingest-obsidian", str(page), "--vault", str(tmp_path)])
    assert result.exit_code == 0
    assert json.loads(result.output)["meta"]["title"] == "On Walking"
