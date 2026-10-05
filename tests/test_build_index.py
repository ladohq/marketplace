"""Tests of scripts/build_index.py: reading a kit, the fallback of a failed kit, the output.

Run: uv run --no-project --with pyyaml --with pytest pytest tests
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from build_index import build, read_kit, render  # noqa: E402
from kitlib import KitFailure  # noqa: E402

KIT = Path(__file__).parent / "fixtures" / "kit"
URL = "https://example.org/kit-demo.git"


def passing(name: str, url: str) -> dict:
    return {"address": url, "latest": "v1.2.3", "commit": "abc", **read_kit(KIT)}


def failing(name: str, url: str) -> dict:
    raise KitFailure("kits check failed")


class ReadKit(unittest.TestCase):
    def test_fields(self):
        self.assertEqual(
            read_kit(KIT),
            {
                "description": "A demo kit for the index tests.",
                "lado": ">=0.20",
                "agents": {"lead": "Leads the session.", "worker": "Does one task."},
                "mcp": {"search": "uvx search-server --verbose"},
                "skills": ["own-skill"],
                "flows": ["build", "review"],
            },
        )

    def test_no_lado_dependency(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        tmp = Path(folder.name)
        (tmp / "kit.yaml").write_text("name: bare\ndescription: Bare.\n")
        self.assertEqual(
            read_kit(tmp),
            {"description": "Bare.", "agents": {}, "mcp": {}, "skills": [], "flows": []},
        )


class Build(unittest.TestCase):
    def test_entry(self):
        index, failed = build({"demo": URL}, {}, passing)
        self.assertEqual(failed, [])
        self.assertEqual(index["index"], 1)
        self.assertEqual(index["kits"]["demo"]["address"], URL)

    def test_failed_kit_keeps_previous_entry(self):
        previous = {"demo": {"address": URL, "latest": "v1.0.0"}}
        index, failed = build({"demo": URL}, previous, failing)
        self.assertEqual(failed, ["demo"])
        self.assertEqual(index["kits"]["demo"], previous["demo"])

    def test_failed_kit_without_previous_entry_has_only_its_address(self):
        index, failed = build({"demo": URL}, {}, failing)
        self.assertEqual(index["kits"]["demo"], {"address": URL})

    def test_failed_kit_with_a_new_address_drops_the_old_entry(self):
        previous = {"demo": {"address": "https://example.org/old.git", "latest": "v1.0.0"}}
        index, _ = build({"demo": URL}, previous, failing)
        self.assertEqual(index["kits"]["demo"], {"address": URL})


class Render(unittest.TestCase):
    def test_deterministic(self):
        one, _ = build({"demo": URL, "another": URL}, {}, passing)
        two, _ = build({"another": URL, "demo": URL}, {}, passing)
        text = render(one)
        self.assertEqual(text, render(two))
        self.assertTrue(text.endswith("}\n"))
        self.assertEqual(json.loads(text), one)
        self.assertIn('\n  "kits": {\n    "another": {', text)
        keys = list(json.loads(text)["kits"]["demo"])
        self.assertEqual(keys, sorted(keys))


if __name__ == "__main__":
    unittest.main()
