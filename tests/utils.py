"""Test helpers: a minimal chaptered-site fixture in a temp dir."""

import tempfile
from pathlib import Path

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
    """A minimal chaptered site, mimicking eleventy-chapbook's shape."""

    def __init__(self, naming: tuple[str, ...] = ("ch01-the-beginning.md", "ch02-the-middle.md")):
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

    def chapter(self, name: str) -> str:
        return (self.root / "content" / "chapters" / name).read_text(encoding="utf-8")

    def chapters(self) -> list[str]:
        return sorted(p.name for p in (self.root / "content" / "chapters").glob("*.md"))
