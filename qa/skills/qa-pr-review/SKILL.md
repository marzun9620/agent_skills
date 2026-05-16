---
name: qa-pr-review
description: Reviews a code PR from a QA lens — testability, test coverage adequacy, regression risk, observability (logs/metrics/alerts), edge cases the PR misses, data migration / backwards-compat concerns, and rollback plan. Distinct from a dev code review (which focuses on correctness / style). Use when the user says "QA review this PR", "review for testability", "regression risk review", "testability review", "QA sign-off on", or asks "what would a QA think of this PR".
---

# QA PR Review

Review a pull request through the lens of *"if this ships, what could go wrong, and could we catch it?"* — not whether the code is well-written.

## Process

### 1. Get the PR context

Accept any of:
- A PR URL (use `gh pr view <n>` and `gh pr diff <n>`)
- A diff pasted in chat
- A local branch (use `git diff main...HEAD`)

If a PR URL was given but `gh` access is limited, request the diff or summary explicitly.

### 2. Read three things in this order

1. **The PR description** — what does the author say this changes? If empty or one-line, that's the first review comment.
2. **The diff** — what actually changed?
3. **The tests in the diff** — what coverage did the author add or update?

If 2 and 3 don't match (large code change with no test changes, or test-only PR claiming to be a feature), call that out immediately.

### 3. Apply this checklist

#### Testability
- [ ] Can a QA write a test case against this change without reading the code? (If not — the change has unclear acceptance criteria.)
- [ ] Are there public seams (env vars, feature flags, API params) a test can use to exercise edge paths?
- [ ] Are there hidden side effects (background jobs, webhooks, async writes) the test would need to wait for?

#### Test coverage
- [ ] **Unit**: new logic has unit tests
- [ ] **Integration**: API contracts touched have integration tests
- [ ] **E2E**: user-facing flows have at least a happy-path E2E
- [ ] **Negative tests**: error paths are tested, not just success
- [ ] **Boundary**: numeric / length / quantity changes have boundary tests
- [ ] **Regression**: any bug being fixed has a regression test that fails without the fix

If coverage is thin, list *which specific test cases are missing* — not a generic "needs more tests."

#### Regression risk
Score: **Low / Medium / High** with reasoning.

Look for:
- Changes to **shared utilities** used by many call sites (high — verify all call sites still work)
- Changes to **data shapes** (high — old code may read the new shape and break)
- Changes to **default values** (medium — silently changes behaviour for unset callers)
- Changes to **feature flags** that affect production users immediately on merge (high — needs cohort plan)
- Changes to **migrations** (high — also needs rollback plan)
- Changes to **interfaces** or types that other PRs may have copied (medium)

#### Observability
- [ ] Does the change add logs at the new failure modes?
- [ ] Does it expose a metric the team can alert on?
- [ ] Are existing dashboards / alerts still valid after this change?
- [ ] If it's a perf-sensitive path, does it emit timing info?

#### Edge cases the PR likely misses
Mentally run through the standard list:
- Empty input (zero items, null, empty string)
- Maximum input (limit + 1, very large lists, very long strings)
- Concurrent access (two requests on the same entity)
- Stale data (cached value vs fresh write)
- Permission denied / unauthenticated path
- Network failure mid-operation
- Idempotency (what happens if the operation runs twice?)

List the cases that *seem like the dev didn't think about them*, not all of them.

#### Data migrations / backwards compat
- [ ] Is there a migration? Does it have a rollback?
- [ ] Is the new code backwards-compatible with rows written by the old code (and vice versa, during rolling deploy)?
- [ ] If a field is being renamed/removed, is there a deprecation window?

#### Rollout / rollback
- [ ] Is there a feature flag, or is this on for all users immediately?
- [ ] If shipping silently broken, can we roll back without data loss?
- [ ] If gated, what's the cohort plan and the success metric?

### 4. Produce the review in this format

```md
## QA review: <PR title>

**Verdict**: Approve | Request changes | Block + brief reason

**Test coverage**: <Adequate | Thin | Missing>
**Regression risk**: <Low | Medium | High> — <one sentence why>

### What's good
- <2–3 bullets noting what the author already did well — testability seams added, good unit test coverage, etc.>

### Required before merge
1. <Specific, actionable. Say which test to add, which code to instrument, etc.>
2. <…>

### Should consider (not blocking)
- <Optional improvements — could file as follow-up tickets>

### Edge cases I'd want covered
- <Concrete missing test case 1: "what happens when input X is empty?">
- <Concrete missing test case 2: "two concurrent requests on the same entity">

### Rollout plan I'd want to see
- <Specific to this PR. E.g. "Behind a feature flag, 5% cohort for 48h, watch dashboard X.">

### Open questions for the author
- <If anything is genuinely unclear, ask. Don't speculate in the review itself.>
```

### 5. Calibrate the verdict

- **Approve**: tests cover the happy path + main error paths, regression risk is Low/Medium with clear mitigations, no migration or migration has rollback.
- **Request changes**: missing tests for a specific case, missing logs for a specific failure mode, missing rollback for a risky migration. Always say what specifically needs to change.
- **Block**: data corruption risk, security regression, breaking change without deprecation. Use sparingly; explain what would unblock.

Never block without saying how to unblock.

## Anti-patterns to avoid

- Reviewing code style / naming — that's a dev review, not a QA review. Stay in your lane.
- "Add more tests" without saying which tests — useless feedback.
- Speculating about implementation ("I think this might race") without testing or pointing to evidence.
- Marking high-risk PRs as Approve because they're nicely written. Pretty code ships bugs too.
- Approving without checking the test diff. The tests are the QA review surface.
