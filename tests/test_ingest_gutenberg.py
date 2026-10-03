"""Tests for ingest_gutenberg: marker slicing, CONTENTS drop, heading
split, paragraph reflow, metadata, preamble and license reporting."""

import importlib.util
import sys
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "ingest_gutenberg", Path(__file__).parent.parent / "stencil-work" / "ingest_gutenberg.py"
)
ingest = importlib.util.module_from_spec(_spec)
sys.modules["ingest_gutenberg"] = ingest
_spec.loader.exec_module(ingest)


def book(**overrides):
    """A small synthetic PG book exercising the known structural pieces."""
    text = """The Project Gutenberg eBook of Test Book

This eBook is for the use of anyone anywhere in the United States and
most other parts of the world at no cost.

Title: Test Book; or, a Fixture

Author: A. Tester

Release date: January 1, 2020 [eBook #1234]

Language: English

*** START OF THE PROJECT GUTENBERG EBOOK TEST BOOK ***

Test Book

by A. Tester


 CONTENTS

 Chapter 1
 Chapter 2




Chapter 1

First paragraph of one,
wrapped mid-line.

Second paragraph.

Chapter 2.

Body two.

*** END OF THE PROJECT GUTENBERG EBOOK TEST BOOK ***


Updated editions will replace the previous one.
"""
    for key, value in overrides.items():
        text = text.replace(key, value)
    return text


class ParseTest(unittest.TestCase):
    def test_requires_pg_markers(self):
        with self.assertRaises(SystemExit):
            ingest.parse("no markers here")

    def test_meta_fields_and_ebook_id(self):
        m = ingest.parse(book())["meta"]
        self.assertEqual(m["title"], "Test Book; or, a Fixture")
        self.assertEqual(m["author"], "A. Tester")
        self.assertEqual(m["ebook_id"], 1234)
        self.assertEqual(m["source_url"], "https://www.gutenberg.org/ebooks/1234")

    def test_contents_block_dropped_no_duplicate_headings(self):
        units = ingest.parse(book())["units"]
        self.assertEqual([u["heading"] for u in units], ["Chapter 1", "Chapter 2."])

    def test_split_and_orders(self):
        units = ingest.parse(book())["units"]
        self.assertEqual([u["order"] for u in units], [1, 2])

    def test_reflow_joins_wrapped_paragraphs(self):
        units = ingest.parse(book())["units"]
        self.assertEqual(
            units[0]["text"], "First paragraph of one, wrapped mid-line.\n\nSecond paragraph."
        )

    def test_heading_with_trailing_period_matches(self):
        # "Chapter 2." is a distinct heading, not body text
        self.assertIn("Body two.", ingest.parse(book())["units"][1]["text"])

    def test_preamble_reported_not_discarded(self):
        # title page text before CONTENTS and before the first heading
        p = ingest.parse(book())["preamble"]
        self.assertIn("Test Book", p)
        self.assertIn("by A. Tester", p)

    def test_license_captured_after_end_marker(self):
        lic = ingest.parse(book())["license"]
        self.assertIn("Updated editions will replace the previous one.", lic)

    def test_roman_and_book_headings_match(self):
        text = book().replace("Chapter 1", "BOOK I").replace("Chapter 2.", "Part 4")
        units = ingest.parse(text)["units"]
        self.assertEqual([u["heading"] for u in units], ["BOOK I", "Part 4"])

    def test_letters_split_like_chapters(self):
        text = book().replace("Chapter 1", "Letter 3").replace("Chapter 2.", "Chapter 1.")
        units = ingest.parse(text)["units"]
        self.assertEqual([u["heading"] for u in units], ["Letter 3", "Chapter 1."])

    def test_no_headings_yields_no_units_and_preamble_holds_body(self):
        text = book().replace("Chapter 1", "Section").replace("Chapter 2.", "Section")
        result = ingest.parse(text)
        self.assertEqual(result["units"], [])
        self.assertIn("First paragraph", result["preamble"])

    def test_text_before_start_marker_excluded_from_body(self):
        units = ingest.parse(book())["units"]
        self.assertNotIn("no cost", units[0]["text"])
        self.assertNotIn("eBook #1234", units[0]["text"])

    def test_warning_on_large_preamble(self):
        # un-recognize the first BODY heading (match it with its following
        # body text so the TOC entry is not touched) and pad past 500 words:
        # the content must land in the preamble and trip the warning
        text = book().replace(
            "Chapter 1\n\nFirst paragraph of one,",
            "[Chapter I.]\n\nFirst paragraph of one,",
        )
        text = text.replace(
            "First paragraph of one,\nwrapped mid-line.",
            "First paragraph of one,\nwrapped mid-line.\n\n" + " ".join("filler" for _ in range(600)),
        )
        result = ingest.parse(text)
        self.assertTrue(any("preamble holds" in w for w in result["warnings"]))

    def test_warning_on_duplicate_headings(self):
        # TOC entry is "Chapter 2" (no period); the body heading has one,
        # so only the body heading changes and collides with "Chapter 1"
        text = book().replace("Chapter 2.", "Chapter 1")
        result = ingest.parse(text)
        self.assertTrue(any("duplicate heading labels" in w for w in result["warnings"]))

    def test_warning_when_no_headings(self):
        result = ingest.parse(book().replace("Chapter 1", "Section").replace("Chapter 2.", "Section"))
        self.assertTrue(any("no structural headings" in w for w in result["warnings"]))

    def test_contents_match_is_case_insensitive(self):
        text = book().replace(" CONTENTS", " Contents")
        result = ingest.parse(text)
        self.assertEqual([u["heading"] for u in result["units"]], ["Chapter 1", "Chapter 2."])

    def test_extra_heading_regex_teaches_the_splitter(self):
        text = book().replace("Chapter 1\n", "[Chapter I.]\n")
        result = ingest.parse(text, [r"^\[Chapter [IVX]+\.\]$"])
        self.assertEqual(result["units"][0]["heading"], "[Chapter I.]")
        self.assertIn("First paragraph", result["units"][0]["text"])


if __name__ == "__main__":
    unittest.main()
