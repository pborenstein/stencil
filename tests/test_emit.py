"""Tests for stencil.emit: site probing, chapter emission, stage flags,
and the metadata.js contract (url never touched)."""

import json

import pytest

from stencil.emit import (
    EmitError,
    apply_annotations,
    emit_chapters,
    emit_colophon,
    probe,
    update_metadata_js,
)
from tests.utils import SiteFixture

INGESTED = {
    "meta": {
        "title": 'Test Book; "quoted"',
        "author": "A. Tester",
        "release_date": "January 1, 2020 [eBook #1234]",
        "language": "English",
        "ebook_id": 1234,
        "source_url": "https://www.gutenberg.org/ebooks/1234",
    },
    "preamble": "",
    "units": [
        {"heading": "Chapter 1", "order": 1, "text": "Para one.\n\nPara two."},
        {"heading": "Chapter 2", "order": 2, "text": "Para one.\n\nPara two.\n\nPara three."},
    ],
    "license": "Updated editions will replace the previous one.",
    "warnings": [],
}


def test_naming_convention_from_demo_files():
    assert probe(SiteFixture().root)["naming"] == "ch{order:02d}-{slug}.md"


def test_naming_without_alpha_prefix():
    assert probe(SiteFixture(naming=("01-threshold.md",)).root)["naming"] == "{order:02d}-{slug}.md"


def test_frontmatter_keys_from_demo():
    assert probe(SiteFixture().root)["frontmatter_keys"] == ["title", "order", "description"]


def test_nav_next_order_after_about():
    assert probe(SiteFixture().root)["nav_next_order"] == 3


def test_empty_chapters_dir_gets_defaults():
    assert probe(SiteFixture(naming=()).root)["frontmatter_keys"] == ["title", "order"]


def test_missing_chapters_dir_raises():
    fx = SiteFixture(naming=())
    (fx.root / "content" / "chapters").rmdir()
    with pytest.raises(EmitError):
        probe(fx.root)


def test_emits_files_imitating_naming():
    fx = SiteFixture()
    emit_chapters(fx.root, INGESTED["units"], probe(fx.root), replace_demo=True)
    assert fx.chapters() == ["ch01-chapter-1.md", "ch02-chapter-2.md"]


def test_frontmatter_gets_title_and_order_only():
    fx = SiteFixture()
    emit_chapters(fx.root, INGESTED["units"], probe(fx.root), replace_demo=True)
    assert fx.chapter("ch01-chapter-1.md") == (
        '---\ntitle: "Chapter 1"\norder: 1\n---\n\nPara one.\n\nPara two.\n'
    )


def test_demo_chapters_survive_without_flag():
    fx = SiteFixture()
    emit_chapters(fx.root, INGESTED["units"], probe(fx.root), replace_demo=False)
    assert "ch01-the-beginning.md" in fx.chapters()


def test_colophon_page_carries_book_info_and_license():
    fx = SiteFixture()
    page = emit_colophon(fx.root, INGESTED, probe(fx.root))
    text = page.read_text(encoding="utf-8")
    assert "title: Colophon" in text
    assert "order: 3" in text
    assert "https://www.gutenberg.org/ebooks/1234" in text
    assert "**Author:** A. Tester" in text
    assert "Updated editions will replace the previous one." in text


def test_flat_keys_author_and_language():
    fx = SiteFixture()
    update_metadata_js(fx.root, INGESTED)
    src = (fx.root / "content/_data/metadata.js").read_text(encoding="utf-8")
    assert 'title: "Test Book; \\"quoted\\""' in src
    assert "Reading edition of" in src
    assert 'name: "A. Tester"' in src


def test_url_key_never_touched():
    fx = SiteFixture()
    update_metadata_js(fx.root, INGESTED)
    src = (fx.root / "content/_data/metadata.js").read_text(encoding="utf-8")
    assert 'url: "https://example.com/"' in src


def test_details_block_placed_after_paragraph(tmp_path):
    units = [dict(u) for u in INGESTED["units"]]
    path = tmp_path / "ann.json"
    path.write_text(json.dumps([
        {"chapter": 2, "after_paragraph": 1, "summary": "A note", "text": "The note body."}
    ]))
    assert apply_annotations(units, json.loads(path.read_text())) == 1
    assert units[1]["text"] == (
        "Para one.\n\n<details>\n<summary>A note</summary>\n\nThe note body.\n\n</details>"
        "\n\nPara two.\n\nPara three."
    )


def test_two_annotations_same_chapter_keep_positions(tmp_path):
    units = [dict(u) for u in INGESTED["units"]]
    anns = [
        {"chapter": 2, "after_paragraph": 1, "summary": "One", "text": "b1"},
        {"chapter": 2, "after_paragraph": 2, "summary": "Two", "text": "b2"},
    ]
    apply_annotations(units, anns)
    text = units[1]["text"]
    assert text.index("<summary>One</summary>") < text.index("Para two.")
    assert text.index("Para two.") < text.index("<summary>Two</summary>")
