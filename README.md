# agent_skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/marzun9620/agent_skills/actions/workflows/ci.yml/badge.svg)](https://github.com/marzun9620/agent_skills/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/marzun9620/agent_skills)](https://github.com/marzun9620/agent_skills/releases)
[![Last commit](https://img.shields.io/github/last-commit/marzun9620/agent_skills)](https://github.com/marzun9620/agent_skills/commits/main)
[![GitHub stars](https://img.shields.io/github/stars/marzun9620/agent_skills?style=social)](https://github.com/marzun9620/agent_skills/stargazers)

> **My personal [Claude Code](https://code.claude.com) skills, kept in one place.** 59 skills across 8 categories — TDD, debugging, ADRs, Playwright, Effect-TS reference, plan stress-testing, and more.

You're welcome to use any of them, copy individual skills into your own projects, or open a PR to add yours. These are what I actually use day-to-day — not a curated commercial product. Your mileage may vary.

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

You can also invoke any skill directly with `/<category>:<skill>` — e.g. `/dev-process:diagnose`. See [Anthropic's docs](https://code.claude.com/docs/en/skills) for the full mental model.

## Use them

Pick whichever way works for you.

### A — Install everything as Claude Code plugins (easiest)

Inside any Claude Code session:

```text
/plugin marketplace add marzun9620/agent_skills
/plugin install <category>@marzun9620-skills
```

### B — Cherry-pick what you want

If you only need a couple of skills, install just those:

```text
/plugin install planning@marzun9620-skills      # brainstorming, grilling, plans → issues
/plugin install dev-process@marzun9620-skills   # ADR, diagnosis, architecture review
/plugin install testing@marzun9620-skills       # TDD + Playwright
/plugin install communication@marzun9620-skills # output-style toggles
```

Add `effect-ts` if you write TypeScript with [Effect](https://effect.website), or `design` if you do FSD frontends or DDD backends.

### C — Copy a single skill into your project

If you just want one skill (e.g. for one repo), grab the folder directly. No install, no plugin system:

```bash
curl -L https://github.com/marzun9620/agent_skills/raw/main/<category>/skills/<skill-name>/SKILL.md \
  -o .claude/skills/<skill-name>/SKILL.md
```

Or `git clone` the whole repo and copy whatever you want.

### D — Clone and use as your own setup

If you want to maintain this as your personal skills config (and edit/add freely):

```bash
git clone https://github.com/marzun9620/agent_skills.git ~/agent_skills
cd ~/agent_skills
./install.sh         # symlinks every skill into ~/.claude/skills/
```

## What's in here

| Category | Skills | What's inside |
|---|---:|---|
| [`effect-ts`](effect-ts/) | 23 | Schema, runtime, error management, streams, testing, and every other corner of [Effect-TS](https://effect.website). |
| [`planning`](planning/) | 6 | brainstorming, grill-me, grill-with-docs, to-issues, to-prd, triage. |
| [`testing`](testing/) | 4 | TDD red-green-refactor + Playwright (CLI, test runner, project conventions). |
| [`dev-process`](dev-process/) | 3 | adr-drafter, diagnose, improve-codebase-architecture. |
| [`meta`](meta/) | 3 | write-a-skill, find-skills, setup-matt-pocock-skills. |
| [`design`](design/) | 2 | domain-design (DDD with Effect Schema), frontend-design (FSD). |
| [`communication`](communication/) | 2 | caveman (token compression), zoom-out (perspective shift). |
| [`codex-effect-workflows`](workflow/) | 16 | **[NICHE]** Codex CLI workflows for layered Effect-TS + Drizzle + Hono backends. Bodies are mostly Japanese. |

Click any category to see its README + the per-skill descriptions inside.

## How skills work

Claude Code reads `SKILL.md` files containing YAML frontmatter (`description`, `name`) plus markdown instructions. When you describe a task, Claude matches it against the `description` field of every loaded skill — when there's a hit, that skill's body is loaded into the prompt for the rest of the session.

Three concrete consequences:

- You can invoke any skill directly by name: `/effect-ts:schema`, `/dev-process:diagnose`. The category is the namespace.
- You can also just describe the task and Claude picks the right skill: "help me write tests for this" → `tdd` activates.
- Skill bodies stay loaded across turns, so they're a recurring token cost. Keep yours concise. See [Anthropic's docs](https://code.claude.com/docs/en/skills) for the full mental model.

## Contributing

Open a PR — happy to take new skills, fixes, or sharper descriptions. The bar is low: if it's useful to more than one project and isn't a thin wrapper around a paid SaaS, it probably fits.

```bash
git clone https://github.com/marzun9620/agent_skills.git
cp -R _template <category>/skills/my-new-skill
$EDITOR <category>/skills/my-new-skill/SKILL.md
./install.sh my-new-skill                # test locally
```

[CONTRIBUTING.md](CONTRIBUTING.md) has the structural conventions (frontmatter fields, file size, language policy). If you're not sure whether a skill fits, open an issue first — happy to discuss before you write it.

## Layout

```
agent_skills/
├── README.md
├── LICENSE
├── NOTICE.md                          ← upstream author attribution
├── CONTRIBUTING.md
├── CHANGELOG.md
├── install.sh                         ← clone-and-symlink installer
├── _template/                         ← starter SKILL.md
├── _helpers/effect-ts-references/     ← shared reference material
├── .claude-plugin/marketplace.json    ← catalog so /plugin install works
│
├── effect-ts/        .claude-plugin/plugin.json + skills/* + README.md
├── workflow/
├── testing/
├── design/
├── planning/
├── dev-process/
├── meta/
└── communication/
```

Each category folder is self-contained. The `.claude-plugin/marketplace.json` at the root makes `/plugin install` work — it's an implementation detail; you don't need to understand it to use or contribute.

## Troubleshooting

**Skill doesn't show up after `/plugin install`.** Run `/plugin marketplace update` to refresh the catalog, then try the install again.

**A skill isn't being auto-invoked when you'd expect.** Sharpen its `description:` field with trigger phrases — put what you'd actually type first. Anthropic truncates descriptions at 1,536 chars under context pressure (drops from the end).

**Too many skills loaded, descriptions getting cut off.** Run `/doctor` — it reports skill-listing budget overflow. Uninstall categories you don't use, or set individual skills to `"name-only"` in `~/.claude/settings.json` under `skillOverrides`.

**`install.sh` reports a conflict.** Something in `~/.claude/skills/` already uses that name. The script never overwrites — `rm` the existing entry first, or use the `/plugin install` path (skills get namespaced under their category, so no conflicts).

## Attribution

This repo is a curated collection. Most of the skills in it were authored by other people, and I'm just packaging them for easier installation:

- **`effect-ts` plugin (23 skills) + `_helpers/`** — by [**Andrue Anderson**](https://github.com/andrueandersoncs/claude-skill-effect-ts) (MIT)
- **14 skills across `planning`, `dev-process`, `meta`, `testing`, `communication`** — by [**Matt Pocock**](https://github.com/mattpocock/skills) (MIT)
- **`workflow-*` plugin (16 skills)** — original to this repo

See [`NOTICE.md`](NOTICE.md) for the full per-skill attribution table and verbatim upstream licenses. If you find a misattribution, please open an issue.

## License

[MIT](LICENSE) for the maintainer's contributions; upstream MIT licenses for third-party skills (see [`NOTICE.md`](NOTICE.md)). Use them, fork them, ship them with your tools — but preserve the original copyright notices.
