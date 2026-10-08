"""ingest-obsidian command: one Obsidian page to stencil JSON on stdout."""

import json
from pathlib import Path

import click

from ..obsidian import ObsidianError, parse


@click.command(name="ingest-obsidian")
@click.argument("page", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--vault", type=click.Path(exists=True, file_okay=False, path_type=Path),
              help="Vault root; images and wikilink targets are also looked up there.")
def ingest_obsidian(page: Path, vault: Path | None) -> None:
    """Parse an Obsidian page into stencil JSON.

    Writes the JSON to stdout: meta (title, front matter), text,
    images, links, and warnings. Wikilinks flatten to display text,
    image embeds become Markdown images, callouts become blockquotes.
    Read the warnings before emitting.
    """
    try:
        result = parse(page.read_text(encoding="utf-8"), page, vault)
    except ObsidianError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(result, ensure_ascii=False, indent=1))
