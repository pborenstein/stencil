"""Command-line interface for Stencil."""

import click

from .. import __version__
from .emit_chapters import emit_chapters
from .ingest_gutenberg import ingest_gutenberg


@click.group()
@click.version_option(version=__version__, prog_name="Stencil")
def main() -> None:
    """Install content into mimeo sites from source material."""


main.add_command(ingest_gutenberg)
main.add_command(emit_chapters)


__all__ = [
    "emit_chapters",
    "ingest_gutenberg",
    "main",
]
