---
name: qa-bug-report
description: Drafts a high-quality bug report that a developer can act on without follow-up. Output includes a specific one-line summary, numbered repro steps, expected vs actual, environment fingerprint, severity with rationale, frequency, attachments to gather, and suggested fix area. Use when the user says "write a bug report", "file a bug", "report this defect", "draft a QA ticket", or describes a defect they want documented.
---

# QA Bug Report

Produce a bug report that meets the "good bug report" bar: specific, reproducible, severity-justified, complete enough that a developer can start work without asking questions.

## Process

### 1. Gather the facts

Ask only for what's missing — don't re-ask anything the user already provided.

Required facts:
- **What happened** (one or two sentences in the user's own words)
- **What you expected** (one sentence)
- **Steps you took** (the exact sequence, including data entered)
- **Where** (URL, screen, deeplink, or file path)
- **When** (timestamp if helpful for log correlation)
- **Environment** (browser + version, OS, app build, env name like prod/staging)

Optional but valuable:
- Screenshot / screen recording / log excerpt
- Network request that failed (curl command if reproducible)
- Recent changes (deploy, feature flag flip, data migration)
- Whether it happens for other users / accounts

If the user gave a verbal description, do not invent specifics. Ask for the URL, the browser, the exact text they typed.

### 2. Produce the bug report in this format

```md
# [<severity>] <one-line summary>

**Summary**: <one sentence — what's broken from the user's point of view, not from the code's point of view>

## Steps to reproduce
1. <Specific action — include the data entered>
2. <…>
3. <…>

## Expected behaviour
<One paragraph or bullet list. State what should have happened given the spec.>

## Actual behaviour
<One paragraph or bullet list. State what happens instead. Include exact error messages verbatim.>

## Environment
| | |
|---|---|
| URL | <url where it occurs> |
| Browser | <name + version> |
| OS | <name + version> |
| App build | <commit SHA or version string> |
| Env | <prod / staging / local> |
| Account | <test account email or 'real user XXX'> |
| Timestamp | <ISO datetime, for log lookup> |

## Frequency
<Always / Often (~50%) / Sometimes / Once — and what conditions make it more/less likely>

## Severity: <Critical | High | Medium | Low>
**Rationale**: <why this severity — see severity rubric below>

## Attachments
- [ ] Screenshot of the broken state
- [ ] Browser console output (if frontend)
- [ ] Server log excerpt around the timestamp
- [ ] Network request that returned the error (curl or HAR)

## Suggested area / possible cause
<Optional — only include if you have a reasonable guess. Otherwise omit. Don't speculate wildly; a wrong guess costs the dev time.>

## Workaround
<If a temporary workaround exists, document it. Otherwise: "None known.">
```

### 3. Apply the severity rubric

| Severity | Use when |
|---|---|
| **Critical** | Production down, data loss/corruption, security exposure, payments broken, full outage for a user segment |
| **High** | Core feature unusable for a significant segment, no easy workaround, blocks revenue or compliance |
| **Medium** | Important feature degraded; workaround exists but is annoying or partial |
| **Low** | Cosmetic, edge case, advanced-user-only, or rare condition with easy workaround |

If you're between two levels, pick the higher one and let the dev/PM downgrade. Severity is about user impact, not how hard the bug is to fix.

### 4. Apply the title rubric

Bug titles should let the reader understand the bug from the title alone. Pattern: **`<surface>: <specific failure>`** — not "doesn't work", not "broken".

- **Bad**: "Login page broken"
- **Better**: "Login: error 500 on submit when email contains a + character"

- **Bad**: "Search is weird"
- **Better**: "Product search: results are sorted oldest-first when 'price low to high' is selected"

## Edge cases

- **Intermittent bug**: write the report with `Frequency: Sometimes (~X%)`. Include everything you know about conditions that trigger it. Add a "Suggested next step" line ("attempt to reproduce 10 times in a fresh incognito session").
- **Cosmetic issue**: still produce a full report — screenshot is mandatory, severity is Low. Don't skip steps.
- **You can't reproduce yourself yet**: write a "reported by user" report with all the user's facts verbatim, mark `Frequency: Reported, not yet reproduced`, and add an explicit "needs reproduction" todo.
- **Multiple related defects**: file one ticket per root cause if you suspect different causes. File one ticket with a list of symptoms if you suspect a single cause.

## Anti-patterns to avoid

- "Doesn't work" / "broken" / "weird" — say specifically what happens.
- Speculating about the cause without evidence ("definitely a race condition") — the dev will diagnose.
- Reporting "I think this might also happen on mobile" without testing — either test or omit.
- One ticket per symptom when there's a single root cause — wastes triage time.
- Severity inflation ("everything is Critical") — this destroys the signal.
