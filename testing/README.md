# Testing skills

Test authoring and Playwright tooling. The Playwright trio splits responsibilities: `playwright-test` covers test-runner best practices, `playwright-cli` covers terminal commands and codegen, `playwright-patterns` covers project conventions (POM, selectors, flow specs).

| Skill | Description |
|---|---|
| [`playwright-cli`](skills/playwright-cli/) | Use when running Playwright via terminal CLI — `npx playwright test` (test runner), `codegen` (interactive recording), `screenshot` / `pdf` (one-off captures), and CI sharding. NOT for agent-driven real-time browser control (use `claude-in-chrome` MCP tools for that). |
| [`playwright-e2e`](skills/playwright-e2e/) | Project-specific Playwright E2E authoring rules for healthian-wood (RM + DH + Firebase emulator). Effect-TS embedded architecture (§21 boundary rule), AI/MCP three-layer integration (§22). Use when adding, reviewing, or debugging tests under apps/reservation-manager/e2e/. Defer to docs/research/playwright-e2e.md for full depth. |
| [`playwright-patterns`](skills/playwright-patterns/) | Patterns for writing Playwright E2E tests — POM structure, selector hierarchy, flow specs, waits, role contexts, dialog handling. Use when authoring or reviewing anything under /e2e. |
| [`playwright-test`](skills/playwright-test/) | Playwright Test (E2E) best practices and reference. Covers test authoring, avoiding fixed waits, network triggers, drag-and-drop, and shard/retry configuration in GitHub Actions. Use when writing, reviewing, or setting up CI for Playwright tests. |
| [`tdd`](skills/tdd/) | Test-driven development with red-green-refactor loop. Use when user wants to build features or fix bugs using TDD, mentions "red-green-refactor", wants integration tests, or asks for test-first development. |

## Install just this plugin

```
/plugin marketplace add marzun9620/agent_skills
/plugin install testing@marzun9620-skills
```

_See the [repo README](../README.md) for the full picture._
