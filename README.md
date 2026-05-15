# agent_skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Latest release](https://img.shields.io/github/v/release/marzun9620/agent_skills)](https://github.com/marzun9620/agent_skills/releases)
[![Last commit](https://img.shields.io/github/last-commit/marzun9620/agent_skills)](https://github.com/marzun9620/agent_skills/commits/main)
[![GitHub stars](https://img.shields.io/github/stars/marzun9620/agent_skills?style=social)](https://github.com/marzun9620/agent_skills/stargazers)

> **A plugin marketplace for [Claude Code](https://code.claude.com).** 59 curated skills covering TDD, debugging, ADR drafting, Playwright patterns, Effect-TS reference, plan stress-testing, and more. Install in one line:

```text
/plugin marketplace add marzun9620/agent_skills
```

Then `/plugin install <plugin>@marzun9620-skills` for any of the 8 plugins below. Claude Code auto-loads each skill when its trigger phrases match what you're asking — no manual invocation needed.

<!-- Demo GIF goes here once recorded — see docs/RECORDING_DEMO.md -->
<!-- ![demo](docs/demo.gif) -->

## What a skill actually does

Skills are markdown files that Claude reads on-demand. You don't invoke them by name; you describe a task and Claude picks the right one based on its `description:` field:

```text
You: "Help me write tests for this auth flow."
→ The tdd skill loads, guides you through red-green-refactor TDD.

You: "I'm torn between Postgres and DynamoDB for our event store."
→ The adr-drafter skill loads, walks you through the trade-offs and writes an ADR.

You: "What changed in this branch? Is anything risky?"
→ Skills from dev-process load with diff context inlined.
```

You can also invoke a skill directly with `/<plugin>:<skill>` if you want — e.g. `/dev-process:diagnose`. See [the Anthropic docs](https://code.claude.com/docs/en/skills) for the full mental model.

## Install

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

## Attribution

This repo is a curated collection. Most of the skills in it were authored by other people, and I'm just packaging them for easier installation:

- **`effect-ts` plugin (23 skills) + `_helpers/`** — by [**Andrue Anderson**](https://github.com/andrueandersoncs/claude-skill-effect-ts) (MIT)
- **14 skills across `planning`, `dev-process`, `meta`, `testing`, `communication`** — by [**Matt Pocock**](https://github.com/mattpocock/skills) (MIT)
- **`workflow-*` plugin (16 skills)** — original to this repo

See [`NOTICE.md`](NOTICE.md) for the full per-skill attribution table and verbatim upstream licenses. If you find a misattribution, please open an issue.

## License

[MIT](LICENSE) for the maintainer's contributions; upstream MIT licenses for third-party skills (see [`NOTICE.md`](NOTICE.md)). Use them, fork them, ship them with your tools — but preserve the original copyright notices.
