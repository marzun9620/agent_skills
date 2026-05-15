# Changelog

All notable changes to this repo are documented as [GitHub Releases](https://github.com/marzun9620/agent_skills/releases). This file is a short summary; click through to a release for full details.

## [v1.1.0](https://github.com/marzun9620/agent_skills/releases/tag/v1.1.0) — 2026-05-15

Discovery & framing polish. No skill content changes; functionality identical to v1.0.0.

- Reframed positioning: from *"plugin marketplace for Claude Code"* (sounded commercial) to *"my personal Claude Code skills, kept in one place. Use any, fork, or contribute."* The repo description, README hero, and CONTRIBUTING tone all match.
- README adds a **"Use them"** section with 4 install paths (marketplace, cherry-pick, curl a single SKILL.md, or clone + `install.sh`) — `/plugin install` is now one option of four, not THE option.
- New **"What a skill actually does"** section with 3 concrete examples of the auto-invocation pattern.
- Demo GIF placeholder + `docs/RECORDING_DEMO.md` walkthrough.
- Release-version badge.
- `CHANGELOG.md` (this file).
- `.github/ISSUE_TEMPLATE/` (bug, skill request, attribution correction) + PR template.
- GitHub repo description updated to lead with the value prop.

## [v1.0.0](https://github.com/marzun9620/agent_skills/releases/tag/v1.0.0) — 2026-05-15

First tagged release.

- 59 curated Claude Code skills across 8 plugins (`effect-ts`, `codex-effect-workflows`, `testing`, `design`, `planning`, `dev-process`, `meta`, `communication`)
- Plugin marketplace via `.claude-plugin/marketplace.json` — install with `/plugin marketplace add marzun9620/agent_skills`
- Clone-and-symlink alternative via `install.sh` (macOS + Linux)
- Full attribution to upstream authors: [Andrue Anderson](https://github.com/andrueandersoncs/claude-skill-effect-ts) (effect-ts plugin) and [Matt Pocock](https://github.com/mattpocock/skills) (14 skills across multiple plugins). See [`NOTICE.md`](NOTICE.md) for the per-skill table and upstream license texts.
- MIT licensed (for maintainer's original contributions) with preserved upstream MIT notices.
