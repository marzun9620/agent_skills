---
name: qa-test-cases
description: Converts acceptance criteria (Given/When/Then or any-format AC) into a structured set of executable test cases — happy path + boundary + negative + edge. Each test case has ID, preconditions, test data, steps, expected results, and a test-type tag. Use when the user says "write test cases for", "convert AC to test cases", "test cases for this AC", or hands over acceptance criteria and asks how to test them. Complements pm-execution:test-scenarios (which works from user stories) by focusing on AC granularity.
---

# QA Test Cases

Take one or more acceptance criteria and produce a set of test cases. Each test case is small enough to be executed by a person in one sitting, with a single binary pass/fail outcome.

## Process

### 1. Read the acceptance criteria

Accept:
- Given / When / Then format
- Bulleted AC from a Jira/Linear ticket
- Free-form "this must work" statements
- A PRD section with implicit AC

If AC is too vague to produce concrete test cases (e.g. "the feature should be intuitive"), surface that as an open question rather than inventing the criterion.

### 2. For each AC, generate test cases covering these categories

| Category | When to include | Typical count |
|---|---|---|
| **Happy path** | Always | 1 |
| **Boundary** | Numeric / length / date / quantity inputs | 1–3 |
| **Negative** | Any input the user could realistically get wrong | 1–3 |
| **Permission / role** | Multi-role systems | 1 per role |
| **State** | Stateful workflows (draft → published, locked, etc.) | 1 per state |
| **Concurrency** | Multi-user actions on the same entity | 1 if applicable |
| **Empty / max** | Lists, search results, attachments | 1 each |

Don't generate cases for categories that don't apply to the AC. A button that does one thing doesn't need a "concurrency" case.

### 3. Produce the test cases in this format

```md
## Test cases: <AC ID or one-line AC summary>

### TC-<NN>: <descriptive name in active voice>
**Type**: happy path | boundary | negative | permission | state | concurrency | empty | max
**Preconditions**:
- <state needed before the test runs>
- <user logged in as <role>>
**Test data**:
- <field>: <specific value>
- <field>: <specific value>
**Steps**:
1. <specific action>
2. <…>
3. <…>
**Expected results**:
- <observable outcome 1 — UI change, API response, DB row, email, log entry>
- <observable outcome 2>
**Notes** (optional): <anything that needs explanation>
```

### 4. Apply naming and ID conventions

- IDs: `TC-<feature-prefix>-<NN>` (e.g. `TC-CSV-01`). Keep them stable so they can be referenced from automation suites.
- Names: action-oriented and specific. **Good**: "Submit form with 256-char email triggers validation error". **Bad**: "Test email field".
- Steps: imperative, second-person elided. **Good**: "Click 'Submit'". **Bad**: "The user should click submit".
- Expected results: observable, not internal. **Good**: "A 'Saved' toast appears with text 'Profile updated'". **Bad**: "The save function is called".

## Worked example

**AC**: *"Given the user has admin role, when they click 'Delete user X', they must confirm in a dialog, after which user X is removed and a confirmation toast appears."*

**Test cases produced**:

- **TC-DEL-01** (happy path) — Admin deletes a regular user via confirm dialog → user removed, toast appears.
- **TC-DEL-02** (negative) — Admin clicks Delete, cancels the dialog → no deletion, user X still in list.
- **TC-DEL-03** (permission) — Non-admin user opens the same screen → Delete button is not shown.
- **TC-DEL-04** (state) — Admin tries to delete a user who has already been deleted (race condition) → error toast "user no longer exists", list refreshes.
- **TC-DEL-05** (state) — Admin tries to delete themselves → button is disabled (or shows "you cannot delete your own account").
- **TC-DEL-06** (state) — Admin deletes a user mid-active-session → user X is logged out immediately on next request.

Notice what's NOT generated:
- No boundary case (nothing numeric / length-bounded here)
- No empty/max case (single-user action, no list)
- No concurrency case (admin actions on different users don't conflict)

### 5. Hand off

Save the test cases to the user's test-case location (default `docs/test-cases/<feature>.md`). If the test cases reveal a gap in AC (e.g. "the AC doesn't say what happens when admin deletes themselves"), surface that as a question to the PM/spec author, not as a test case.

## Anti-patterns to avoid

- Generating one test case per word in the AC. Two AC lines often share preconditions and produce one test case.
- Test cases that exercise the framework, not the AC ("verify React renders"). Stay at the behaviour level.
- Vague expected results ("it should work"). Every expected result must be observable.
- Skipping the type tag. The type drives prioritisation later — happy path runs on every PR, boundary tests run nightly, etc.
- Generating cases for AC that's too vague. Push back on the AC instead.
