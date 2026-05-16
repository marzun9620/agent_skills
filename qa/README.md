# QA skills

QA-persona skills covering the day-to-day output of a quality engineer: writing test plans from PRDs, drafting actionable bug reports, converting acceptance criteria into executable test cases, planning exploratory testing sessions (SBTM), and reviewing PRs from a testability and regression-risk lens.

These complement (not duplicate) the existing `testing/` plugin (TDD + Playwright tooling) and `pm-execution:test-scenarios` (which generates test scenarios from user stories at the PM level).

| Skill | Description |
|---|---|
| [`qa-bug-report`](skills/qa-bug-report/) | Drafts a high-quality bug report that a developer can act on without follow-up. Output includes a specific one-line summary, numbered repro steps, expected vs actual, environment fingerprint, severity with rationale, frequency, attachments to gather, and suggested fix area. Use when the user says "write a bug report", "file a bug", "report this defect", "draft a QA ticket", or describes a defect they want documented. |
| [`qa-exploratory-charter`](skills/qa-exploratory-charter/) | Writes a Session-Based Test Management (SBTM) charter for an exploratory testing session — mission, areas, tactics (heuristics + attacks), time-box, oracle, setup data, and PROOF debrief template. Use when the user says "exploratory testing", "exploratory charter", "session-based testing", "SBTM", "exploratory test session for", or wants to design a focused exploration session for a feature. |
| [`qa-pr-review`](skills/qa-pr-review/) | Reviews a code PR from a QA lens — testability, test coverage adequacy, regression risk, observability (logs/metrics/alerts), edge cases the PR misses, data migration / backwards-compat concerns, and rollback plan. Distinct from a dev code review (which focuses on correctness / style). Use when the user says "QA review this PR", "review for testability", "regression risk review", "testability review", "QA sign-off on", or asks "what would a QA think of this PR". |
| [`qa-test-cases`](skills/qa-test-cases/) | Converts acceptance criteria (Given/When/Then or any-format AC) into a structured set of executable test cases — happy path + boundary + negative + edge. Each test case has ID, preconditions, test data, steps, expected results, and a test-type tag. Use when the user says "write test cases for", "convert AC to test cases", "test cases for this AC", or hands over acceptance criteria and asks how to test them. Complements pm-execution:test-scenarios (which works from user stories) by focusing on AC granularity. |
| [`qa-test-plan`](skills/qa-test-plan/) | Authors a structured test plan from a PRD, feature spec, or change description. Output covers objectives, scope (in/out), test types needed (unit, integration, E2E, exploratory, performance, security, accessibility), environments, entry/exit criteria, risks, and effort estimate. Use when the user asks to "write a test plan", "QA plan for", "verification plan", "what should we test in", or hands over a PRD/spec and asks how to verify it. |

## Install just this plugin

```
/plugin marketplace add marzun9620/agent_skills
/plugin install qa@marzun9620-skills
```

_See the [repo README](../README.md) for the full picture._
