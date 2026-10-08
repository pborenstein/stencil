"""emit-post command: install an ingested page as a post or loose page."""

import json
from pathlib import Path

import click

from ..emit import EmitError
from ..posts import emit_post as _emit_post
from ..posts import probe_posts


@click.command(name="emit-post")
@click.argument("site", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("page", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--page", "as_page", is_flag=True,
              help="Write to content/pages/ as a loose page instead of a post.")
@click.option("--replace-demo", is_flag=True,
              help="Delete the site's demo posts before emitting (posts only).")
def emit_post(site: Path, page: Path, as_page: bool, replace_demo: bool) -> None:
    """Install ingested JSON (e.g. from ingest-obsidian) into a blog site.

    The site is probed first and its conventions imitated: filename
    pattern, frontmatter keys, image directory. Excerpt, date, and
    tags come from the JSON's meta (agent-written); any probed key
    with no value is reported, never invented. Run the site's build
    afterward -- it is the acceptance gate.
    """
    data = json.loads(page.read_text(encoding="utf-8"))
    try:
        pr = probe_posts(site)
        click.echo(f"probe: {json.dumps(pr)}")
        result = _emit_post(site, data, pr, as_page=as_page, replace_demo=replace_demo)
    except EmitError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"{'page' if as_page else 'post'}: {result['path']}")
    for name in result["images"]:
        click.echo(f"image: {name}")
    if result["missing"]:
        click.echo("no value for keys: " + ", ".join(result["missing"]))
