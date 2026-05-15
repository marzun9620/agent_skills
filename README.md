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

```
agent_skills/
├── README.md
├── install.sh                # symlinks every skill dir into ~/.claude/skills/
├── _template/                # copy this when starting a new skill
│   └── SKILL.md
└── <skill-name>/
    ├── SKILL.md              # required: frontmatter + instructions
    ├── reference.md          # optional supporting docs
    └── scripts/              # optional bundled scripts
```

Directories starting with `_` (e.g. `_template/`, `effect-ts-skills/_agents/`) are excluded from installation — useful for templates, shared helpers, or reference material that isn't itself a registerable skill.

## Add a new skill

```bash
cp -R _template my-new-skill
$EDITOR my-new-skill/SKILL.md
./install.sh my-new-skill
```

Then in any project, type `/my-new-skill` or just describe the task — Claude will auto-invoke based on the `description` field.

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
