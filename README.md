# LADO marketplace

The official list of kits for [LADO](https://github.com/ladohq/lado). LADO knows it as the
marketplace `official`:

```bash
lado marketplaces update official      # get the latest list
lado kits add lado-dev -m official     # install a kit from it (latest vX.Y.Z)
lado kits add lado-dev@v0.9.1 -m official
```

This repository holds no kits and no skills: only `marketplace.yaml`, a list of kit names
and the git address of each kit's own repository. Versions, roles, skills and flows come
from the kits themselves. You can always install a kit that is not listed here straight
from git (`lado kits add <git-url>[@vX.Y.Z]`) or add your own marketplace
(`lado marketplaces add <name> <git-url>`).

## Kits

| Kit | Repository | What it is for |
|---|---|---|
| `lado-dev` | [ladohq/kit-lado-dev](https://github.com/ladohq/kit-lado-dev) | Developing LADO itself: a supervisor, an architect, developers and reviewers, with the flows `feature` and `fix`. |
| `kit-builder` | [ladohq/kit-builder](https://github.com/ladohq/kit-builder) | Building and evaluating LADO kits: a supervisor that interviews you and writes the blueprint, an author and a critic, with the flows `create` and `evaluate`. |
| `tracker-jira-server` | [ladohq/kit-tracker-jira-server](https://github.com/ladohq/kit-tracker-jira-server) | The `tracker` skill for Jira Server / Data Center 8.4+: process kits' roles find, read, create, move, comment on and link tasks; no agents, no MCP. |
| `sdlc` | [ladohq/kit-sdlc](https://github.com/ladohq/kit-sdlc) | Day-to-day development, one tracker task per run: an analyst designs the change with you as an openspec change, a developer builds it test-first, a reviewer drives local and external review rounds, an integrator archives and merges; you approve the design and the merge. Needs a tracker kit such as `tracker-jira-server`. |
| `tracker-yougile` | [ladohq/kit-tracker-yougile](https://github.com/ladohq/kit-tracker-yougile) | The `tracker` skill for Yougile (cloud, REST API v2): process kits' roles find, read, create, move, comment on, assign, label and link tasks; no agents, no MCP. |

## index.json

`index.json` is what LADO's Kits page shows of each listed kit without cloning it: its
address, latest release tag `vX.Y.Z` and that tag's commit, and, read from the kit at that
tag, its description, the LADO version it needs, its roles (with the first line of each
description), its own skills, its flows and its MCP servers (`"index": 1` is the format's
version). CI rebuilds it with `scripts/build_index.py` on each push to `main`, daily and by
hand, and commits it when it changed. Do not edit it by hand. A kit whose latest tag fails
its check keeps its previous entry and fails the build.

## Propose a kit

1. **One kit, one repository.** `kit.yaml` at the repository's root; several kits in one
   repository are not supported.
2. **A version in `kit.yaml`, equal to a tag.** Each release is a tag `vX.Y.Z` (or a
   pre-release `vX.Y.Z-rc.1`) whose `kit.yaml` says `version: X.Y.Z`. LADO refuses a kit
   whose tag and `version` disagree, and a kit pinned by a commit or branch. Never move a
   tag that was published: LADO warns when a tag points to another commit than the one
   installed.
3. **Check it** before tagging: `lado kits check . --tag vX.Y.Z` prints `OK`.
4. **Name the repository** `lado-kit-<name>` and give it the GitHub topic `lado-kit`, so
   people find it (kits of the ladohq organisation are named `kit-<name>`). This is a
   convention: LADO takes the kit's name from `kit.yaml`.
5. **Open a pull request** here that adds one line to `marketplace.yaml`
   (`<name>: <git-url>`, the name as in `kit.yaml`) and one row to the table above.

CI checks each kit the pull request adds or changes: it takes the kit's latest release tag
and runs `lado kits check --tag` on it, and checks that the name matches `kit.yaml`. A
maintainer reviews the kit itself: a kit's prompts steer agents and its MCP servers run
code, so we read what a kit does before we list it.

A listed kit that turns out vulnerable or malicious, or a problem in this repository's CI:
report it privately as [SECURITY.md](SECURITY.md) says.
