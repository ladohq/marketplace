# Security

## Report a problem

Report privately, not in a public issue or pull request, when:

- a kit listed in `marketplace.yaml` is vulnerable or malicious: its prompts steer agents
  somewhere they should not go, its MCP servers run code they should not, or its repository
  was taken over or a published tag was moved;
- this repository's CI can be abused: a workflow, `scripts/` or how `index.json` is built
  and pushed.

Use GitHub's private vulnerability reporting: the **Security** tab of this repository,
**Report a vulnerability**. Name the kit and its tag (or the workflow or script), and say
what it does and how to see it. A problem in LADO itself goes to
[ladohq/lado](https://github.com/ladohq/lado) the same way; a problem in a kit's own code
can also go to the kit's repository.

## What maintainers do

We answer in the advisory. When a listed kit is the problem, we delist it: a pull request
removes its line from `marketplace.yaml` and its row from the README. CI then rebuilds
`index.json` without it, and LADO stops offering the kit once people run
`lado marketplaces update official`. Kits already installed stay installed: we say in the
advisory what users should do. A kit comes back only through a new pull request, after the
problem is fixed in a new tag.
