"""Tests for emit_chapters: site probing, chapter emission, each stage
flag, and the metadata.js contract (url never touched)."""

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "emit_chapters", Path(__file__).parent.parent / "stencil-work" / "emit_chapters.py"
)
emit = importlib.util.module_from_spec(_spec)
sys.modules["emit_chapters"] = emit
_spec.loader.exec_module(emit)


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
}

METADATA_JS = """export default {
  title: "Chapbook",
  subtitle: "",
  url: "https://example.com/",
  language: "en",
  description: "A description of this work.",
  author: {
    name: "Author Name",
  },
  image: "",
}
"""


class SiteFixture:
    """A minimal chaptered site in a temp dir, mimicking chapbook's shape."""

    def __init__(self, naming=("ch01-the-beginning.md", "ch02-the-middle.md")):
        self.root = Path(tempfile.mkdtemp())
        chdir = self.root / "content" / "chapters"
        chdir.mkdir(parents=True)
        for i, name in enumerate(naming, 1):
            (chdir / name).write_text(
                f"---\ntitle: Demo {i}\norder: {i}\ndescription: demo\n---\n\nbody\n",
                encoding="utf-8",
            )
        (self.root / "content" / "about.md").write_text(
            "---\ntitle: About\neleventyNavigation:\n  key: About\n  order: 2\n---\n\nabout\n",
            encoding="utf-8",
        )
        data = self.root / "content" / "_data"
        data.mkdir()
        (data / "metadata.js").write_text(METADATA_JS, encoding="utf-8")

    def chapter(self, name):
        return (self.root / "content" / "chapters" / name).read_text(encoding="utf-8")


class ProbeTest(unittest.TestCase):
    def test_naming_convention_from_demo_files(self):
        pr = emit.probe(SiteFixture().root)
        self.assertEqual(pr["naming"], "ch{order:02d}-{slug}.md")

    def test_naming_without_alpha_prefix(self):
        pr = emit.probe(SiteFixture(naming=("01-threshold.md",)).root)
        self.assertEqual(pr["naming"], "{order:02d}-{slug}.md")

    def test_frontmatter_keys_from_demo(self):
        pr = emit.probe(SiteFixture().root)
        self.assertEqual(pr["frontmatter_keys"], ["title", "order", "description"])

    def test_nav_next_order_after_about(self):
        self.assertEqual(emit.probe(SiteFixture().root)["nav_next_order"], 3)

    def test_empty_chapters_dir_gets_defaults(self):
        self.assertEqual(emit.probe(SiteFixture(naming=()).root)["frontmatter_keys"],
                         ["title", "order"])

    def test_missing_chapters_dir_exits_with_message(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "content").mkdir()
            with self.assertRaises(SystemExit):
                emit.probe(root)


class EmitTest(unittest.TestCase):
    def test_emits_files_imitating_naming(self):
        fx = SiteFixture()
        pr = emit.probe(fx.root)
        emit.emit_chapters(fx.root, INGESTED["units"], pr, replace_demo=True)
        self.assertEqual((fx.root / "content/chapters").glob("*.md") and
                         sorted(p.name for p in (fx.root / "content/chapters").glob("*.md")),
                         ["ch01-chapter-1.md", "ch02-chapter-2.md"])

    def test_frontmatter_gets_title_and_order_only(self):
        fx = SiteFixture()
        pr = emit.probe(fx.root)
        emit.emit_chapters(fx.root, INGESTED["units"], pr, replace_demo=True)
        self.assertEqual(
            fx.chapter("ch01-chapter-1.md"),
            '---\ntitle: "Chapter 1"\norder: 1\n---\n\nPara one.\n\nPara two.\n',
        )

    def test_demo_chapters_survive_without_flag(self):
        fx = SiteFixture()
        pr = emit.probe(fx.root)
        emit.emit_chapters(fx.root, INGESTED["units"], pr, replace_demo=False)
        names = sorted(p.name for p in (fx.root / "content/chapters").glob("*.md"))
        self.assertIn("ch01-the-beginning.md", names)

    def test_colophon_page_carries_book_info_and_license(self):
        fx = SiteFixture()
        pr = emit.probe(fx.root)
        emit.emit_colophon(fx.root, INGESTED, pr)
        page = (fx.root / "content/colophon.md").read_text(encoding="utf-8")
        self.assertIn("title: Colophon", page)
        self.assertIn("order: 3", page)
        self.assertIn("https://www.gutenberg.org/ebooks/1234", page)
        self.assertIn("**Author:** A. Tester", page)
        self.assertIn("Updated editions will replace the previous one.", page)


class MetadataTest(unittest.TestCase):
    def test_flat_keys_author_and_language(self):
        fx = SiteFixture()
        emit.update_metadata_js(fx.root, INGESTED)
        src = (fx.root / "content/_data/metadata.js").read_text(encoding="utf-8")
        self.assertIn('title: "Test Book; \\"quoted\\""', src)
        self.assertIn("Reading edition of", src)
        self.assertIn('name: "A. Tester"', src)

    def test_url_key_never_touched(self):
        fx = SiteFixture()
        emit.update_metadata_js(fx.root, INGESTED)
        src = (fx.root / "content/_data/metadata.js").read_text(encoding="utf-8")
        self.assertIn('url: "https://example.com/"', src)


class AnnotationTest(unittest.TestCase):
    def test_details_block_placed_after_paragraph(self):
        units = [dict(u) for u in INGESTED["units"]]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump([{"chapter": 2, "after_paragraph": 1,
                        "summary": "A note", "text": "The note body."}], f)
            path = f.name
        emit.apply_annotations(units, path)
        self.assertEqual(
            units[1]["text"],
            "Para one.\n\n<details>\n<summary>A note</summary>\n\nThe note body.\n\n</details>"
            "\n\nPara two.\n\nPara three.",
        )

    def test_two_annotations_same_chapter_keep_positions(self):
        units = [dict(u) for u in INGESTED["units"]]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump([
                {"chapter": 2, "after_paragraph": 1, "summary": "One", "text": "b1"},
                {"chapter": 2, "after_paragraph": 2, "summary": "Two", "text": "b2"},
            ], f)
            path = f.name
        emit.apply_annotations(units, path)
        text = units[1]["text"]
        self.assertLess(text.index("<summary>One</summary>"), text.index("<summary>Two</summary>"))
        self.assertLess(text.index("<summary>One</summary>"), text.index("Para two."))
        self.assertLess(text.index("Para two."), text.index("<summary>Two</summary>"))


if __name__ == "__main__":
    unittest.main()
