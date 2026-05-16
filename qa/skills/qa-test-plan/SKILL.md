---
name: qa-test-plan
description: Authors a structured test plan from a PRD, feature spec, or change description. Output covers objectives, scope (in/out), test types needed (unit, integration, E2E, exploratory, performance, security, accessibility), environments, entry/exit criteria, risks, and effort estimate. Use when the user asks to "write a test plan", "QA plan for", "verification plan", "what should we test in", or hands over a PRD/spec and asks how to verify it.
---

# QA Test Plan

Produce a test plan that another engineer can execute without follow-up questions.

## Process

### 1. Read the input

Accept any of:
- A PRD link / file path
- A pasted spec, ticket description, or feature summary
- A `git diff` or PR description
- A verbal description of what shipped or is about to ship

If only a one-line description was provided, ask one targeted question before producing the plan (e.g. *"Is this a brand-new feature, a behaviour change, or a bug fix?"*).

### 2. Produce the plan in this format

```md
# Test Plan: <feature or change name>

## Objectives
<2–4 bullets. What confidence does this plan give us? Why are we testing?>

## Scope
**In scope:**
- <user-facing flows under test>
- <integrations touched>
- <data states / migrations to verify>

**Out of scope:**
- <explicitly excluded, with one-line reason each>

## Test types
| Type | Owner | Coverage target | Notes |
|---|---|---|---|
| Unit | dev | new logic in <module> | run on every PR |
| Integration | dev/QA | API contracts touched | run on PR + nightly |
| E2E (Playwright) | QA | happy path + 2 error paths | run on PR for affected suites |
| Exploratory | QA | 1 charter, 90 min | post-merge, pre-release |
| Performance | QA | <benchmark or load profile> | only if PR affects hot path |
| Security | QA / sec | auth / input validation | only if PR touches authn/authz, file upload, user-supplied SQL |
| Accessibility | QA / design | new UI components | only if PR adds UI |

Drop rows that don't apply. Add rows for stack-specific needs (chaos, contract, visual regression, etc.).

## Environments
- **Local**: <how to run>
- **Staging**: <URL, data state, auth>
- **Prod-like**: <if separate>

## Entry criteria
- [ ] All required tests defined and reviewed
- [ ] Test data prepared in staging
- [ ] Feature flag flipped to test cohort (if applicable)
- [ ] Build deployed to staging

## Exit criteria
- [ ] All P0/P1 test cases pass
- [ ] No new bugs of severity ≥ Medium open against this feature
- [ ] Performance within <X%> of baseline
- [ ] Sign-off from <PM / engineering lead>

## Risks & open questions
- <risk 1> — mitigation: <…>
- <open question 1> — needs answer from <person/team> before <when>

## Effort estimate
| Phase | Person-hours |
|---|---|
| Test case design | … |
| Test data setup | … |
| Execution (manual + automation) | … |
| Bug triage + retest | … |
| **Total** | **…** |
```

### 3. Anchor every section in the actual change

Don't produce a generic boilerplate. If the PRD says "add CSV export," every row in the test-types table should be specifically about CSV export — what error states (empty data, 1M rows, special characters), what environments (which browsers download CSV correctly), what regression risks (existing JSON export shouldn't break).

### 4. Hand off

Save to the user's plan location (default `docs/test-plans/<feature>.md` if unspecified). Mention which test cases need to be expanded next via `qa-test-cases`, and whether an exploratory session would add value via `qa-exploratory-charter`.

## Edge cases

- **Bug fix, not new feature**: scope is the regression + the original bug. Risk section calls out adjacent regressions.
- **Refactor, no behaviour change**: focus on regression coverage + characterisation tests; performance benchmark before/after.
- **Feature flag rollout**: include a per-cohort exit criterion ("X% of users for Y days with no severity-Medium issues").
- **Migration / data backfill**: add a "data correctness" section with sample queries, expected row counts, and rollback rehearsal.

## Anti-patterns to avoid

- Generic "all standard test types apply" — pick the ones that matter for THIS change.
- Empty "out of scope" — every plan has things it's not testing; naming them prevents scope creep later.
- Exit criteria that can never be verified ("zero bugs ever"). Use measurable conditions.
- No risks section. Every change has risks; if you can't think of any, ask another engineer.
