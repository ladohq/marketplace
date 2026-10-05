"""Check the kits marketplace.yaml adds or changes against a base commit.

For each such kit: its repository's latest release tag vX.Y.Z (git ls-remote), a shallow
clone of that tag, the name in its kit.yaml equal to the name in the list, and
`lado kits check . --tag <tag>`. Usage: check_kits.py [<base-ref>] (no base: every kit).
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

LIST = Path("marketplace.yaml")
RELEASE = re.compile(r"v(\d+)\.(\d+)\.(\d+)")


def listed(text: str) -> dict[str, str]:
    data = yaml.safe_load(text) or {}
    kits = data.get("kits") or {}
    if not isinstance(kits, dict):
        sys.exit("marketplace.yaml: kits must be a mapping name -> git address")
    return kits


def git(*args: str, cwd: str | None = None) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout


def latest(url: str) -> str:
    tags = [
        line.split("refs/tags/", 1)[1]
        for line in git("ls-remote", "--tags", "--refs", url).splitlines()
    ]
    releases = [(tuple(map(int, m.groups())), t) for t in tags if (m := RELEASE.fullmatch(t))]
    if not releases:
        raise RuntimeError(f"{url} has no release tags vX.Y.Z")
    return max(releases)[1]


def check(name: str, url: str) -> bool:
    try:
        tag = latest(url)
        with tempfile.TemporaryDirectory() as tmp:
            git("clone", "--quiet", "--depth", "1", "--branch", tag, url, tmp)
            meta = yaml.safe_load((Path(tmp) / "kit.yaml").read_text()) or {}
            if meta.get("name") != name:
                raise RuntimeError(f'kit.yaml at {tag} names the kit "{meta.get("name")}"')
            result = subprocess.run(
                ["lado", "kits", "check", ".", "--tag", tag],
                cwd=tmp, capture_output=True, text=True,
            )
            if result.returncode != 0:
                raise RuntimeError((result.stdout + result.stderr).strip())
    except (RuntimeError, subprocess.CalledProcessError, OSError) as exc:
        detail = getattr(exc, "stderr", None) or exc
        print(f"FAIL {name} ({url}): {detail}")
        return False
    print(f"OK   {name} {tag} ({url})")
    return True


def main() -> int:
    now = listed(LIST.read_text())
    before = listed(git("show", f"{sys.argv[1]}:{LIST}")) if len(sys.argv) > 1 else {}
    changed = {n: u for n, u in now.items() if before.get(n) != u}
    if not changed:
        print("no kit added or changed")
        return 0
    results = [check(name, url) for name, url in sorted(changed.items())]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
