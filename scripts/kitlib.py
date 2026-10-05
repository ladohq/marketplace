"""What check_kits.py and build_index.py share: the list, a kit's latest release, its check.

A kit is checked at its repository's latest release tag vX.Y.Z (git ls-remote): a shallow
clone of that tag, the name in its kit.yaml equal to the name in the list, and
`lado kits check . --tag <tag>`.
"""

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

LIST = Path("marketplace.yaml")
RELEASE = re.compile(r"v(\d+)\.(\d+)\.(\d+)")


class KitFailure(RuntimeError):
    """A kit that fails its check, with what went wrong."""


@dataclass(frozen=True)
class Release:
    tag: str
    commit: str  # the tag's commit (an annotated tag peeled)


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


def latest(url: str) -> Release:
    """The highest release tag vX.Y.Z of the repository at `url` and its commit."""
    shas: dict[str, str] = {}
    peeled: dict[str, str] = {}
    for line in git("ls-remote", "--tags", url).splitlines():
        sha, ref = line.split("\t", 1)
        tag = ref.removeprefix("refs/tags/")
        if tag.endswith("^{}"):
            peeled[tag[:-3]] = sha
        else:
            shas[tag] = sha
    releases = [(tuple(map(int, m.groups())), t) for t in shas if (m := RELEASE.fullmatch(t))]
    if not releases:
        raise KitFailure(f"{url} has no release tags vX.Y.Z")
    tag = max(releases)[1]
    return Release(tag, peeled.get(tag, shas[tag]))


def clone(url: str, tag: str, dest: str) -> None:
    git("clone", "--quiet", "--depth", "1", "--branch", tag, url, dest)


def check(name: str, tag: str, folder: str) -> None:
    """Raise KitFailure unless the kit cloned in `folder` at `tag` passes its checks."""
    meta = yaml.safe_load((Path(folder) / "kit.yaml").read_text()) or {}
    if meta.get("name") != name:
        raise KitFailure(f'kit.yaml at {tag} names the kit "{meta.get("name")}"')
    result = subprocess.run(
        ["lado", "kits", "check", ".", "--tag", tag],
        cwd=folder, capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise KitFailure((result.stdout + result.stderr).strip())


def failure(exc: Exception) -> object:
    """What to print for a failed kit: git's stderr when git failed."""
    return getattr(exc, "stderr", None) or exc


FAILURES = (KitFailure, subprocess.CalledProcessError, OSError)
