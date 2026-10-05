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
