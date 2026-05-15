# Testing skills

Test authoring and Playwright tooling. The Playwright trio splits responsibilities: `playwright-test` covers test-runner best practices, `playwright-cli` covers terminal commands and codegen, `playwright-patterns` covers project conventions (POM, selectors, flow specs).

| Skill | Description |
|---|---|
| [`playwright-cli`](playwright-cli/) | Use when running Playwright via terminal CLI — `npx playwright test` (test runner), `codegen` (interactive recording), `screenshot` / `pdf` (one-off captures), and CI sharding. NOT for agent-driven real-time browser control (use `claude-in-chrome` MCP tools for that). |
| [`playwright-e2e`](playwright-e2e/) | Project-specific Playwright E2E authoring rules for healthian-wood (RM + DH + Firebase emulator). Effect-TS embedded architecture (§21 boundary rule), AI/MCP three-layer integration (§22). Use when adding, reviewing, or debugging tests under apps/reservation-manager/e2e/. Defer to docs/research/playwright-e2e.md for full depth. |
| [`playwright-patterns`](playwright-patterns/) | Patterns for writing Playwright E2E tests in this repo — POM structure, selector hierarchy, flow specs, waits, role contexts, dialog handling. Use when authoring or reviewing anything under /e2e. |
| [`playwright-test`](playwright-test/) | Playwright Test (E2E) のベストプラクティスとリファレンス。テストの書き方、固定 wait 回避、ネットワークトリガー、DnD、GitHub Actions での shard/retry 設定など。Playwright テストを書く・レビュー・CI 設定するときに使用。 |
| [`tdd`](tdd/) | Test-driven development with red-green-refactor loop. Use when user wants to build features or fix bugs using TDD, mentions "red-green-refactor", wants integration tests, or asks for test-first development. |

_See the [repo README](../README.md) for install instructions._
