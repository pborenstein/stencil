"""Tests for stencil.gutenberg: marker slicing, CONTENTS drop, heading
split, paragraph reflow, metadata, preamble/license/warnings reporting."""

import pytest

from stencil.gutenberg import GutenbergError, parse


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


def test_requires_pg_markers():
    with pytest.raises(GutenbergError):
        parse("no markers here")


def test_meta_fields_and_ebook_id():
    m = parse(book())["meta"]
    assert m["title"] == "Test Book; or, a Fixture"
    assert m["author"] == "A. Tester"
    assert m["ebook_id"] == 1234
    assert m["source_url"] == "https://www.gutenberg.org/ebooks/1234"


def test_contents_block_dropped_no_duplicate_headings():
    units = parse(book())["units"]
    assert [u["heading"] for u in units] == ["Chapter 1", "Chapter 2."]


def test_split_and_orders():
    units = parse(book())["units"]
    assert [u["order"] for u in units] == [1, 2]


def test_reflow_joins_wrapped_paragraphs():
    units = parse(book())["units"]
    assert units[0]["text"] == "First paragraph of one, wrapped mid-line.\n\nSecond paragraph."


def test_heading_with_trailing_period_matches():
    # "Chapter 2." is a distinct heading, not body text
    assert "Body two." in parse(book())["units"][1]["text"]


def test_preamble_reported_not_discarded():
    # title page text before CONTENTS and before the first heading
    p = parse(book())["preamble"]
    assert "Test Book" in p
    assert "by A. Tester" in p


def test_license_captured_after_end_marker():
    assert "Updated editions will replace the previous one." in parse(book())["license"]


def test_roman_and_book_headings_match():
    text = book().replace("Chapter 1", "BOOK I").replace("Chapter 2.", "Part 4")
    units = parse(text)["units"]
    assert [u["heading"] for u in units] == ["BOOK I", "Part 4"]


def test_letters_split_like_chapters():
    text = book().replace("Chapter 1", "Letter 3").replace("Chapter 2.", "Chapter 1.")
    units = parse(text)["units"]
    assert [u["heading"] for u in units] == ["Letter 3", "Chapter 1."]


def test_no_headings_yields_no_units_and_preamble_holds_body():
    text = book().replace("Chapter 1", "Section").replace("Chapter 2.", "Section")
    result = parse(text)
    assert result["units"] == []
    assert "First paragraph" in result["preamble"]


def test_text_before_start_marker_excluded_from_body():
    units = parse(book())["units"]
    assert "no cost" not in units[0]["text"]
    assert "eBook #1234" not in units[0]["text"]


def test_warning_on_large_preamble():
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
    result = parse(text)
    assert any("preamble holds" in w for w in result["warnings"])


def test_warning_on_duplicate_headings():
    # TOC entry is "Chapter 2" (no period); the body heading has one,
    # so only the body heading changes and collides with "Chapter 1"
    text = book().replace("Chapter 2.", "Chapter 1")
    result = parse(text)
    assert any("duplicate heading labels" in w for w in result["warnings"])


def test_warning_when_no_headings():
    result = parse(book().replace("Chapter 1", "Section").replace("Chapter 2.", "Section"))
    assert any("no structural headings" in w for w in result["warnings"])


def test_contents_match_is_case_insensitive():
    text = book().replace(" CONTENTS", " Contents")
    result = parse(text)
    assert [u["heading"] for u in result["units"]] == ["Chapter 1", "Chapter 2."]


def test_extra_heading_regex_teaches_the_splitter():
    text = book().replace(
        "Chapter 1\n\nFirst paragraph of one,",
        "[Chapter I.]\n\nFirst paragraph of one,",
    )
    result = parse(text, [r"^\[Chapter [IVX]+\.\]$"])
    assert result["units"][0]["heading"] == "[Chapter I.]"
    assert "First paragraph" in result["units"][0]["text"]


def test_clean_book_has_no_warnings():
    assert parse(book())["warnings"] == []


def test_toc_shell_run_dropped_and_reported():
    # numeral-only TOC with no CONTENTS label splits into empty units
    text = book().replace(" CONTENTS\n\n Chapter 1\n Chapter 2\n\n\n\n\n", "Chapter 1\nChapter 2\nChapter 3\n\n")
    result = parse(text)
    assert [u["heading"] for u in result["units"]] == ["Chapter 1", "Chapter 2."]
    assert [u["order"] for u in result["units"]] == [1, 2]
    assert any("dropped 3 empty units" in w for w in result["warnings"])


def test_lone_empty_unit_kept_and_flagged():
    text = book().replace("Chapter 1\n\nFirst", "Part 1\n\nChapter 1\n\nFirst")
    result = parse(text)
    assert [u["heading"] for u in result["units"]] == ["Part 1", "Chapter 1", "Chapter 2."]
    assert any("empty unit kept: Part 1" in w for w in result["warnings"])
