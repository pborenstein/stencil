"""ingest-gutenberg command: PG plain text to stencil JSON on stdout."""

import json
from pathlib import Path

import click

from ..gutenberg import GutenbergError, parse


@click.command(name="ingest-gutenberg")
@click.argument("book", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--extra-heading",
    "extra_headings",
    multiple=True,
    metavar="REGEX",
    help="Teach the split an edition's heading style (repeatable), "
    "e.g. '^Chapter [IVXLCDM]+\\.]$' for illustration-caption headings.",
)
def ingest_gutenberg(book: Path, extra_headings: tuple[str, ...]) -> None:
    """Parse a Project Gutenberg plain-text ebook into stencil JSON.

    Writes the JSON to stdout: meta, preamble, units, license, and
    warnings. Read the warnings before emitting -- they carry the
    decisions the agent owns.
    """
    text = book.read_text(encoding="utf-8")
    try:
        result = parse(text, list(extra_headings))
    except GutenbergError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(result, ensure_ascii=False, indent=1))
