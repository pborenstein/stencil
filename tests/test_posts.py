"""Tests for the post emitter."""

import json

import pytest
from click.testing import CliRunner

from stencil.cli import main
from stencil.emit import EmitError
from stencil.posts import emit_post, probe_posts


def make_site(tmp_path, dated=True, pages=True):
    posts = tmp_path / "content" / "posts"
    posts.mkdir(parents=True)
    name = "2025-01-01-hello.md" if dated else "hello.md"
    (posts / name).write_text(
        "---\ntitle: Hello\ndate: 2025-01-01\nexcerpt: x\ntags:\n  - a\n---\n\nbody\n",
        encoding="utf-8")
    if pages:
        (tmp_path / "content" / "pages").mkdir()
    (tmp_path / "content" / "images").mkdir()
    return tmp_path


def page(tmp_path):
    img = tmp_path / "src" / "pic.png"
    img.parent.mkdir(exist_ok=True)
    img.write_bytes(b"x")
    return {
        "meta": {"title": "On Walking", "excerpt": "Short.", "date": "2026-02-03",
                 "frontmatter": {"tags": ["walk", "essay"]}},
        "text": "Body ![](pic.png)",
        "images": [{"ref": "pic.png", "kind": "embed", "found": str(img)}],
    }


def test_probe_dated_and_keys(tmp_path):
    pr = probe_posts(make_site(tmp_path))
    assert pr["naming"] == "{date}-{slug}.md"
    assert pr["frontmatter_keys"] == ["title", "date", "excerpt", "tags"]
    assert pr["pages_dir"] and pr["image_dir"] == "content/images"


def test_probe_requires_posts_dir(tmp_path):
    with pytest.raises(EmitError):
        probe_posts(tmp_path)


def test_emit_post_writes_and_copies_images(tmp_path):
    site = make_site(tmp_path / "site")
    pr = probe_posts(site)
    res = emit_post(site, page(tmp_path), pr)
    assert res["path"] == "content/posts/2026-02-03-on-walking.md"
    out = (site / res["path"]).read_text(encoding="utf-8")
    assert 'excerpt: "Short."' in out and 'tags: ["walk", "essay"]' in out
    assert "![](/images/pic.png)" in out
    assert (site / "content/images/pic.png").exists()
    assert res["missing"] == []


def test_missing_keys_reported_not_invented(tmp_path):
    site = make_site(tmp_path / "site", dated=False)
    pr = probe_posts(site)
    p = page(tmp_path)
    del p["meta"]["excerpt"]
    res = emit_post(site, p, pr)
    assert res["path"] == "content/posts/on-walking.md"
    assert res["missing"] == ["excerpt"]
    assert "excerpt" not in (site / res["path"]).read_text(encoding="utf-8")


def test_emit_as_page_and_replace_demo(tmp_path):
    site = make_site(tmp_path / "site")
    pr = probe_posts(site)
    res = emit_post(site, page(tmp_path), pr, as_page=True)
    assert res["path"] == "content/pages/on-walking.md"
    text = (site / res["path"]).read_text(encoding="utf-8")
    assert "date" not in text and "tags" not in text
    emit_post(site, page(tmp_path), pr, replace_demo=True)
    assert not (site / "content/posts/2025-01-01-hello.md").exists()


def test_page_without_pages_dir_errors(tmp_path):
    site = make_site(tmp_path / "site", pages=False)
    with pytest.raises(EmitError):
        emit_post(site, page(tmp_path), probe_posts(site), as_page=True)


def test_cli(tmp_path):
    site = make_site(tmp_path / "site")
    pj = tmp_path / "page.json"
    pj.write_text(json.dumps(page(tmp_path)), encoding="utf-8")
    r = CliRunner().invoke(main, ["emit-post", str(site), str(pj)])
    assert r.exit_code == 0, r.output
    assert "post: content/posts/2026-02-03-on-walking.md" in r.output
