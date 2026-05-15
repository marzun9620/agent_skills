# agent_skills

Personal Claude Code skills, source-controlled here and symlinked into `~/.claude/skills/` so they're available across every project.

## Quick start (consume this repo)

### Install everything

```bash
git clone <repo-url> ~/agent_skills      # or wherever you want it
cd ~/agent_skills
./install.sh                              # symlinks every skill into ~/.claude/skills/
```

Open Claude Code in any project; all skills are immediately discoverable via `/<skill-name>` or natural-language matching against each skill's `description`.

### Install only specific skills

```bash
./install.sh --list                       # see what's available
./install.sh tdd diagnose adr-drafter     # symlink just these three
```

Re-running with different names later is additive — already-linked skills are left alone, new ones get linked.

### Grab a single skill *without* cloning the whole repo

If you only want one skill (e.g. for one project), copy the directory into the project's `.claude/skills/`:

```bash
cd /path/to/some-project
mkdir -p .claude/skills
# clone the repo somewhere temporary, then:
cp -R /tmp/agent_skills/effect-ts-schema .claude/skills/
# commit it into the project repo so your teammates get it too
git add .claude/skills/effect-ts-schema && git commit -m "Add effect-ts-schema skill"
```

Project-scope skills only apply inside that repo. Personal-scope (via `install.sh`) applies everywhere.

### Uninstall

Personal-scope installs are just symlinks under `~/.claude/skills/`. Remove with:

```bash
rm ~/.claude/skills/<skill-name>          # one skill
# or all of them:
./install.sh --list | xargs -I{} rm -f ~/.claude/skills/{}
```

## How it works

Claude Code auto-discovers skills from `~/.claude/skills/<skill-name>/SKILL.md` ([docs](https://code.claude.com/docs/en/skills)). This repo is the **source of truth**; `install.sh` creates a symlink in `~/.claude/skills/` for each top-level directory here, so editing a `SKILL.md` here updates the skill in every project — Claude Code watches the directory for live changes and picks them up within the current session.

## Layout

Skills are grouped into category folders for browsing. The folder structure is **purely organizational** — `install.sh` walks the tree recursively and discovers skills by their `SKILL.md`. The symlinks it creates in `~/.claude/skills/` stay flat (one per skill), and you still invoke each skill the same way (`/skill-name` or natural-language match).

```
agent_skills/
├── README.md
├── install.sh                       # recursive symlink installer
├── _template/                       # copy this when starting a new skill (excluded from install)
├── _helpers/                        # shared reference material (excluded from install)
│   └── effect-ts-references/        # _agents, _commands, _references bundles
│
├── effect-ts/                       # Effect-TS skills — see effect-ts/README.md
├── workflow/                        # Clean-architecture / Codex workflows — see workflow/README.md
├── testing/                         # Playwright + TDD — see testing/README.md
├── design/                          # FSD + DDD design skills — see design/README.md
├── planning/                        # PRD/issue creation, ideation, grilling — see planning/README.md
├── dev-process/                     # ADR, diagnosis, architecture — see dev-process/README.md
├── meta/                            # skill-authoring + discovery — see meta/README.md
└── communication/                   # output-style skills — see communication/README.md
```

Each category has its own README with a table of every skill in it and what it does:

- [`effect-ts/README.md`](effect-ts/README.md) — 23 Effect-TS reference skills
- [`workflow/README.md`](workflow/README.md) — 16 clean-architecture & Codex-workflow skills
- [`testing/README.md`](testing/README.md) — Playwright trio + TDD
- [`design/README.md`](design/README.md) — domain-design, frontend-design
- [`planning/README.md`](planning/README.md) — ideation, grilling, plan-to-issues/PRD
- [`dev-process/README.md`](dev-process/README.md) — ADR drafting, diagnosis, architecture review
- [`meta/README.md`](meta/README.md) — write-a-skill, find-skills
- [`communication/README.md`](communication/README.md) — caveman, zoom-out

Each skill is a directory inside its category with `SKILL.md` (required) plus optional supporting files:

```
<category>/<skill-name>/
├── SKILL.md           # required: frontmatter + instructions
├── reference.md       # optional supporting docs
└── scripts/           # optional bundled scripts
```

Directories starting with `_` (e.g. `_template/`, `_helpers/`) are excluded from installation. Use them for templates, shared reference material, or anything that isn't itself a registerable skill. The same rule applies at any depth in the tree.

## Add a new skill

Place it inside the most relevant category folder:

```bash
cp -R _template <category>/my-new-skill   # e.g. design/my-new-skill
$EDITOR <category>/my-new-skill/SKILL.md
./install.sh my-new-skill
```

The category folder doesn't affect anything functionally — pick whatever makes the skill easiest to find. If nothing fits, create a new category folder (or drop it at the repo root). Then in any project, type `/my-new-skill` or just describe the task — Claude will auto-invoke based on the `description` field.

## Rules for `SKILL.md`

- Frontmatter must include `description`. Put the key use case **first** — it's truncated at 1,536 chars and used for trigger matching.
- Keep the body under ~500 lines / 1,500–2,000 words. Skill bodies stay in context for the rest of the session, so every line is a recurring token cost.
- Move long reference material into sibling files (`reference.md`, `examples.md`, etc.) and link to them from `SKILL.md` — they only load when Claude reads them.
- Bundled scripts run via bash; their source never enters context, only their output.

## Useful frontmatter fields

| Field | What it does |
|---|---|
| `description` | When Claude should invoke the skill (recommended) |
| `disable-model-invocation: true` | Only you can run it via `/name` — Claude won't trigger it automatically. Use for actions with side effects (deploy, commit, send-slack). |
| `user-invocable: false` | Hide from `/` menu; Claude can still load it as background context |
| `allowed-tools` | Pre-approve tools while the skill is active (e.g. `Bash(git *) Read`) |
| `context: fork` + `agent: Explore` | Run the skill in a subagent — keeps main context clean for research-heavy skills |
| `paths` | Only auto-load when working in files matching globs |

Full reference: <https://code.claude.com/docs/en/skills#frontmatter-reference>

## Troubleshooting

**A skill isn't showing up.** Check `ls -la ~/.claude/skills/<name>` — if it's missing, re-run `./install.sh <name>`. If the symlink exists but points somewhere unexpected, `readlink` it to see what's pointing where.

**`install.sh` reports a conflict.** Something in `~/.claude/skills/` is already using that name (likely a symlink to another source, e.g. `~/.agents/skills/`, or a real directory). The script never overwrites — to switch sources, `rm` the existing entry first, then re-run install.

**Claude isn't auto-invoking my skill.** Sharpen the `description` field — put trigger phrases (the things you'd type) up front. Skill descriptions get truncated under context pressure, and the truncation drops from the end.

**Too many skills, descriptions getting cut off.** Run `/doctor` in Claude Code — it reports if the skill-listing budget is overflowing. Hide rarely-used skills via `skillOverrides` in `~/.claude/settings.json` (`"name": "name-only"` or `"off"`).
