# Flow Spec Patterns (Reference)

## Structure: `describe.serial` nested in `describe.serial`

```ts
test.describe.serial("<journey name>", () => {
    // Outer scope: shared state + setup/teardown
    let adminContext: BrowserContext;
    let adminPage: Page;
    let entityId: string;

    test.beforeAll(async ({ browser }) => { /* ... */ });
    test.afterAll(async () => { /* ... */ });

    // Phase 1 — grouped for reporting
    test.describe.serial("Phase 1: admin setup", () => {
        test("Step 1: create entity", async () => { /* ... */ });
        test("Step 2: configure entity", async () => { /* ... */ });
    });

    // Phase 2
    test.describe.serial("Phase 2: public interaction", () => {
        test("Step 3: public submits", async ({ browser }) => { /* ... */ });
    });

    // ... more phases
});
```

### Why this shape

- **Outer serial** — global ordering; no step starts until all prior steps finished
- **Inner serial** — keeps phases together in reporter output. "Phase 2 failed" is easier to triage than step 7 of 15
- **Shared state lives in the outer scope** — inner phases can read/write `entityId`, `adminPage`, `testEmail` from the outer closure
- **`beforeAll` / `afterAll` survive all phases** — the admin context stays open for the whole journey

## Role contexts

Flow specs often mix admin + public actors. Don't reuse one context — use `browser.newContext()` per role:

```ts
test.beforeAll(async ({ browser }) => {
    adminContext = await browser.newContext({ storageState: adminStorageStatePath });
    adminPage = await adminContext.newPage();
});

test("Step N: public action", async ({ browser }) => {
    const publicContext = await browser.newContext();  // no storageState = anonymous
    const publicPage = await publicContext.newPage();
    try {
        await publicPage.goto("/apply/jobs/" + jobId);
        // ... unauthenticated flow ...
    } finally {
        await publicContext.close();
    }
});
```

### Always `try / finally { context.close() }`

Unclosed contexts leak Chromium processes. On a CI runner with dozens of tests, this OOMs eventually. The `finally` is non-negotiable.

## Shared state across phases

Declare at the top of the outer describe, initialize during a step:

```ts
test.describe.serial("job application flow", () => {
    let createdJobId: string;
    const testEmail = generateTestEmail();  // computed once, shared

    test("create job", async () => {
        // ... after creation, extract id from URL or response
        createdJobId = (await extractIdFromUrl(adminPage)) ?? "";
        expect(createdJobId).toBeTruthy();

        // Annotation so the report shows which job we used
        test.info().annotations.push({
            type: "createdJobId",
            description: createdJobId,
        });
    });

    test("apply to job", async ({ browser }) => {
        // use createdJobId + testEmail from outer scope
    });
});
```

Annotations render in the HTML report, making post-mortems easier when a specific run fails.

## Per-step timeouts

Phases vary wildly in duration. Set `test.setTimeout(...)` per step instead of one global number:

```ts
test("Step 2: create and save draft", async () => {
    test.setTimeout(300_000);  // form has 50 fields + translation API calls
    // ...
});

test("Step 7: wait for document scan", async () => {
    test.setTimeout(600_000);  // scanner runs every 5 min — allow up to 10 min
    // ...
});
```

## Never retry flow specs

```ts
// playwright.config.ts
{
    name: "staging-flow",
    retries: 0,
    fullyParallel: false,
    ...
}
```

If step 3 of a 5-step flow fails, Playwright doesn't retry just step 3 — it retries the whole file from step 1. Steps 1–2 already wrote records. Retry doubles the rows. Over weeks of nightly runs you accumulate thousands of orphans in shared staging.

## Cleanup in the final phase

The last phase of a flow should delete whatever the first phase created:

```ts
test.describe.serial("Phase 5: cleanup", () => {
    test("delete test entity", async () => {
        await entityList.goto();
        await entityList.search(testEntityName);
        await entityList.delete(testEntityName);
        // verify row disappeared
    });
});
```

If cleanup is mandatory, put it in `afterAll` instead — runs even when earlier steps fail. Trade-off: `afterAll` doesn't show in the reporter, so failures in cleanup are less visible.

Good rule: **idempotent names + explicit delete step**. Re-running a flow against a leftover entity from a prior crash should succeed via "find and delete existing, then create" logic — not crash on "name already exists".

## Generating the test email

`lib/email.ts#generateTestEmail()` produces a unique `@mailsac.com` address per worker + timestamp. Always use this for emails you need to poll:

```ts
const testEmail = generateTestEmail();
// applicant submits testEmail.email
// later: const url = await getDocumentTokenFromEmail(testEmail.email);
```

Don't reuse an email across runs — Mailsac keeps messages for 24h, so "the first new email" logic picks up stale content.

## Example: admin creates → public applies → admin processes

See `cic-work/frontend/e2e/specs/flow/applicant-lifecycle.spec.ts` (source reference project) for a 5-phase, 20-step flow spec with two roles, shared state, response-waits, and `expect.poll` for async backend scanning.
