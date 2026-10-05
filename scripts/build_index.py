"""Build index.json, what LADO's Kits page shows of each kit in marketplace.yaml.

For each kit: its latest release tag vX.Y.Z and the tag's commit, checked as check_kits.py
does, then read at that tag: kit.yaml's description and dependencies.lado, the agents with
the first line of their description, the kit's own skills, its flows and its MCP servers.
A kit that fails keeps its entry from the index.json there was (only its address when there
was none); the build then exits 1, after writing the file.

Usage: build_index.py [--check]
--check (for pull requests): build and print, do not write index.json; a kit that fails is
printed as FAIL but does not fail the build (check_kits.py fails a pull request for the kits
it adds or changes). Errors of the builder itself still exit non-zero.
"""

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

from kitlib import FAILURES, LIST, Release, check, clone, failure, latest, listed

INDEX = Path("index.json")
VERSION = 1


def frontmatter(text: str) -> dict:
    """The YAML mapping between the leading --- lines (as LADO reads agents and skills)."""
    match = re.match(r"---[ \t]*\n(.*?)\n---[ \t]*(?:\n|$)", text, re.S)
    meta = yaml.safe_load(match.group(1)) if match else None
    return meta if isinstance(meta, dict) else {}


def first_line(text: object) -> str:
    lines = str(text or "").strip().splitlines()
    return lines[0].strip() if lines else ""


def read_kit(folder: Path) -> dict:
    """The index fields read from a kit's folder (all but address, latest and commit)."""
    meta = yaml.safe_load((folder / "kit.yaml").read_text()) or {}
    fields: dict = {"description": str(meta.get("description") or "").strip()}
    lado = (meta.get("dependencies") or {}).get("lado")
    if lado is not None:
        fields["lado"] = str(lado)
    agents, mcp = {}, {}
    for path in sorted((folder / "agents").glob("*.md")):
        agent = frontmatter(path.read_text())
        agents[path.stem] = first_line(agent.get("description"))
        for server, spec in (agent.get("mcp") or {}).items():
            mcp[server] = " ".join(map(str, spec.get("command") or []))
    fields["agents"] = agents
    fields["mcp"] = mcp
    skills = folder / "skills"
    fields["skills"] = sorted(p.parent.name for p in skills.glob("*/SKILL.md"))
    fields["flows"] = sorted(p.stem for p in (folder / "flows").glob("*.yaml"))
    return fields


def kit_entry(name: str, url: str) -> dict:
    """The entry of a kit that passes its check; raises one of FAILURES otherwise."""
    release: Release = latest(url)
    with tempfile.TemporaryDirectory() as tmp:
        clone(url, release.tag, tmp)
        check(name, release.tag, tmp)
        fields = read_kit(Path(tmp))
    return {"address": url, "latest": release.tag, "commit": release.commit, **fields}


def build(kits: dict[str, str], previous: dict, entry=kit_entry) -> tuple[dict, list[str]]:
    """The index of `kits` and the names that failed. A failed kit keeps its previous entry
    when that entry has the same address, else gets only its address."""
    entries, failed = {}, []
    for name, url in sorted(kits.items()):
        try:
            entries[name] = entry(name, url)
        except FAILURES as exc:
            print(f"FAIL {name} ({url}): {failure(exc)}")
            failed.append(name)
            old = previous.get(name)
            entries[name] = old if isinstance(old, dict) and old.get("address") == url else {
                "address": url
            }
            continue
        print(f"OK   {name} {entries[name]['latest']} ({url})")
    return {"index": VERSION, "kits": entries}, failed


def render(index: dict) -> str:
    return json.dumps(index, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None, entry=kit_entry) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="do not write index.json")
    args = parser.parse_args(argv)
    previous = json.loads(INDEX.read_text()).get("kits", {}) if INDEX.exists() else {}
    index, failed = build(listed(LIST.read_text()), previous, entry)
    text = render(index)
    if args.check:
        print(text, end="")
        if failed:
            print(f"warning: kits that fail their check (not failing --check): {', '.join(failed)}")
        return 0
    if not INDEX.exists() or INDEX.read_text() != text:
        INDEX.write_text(text)
        print(f"wrote {INDEX}")
    else:
        print(f"{INDEX} unchanged")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
