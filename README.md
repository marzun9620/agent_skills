# agent_skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/marzun9620/agent_skills)](https://github.com/marzun9620/agent_skills/commits/main)
[![GitHub stars](https://img.shields.io/github/stars/marzun9620/agent_skills?style=social)](https://github.com/marzun9620/agent_skills/stargazers)

> **59 ready-to-use [Claude Code](https://code.claude.com) skills**, grouped into 8 installable plugins. TDD, diagnosis, ADR drafting, Playwright patterns, Effect-TS reference, and more.

Each skill is a `SKILL.md` that Claude Code auto-loads when its trigger phrases match what you're asking — no manual invocation required. Pick a plugin, install it once, and the skills are available in every project.

## Install

The fastest path: **inside any Claude Code session**, add this marketplace and install whichever plugin you want.

```text
/plugin marketplace add marzun9620/agent_skills
/plugin install <plugin-name>@marzun9620-skills
```

### Recommended starter pack

If you're new to skills, install these four — they're broadly useful regardless of your stack:

```text
/plugin install planning@marzun9620-skills      # brainstorming, grilling, plans → issues
/plugin install dev-process@marzun9620-skills   # ADR, diagnosis, architecture review
/plugin install testing@marzun9620-skills       # TDD + Playwright
/plugin install communication@marzun9620-skills # output-style toggles (caveman, zoom-out)
```

Then add `effect-ts` if you write TypeScript with [Effect](https://effect.website), or `design` if you do FSD frontends or DDD backends.

### Full plugin list

| Plugin | Skills | What's inside |
|---|---:|---|
| [`effect-ts`](effect-ts/) | 23 | Schema, runtime, error management, streams, testing, and every other corner of [Effect-TS](https://effect.website). |
| [`planning`](planning/) | 6 | brainstorming, grill-me, grill-with-docs, to-issues, to-prd, triage. |
| [`testing`](testing/) | 4 | TDD red-green-refactor + Playwright (CLI, test runner, project conventions). |
| [`dev-process`](dev-process/) | 3 | adr-drafter, diagnose, improve-codebase-architecture. |
| [`meta`](meta/) | 3 | write-a-skill, find-skills, setup-matt-pocock-skills. |
| [`design`](design/) | 2 | domain-design (DDD with Effect Schema), frontend-design (FSD). |
| [`communication`](communication/) | 2 | caveman (token compression), zoom-out (perspective shift). |
| [`codex-effect-workflows`](workflow/) | 16 | **[NICHE]** Codex CLI workflows for layered Effect-TS + Drizzle + Hono backends. Bodies are mostly Japanese. |

### Alternative install: clone & symlink

If you'd rather have the skills as personal-scope rather than plugins (so they invoke without a plugin namespace), clone and run `install.sh`:

```bash
git clone https://github.com/marzun9620/agent_skills.git ~/agent_skills
cd ~/agent_skills
./install.sh                                 # install all 59
./install.sh --list                          # list available
./install.sh tdd diagnose adr-drafter        # install just specific ones
```

The script symlinks each skill into `~/.claude/skills/<skill-name>/`. It auto-repairs stale symlinks on re-run, never overwrites existing entries from other sources (like `~/.agents/skills/`), and works on macOS + Linux. Windows users: use WSL or the plugin marketplace path.

## How skills work

Claude Code reads `SKILL.md` files containing YAML frontmatter (`description`, `name`) plus markdown instructions. When you describe a task, Claude matches it against the `description` field of every loaded skill — when there's a hit, that skill's body is loaded into the prompt for the rest of the session.

Three concrete consequences:

- Skill names you can invoke directly: `/effect-ts:schema`, `/dev-process:diagnose`, etc. The plugin name is the namespace.
- You can also just describe the task and Claude picks the right skill: "help me write tests for this" → `tdd` activates.
- Skill bodies stay loaded across turns, so they're a recurring token cost — keep them concise. See [Anthropic's docs](https://code.claude.com/docs/en/skills) for the full mental model.

## Add your own skill

```bash
cp -R _template <category>/skills/my-new-skill
$EDITOR <category>/skills/my-new-skill/SKILL.md
./install.sh my-new-skill                    # if you cloned the repo
```

If your skill is broadly useful, PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for the bar and the conventions. If it's project-specific, fork the repo or keep it in your own personal `.claude/skills/`.

## Layout

```
agent_skills/
├── .claude-plugin/marketplace.json     ← marketplace catalog
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── install.sh                          ← clone-and-symlink installer
├── _template/                          ← starter SKILL.md
├── _helpers/effect-ts-references/      ← shared reference material
│
├── effect-ts/        .claude-plugin/plugin.json + skills/* + README.md
├── workflow/         (codex-effect-workflows plugin)
├── testing/
├── design/
├── planning/
├── dev-process/
├── meta/
└── communication/
```

Each category folder is a self-contained plugin. The marketplace at the root lists all 8 with versions, descriptions, and source paths.

## Troubleshooting

**Skill doesn't show up after `/plugin install`.** Run `/plugin marketplace update` to refresh the catalog, then try the install again.

**A skill isn't being auto-invoked when you'd expect.** Sharpen its `description:` field with trigger phrases — put what you'd actually type first. Anthropic truncates descriptions at 1,536 chars under context pressure (drops from the end).

**Too many skills, descriptions getting cut off.** Run `/doctor` — it reports the skill-listing budget overflow. Disable plugins you don't use, or set individual skills to `"name-only"` in `~/.claude/settings.json` under `skillOverrides`.

**`install.sh` reports a conflict.** Something in `~/.claude/skills/` already uses that name. The script never overwrites — `rm` the existing entry first, or use the plugin marketplace path instead (plugin skills are namespaced, no conflicts).

## License

[MIT](LICENSE). Use them, fork them, ship them with your tools.
