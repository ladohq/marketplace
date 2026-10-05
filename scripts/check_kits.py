"""Check the kits marketplace.yaml adds or changes against a base commit.

For each such kit: its repository's latest release tag vX.Y.Z (git ls-remote), a shallow
clone of that tag, the name in its kit.yaml equal to the name in the list, and
`lado kits check . --tag <tag>`. Usage: check_kits.py [<base-ref>] (no base: every kit).
"""

import sys
import tempfile

from kitlib import FAILURES, LIST, check, clone, failure, git, latest, listed


def check_kit(name: str, url: str) -> bool:
    try:
        tag = latest(url).tag
        with tempfile.TemporaryDirectory() as tmp:
            clone(url, tag, tmp)
            check(name, tag, tmp)
    except FAILURES as exc:
        print(f"FAIL {name} ({url}): {failure(exc)}")
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
    results = [check_kit(name, url) for name, url in sorted(changed.items())]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
