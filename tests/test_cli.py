"""Tests for the stencil CLI: ingest-gutenberg and emit-chapters."""

import json

from click.testing import CliRunner

from stencil.cli import main
from tests.test_gutenberg import book
from tests.utils import SiteFixture


def test_version():
    result = CliRunner().invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "Stencil" in result.output


def test_ingest_gutenberg_writes_json_to_stdout(tmp_path):
    path = tmp_path / "book.txt"
    path.write_text(book(), encoding="utf-8")
    result = CliRunner().invoke(main, ["ingest-gutenberg", str(path)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["meta"]["ebook_id"] == 1234
    assert len(data["units"]) == 2
    assert data["warnings"] == []


def test_ingest_gutenberg_extra_heading(tmp_path):
    path = tmp_path / "book.txt"
    path.write_text(book().replace(
        "Chapter 1\n\nFirst paragraph of one,",
        "[Chapter I.]\n\nFirst paragraph of one,",
    ), encoding="utf-8")
    result = CliRunner().invoke(
        main, ["ingest-gutenberg", str(path), "--extra-heading", r"^\[Chapter [IVX]+\.\]$"]
    )
    assert result.exit_code == 0
    assert json.loads(result.output)["units"][0]["heading"] == "[Chapter I.]"


def test_ingest_gutenberg_rejects_non_pg_text(tmp_path):
    path = tmp_path / "notabook.txt"
    path.write_text("no markers here", encoding="utf-8")
    result = CliRunner().invoke(main, ["ingest-gutenberg", str(path)])
    assert result.exit_code != 0
    assert "START/END markers" in result.output


def test_emit_chapters_full_pipeline(tmp_path):
    site = SiteFixture()
    ingested = tmp_path / "ingested.json"
    ingested.write_text(json.dumps({
        "meta": {"title": "Test Book", "author": "A. Tester", "ebook_id": 1234,
                 "source_url": "https://www.gutenberg.org/ebooks/1234",
                 "release_date": "January 1, 2020", "language": "English"},
        "units": [{"heading": "Chapter 1", "order": 1, "text": "Para one."}],
        "license": "License text.",
    }), encoding="utf-8")
    result = CliRunner().invoke(main, [
        "emit-chapters", str(site.root), str(ingested),
        "--replace-demo", "--colophon", "--metadata",
    ])
    assert result.exit_code == 0
    assert site.chapters() == ["ch01-chapter-1.md"]
    assert (site.root / "content" / "colophon.md").exists()
    src = (site.root / "content/_data/metadata.js").read_text(encoding="utf-8")
    assert 'title: "Test Book"' in src
    assert 'url: "https://example.com/"' in src


def test_emit_chapters_refuses_non_chaptered_site(tmp_path):
    empty = tmp_path / "site"
    (empty / "content").mkdir(parents=True)
    ingested = tmp_path / "ingested.json"
    ingested.write_text(json.dumps({"meta": {}, "units": [], "license": ""}), encoding="utf-8")
    result = CliRunner().invoke(main, ["emit-chapters", str(empty), str(ingested)])
    assert result.exit_code != 0
    assert "not a chaptered site" in result.output
