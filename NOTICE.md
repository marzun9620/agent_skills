# NOTICE

This repository redistributes skills authored by people other than the repo maintainer. All upstream sources are MIT-licensed and are reproduced here in compliance with the MIT requirement to preserve copyright notices and license text. This file lists what came from where, and embeds the full text of each upstream license.

> **Maintainer's note**: I (marzun9620) am the curator, not the author, of most of the skills in this repo. The original authors hold copyright in their work. My contributions are the repo structure, the `install.sh` installer, the `.claude-plugin/marketplace.json`, the category READMEs, the `workflow-*` plugin, and any other content explicitly noted as "original" below. Those are covered by the root [`LICENSE`](LICENSE) (MIT, © marzun9620). The third-party content listed below is covered by the licenses in this NOTICE.

---

## Skill origins

### Plugin `effect-ts/` (23 skills) + `_helpers/effect-ts-references/`

**Author:** Andrue Anderson
**Source:** https://github.com/andrueandersoncs/claude-skill-effect-ts
**License:** MIT (see [Andrue Anderson's MIT license](#mit-license--andrue-anderson) below)

Skills:
- `effect-ts-api-docs`, `effect-ts-batching-caching`, `effect-ts-best-practices`, `effect-ts-code-style`, `effect-ts-concurrency`, `effect-ts-configuration`, `effect-ts-data-types`, `effect-ts-effect-ai`, `effect-ts-effect-core`, `effect-ts-error-management`, `effect-ts-observability`, `effect-ts-pattern-matching`, `effect-ts-platform`, `effect-ts-requirements-management`, `effect-ts-resource-management`, `effect-ts-runtime`, `effect-ts-scheduling`, `effect-ts-schema`, `effect-ts-sinks`, `effect-ts-state-management`, `effect-ts-streams`, `effect-ts-testing`, `effect-ts-traits`

Helpers (also from the same source):
- `_helpers/effect-ts-references/_agents/*`, `_commands/*`, `_references/`

The bundled file `_helpers/effect-ts-references/_references/llms-full.txt` is the [Effect-TS](https://effect.website) developer documentation (also MIT-licensed by the Effect-TS authors).

### Various skills from `mattpocock/skills` (14 skills)

**Author:** Matt Pocock
**Source:** https://github.com/mattpocock/skills
**License:** MIT (see [Matt Pocock's MIT license](#mit-license--matt-pocock) below)

These skills are distributed across multiple plugins in this repo for organizational reasons; they all originated from Matt Pocock's `skills` repository:

| Plugin in this repo | Skill | Original location in mattpocock/skills |
|---|---|---|
| `planning` | `brainstorming` | `skills/productivity/brainstorming` (verify) |
| `planning` | `grill-me` | `skills/productivity/grill-me` |
| `planning` | `grill-with-docs` | `skills/engineering/grill-with-docs` |
| `planning` | `to-issues` | `skills/engineering/to-issues` |
| `planning` | `to-prd` | `skills/engineering/to-prd` |
| `planning` | `triage` | `skills/engineering/triage` |
| `dev-process` | `diagnose` | `skills/engineering/diagnose` |
| `dev-process` | `improve-codebase-architecture` | `skills/engineering/improve-codebase-architecture` |
| `meta` | `find-skills` | (from his ecosystem; see [skills.sh](https://skills.sh)) |
| `meta` | `setup-matt-pocock-skills` | `skills/engineering/setup-matt-pocock-skills` |
| `meta` | `write-a-skill` | `skills/productivity/write-a-skill` |
| `testing` | `tdd` | `skills/engineering/tdd` |
| `communication` | `caveman` | `skills/productivity/caveman` |
| `communication` | `zoom-out` | `skills/engineering/zoom-out` |

### Origin unclear (please verify)

The following may be original to this repo, or may have an upstream source I couldn't identify with certainty. **The repo maintainer should confirm and update this section.**

- `dev-process/adr-drafter`
- `testing/playwright-cli`
- `testing/playwright-patterns`
- `testing/playwright-test`
- `design/domain-design`
- `design/frontend-design`

### Original to this repo (© marzun9620, MIT)

- All 16 `workflow-*` skills (under the `codex-effect-workflows` plugin) — written for an internal project and adapted for this repo.
- `meta/skills/prompt-refinement` — refines rough instructions into structured Agent Task Prompts for delegation to other agents.
- `meta/skills/skill-router` — routes any user task to the best-matching installed skill, or scaffolds a new one when none fits.
- `install.sh`, `README.md`, `CONTRIBUTING.md`, all `<category>/README.md` files, the `.claude-plugin/marketplace.json` catalog, and the `.claude-plugin/plugin.json` manifests are repo-maintenance artefacts produced by the maintainer.
- The `_template/SKILL.md` starter file.

---

## MIT License — Andrue Anderson

The following license applies to the `effect-ts/` plugin and `_helpers/effect-ts-references/`:

```
MIT License

Copyright (c) 2026 Andrue Anderson

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Source LICENSE: <https://github.com/andrueandersoncs/claude-skill-effect-ts/blob/main/LICENSE>

---

## MIT License — Matt Pocock

The following license applies to the 14 Matt Pocock skills listed above:

```
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Source LICENSE: <https://github.com/mattpocock/skills/blob/main/LICENSE>

---

## Effect-TS documentation

The file `_helpers/effect-ts-references/_references/llms-full.txt` is the developer-documentation bundle from the [Effect](https://effect.website) project. Effect is MIT-licensed; its license applies to that file.

Source: <https://github.com/Effect-TS/effect>

---

## Reporting attribution errors

If you find a skill in this repo whose source I've misidentified or failed to credit, please open an issue at <https://github.com/marzun9620/agent_skills/issues>. I'll fix it as a priority.
