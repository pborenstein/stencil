"""emit-chapters command: install stencil JSON into a chaptered site."""

import json
from pathlib import Path

import click

from ..emit import (
    EmitError,
    apply_annotations,
    emit_colophon,
    probe,
    update_metadata_js,
)
from ..emit import (
    emit_chapters as _emit_chapters,
)


@click.command(name="emit-chapters")
@click.argument("site", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("ingested", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--replace-demo", is_flag=True,
              help="Delete the site's demo chapters before emitting.")
@click.option("--colophon", is_flag=True,
              help="Write content/colophon.md with the PG book info and full license.")
@click.option("--metadata", is_flag=True,
              help="Update title/description/language/author.name in metadata.js "
              "(the url key is never touched).")
@click.option("--annotations", type=click.Path(exists=True, dir_okay=False, path_type=Path),
              help="Agent-written annotations JSON; blocks are placed between "
              "source paragraphs.")
def emit_chapters(
    site: Path,
    ingested: Path,
    replace_demo: bool,
    colophon: bool,
    metadata: bool,
    annotations: Path | None,
) -> None:
    """Install stencil JSON into a chaptered site checkout.

    The site is probed first and its local conventions imitated:
    naming, frontmatter keys, navigation order. After emit, run the
    site's own build -- it is the acceptance gate.
    """
    data = json.loads(ingested.read_text(encoding="utf-8"))
    try:
        pr = probe(site)
    except EmitError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"probe: {json.dumps(pr)}")

    if annotations is not None:
        placed = apply_annotations(data["units"],
                                   json.loads(annotations.read_text(encoding="utf-8")))
        click.echo(f"annotations: {placed} placed")

    for fname in _emit_chapters(site, data["units"], pr, replace_demo):
        click.echo(f"chapter: {fname}")

    if colophon:
        path = emit_colophon(site, data, pr)
        click.echo(f"page: {path.relative_to(site)}")

    if metadata:
        if pr["metadata_js"]:
            changed = update_metadata_js(site, data)
            click.echo("metadata.js: " + (", ".join(changed) if changed
                                          else "no keys matched (nothing written)"))
        else:
            click.echo("metadata.js: not found, skipped")
