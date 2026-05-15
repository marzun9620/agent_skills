---
name: playwright-patterns
description: Patterns for writing Playwright E2E tests — POM structure, selector hierarchy, flow specs, waits, role contexts, dialog handling. Use when authoring or reviewing anything under /e2e.
version: 1.0.0
---

# Playwright Patterns

Codified playbook for a Playwright E2E suite (typically in `/e2e`). Distilled from production e2e work so the suite stays consistent as it grows. This skill covers *how* to write tests; pair it with an in-repo `AUTHORING.md` that covers *where* and *what runs when*.

## Quick Reference: Critical Rules

| Category | DO | DON'T |
|---|---|---|
| Selectors | `getByRole` → `getByLabel` → `getByTestId('data-pw=…')` → `getByText` | `page.locator('.css-class')` or positional `nth(n)` |
| Heading / landmark | `getByRole('main')` for authed shell | `getByRole('heading', { level })` for shadcn `CardTitle` (it's a `<div>`) |
| Page load signal | `toHaveTitle` (canonical routes) or form-field / `<main>` visible (alias routes) | Asserting only `toHaveURL` after `page.goto(url)` — tautological |
| POM `goto()` | End with `expectLoaded()` assertion | Return before the page is observable |
| Waits | `page.waitForResponse`, `expect.poll`, auto-waiting locators | `page.waitForTimeout(ms)` |
| Flow specs | `test.describe.serial` + phased sub-describes with `beforeAll`/`afterAll` contexts | Parallel flow specs against shared staging DB |
| Retries on flow | `retries: 0` | Retries on serial multi-step tests — step-1 replay leaks data |
| Multi-role tests | Separate `BrowserContext` per role (`adminPage` + `publicPage`) | One context that signs in/out between steps |
| Test data | Timestamp + `TEST_PARALLEL_INDEX` suffix | Hardcoded names — collides across parallel / retried runs |
| Secrets | `process.env.E2E_ADMIN_PASSWORD` read by `lib/config.ts` | Hardcoding in specs or committing `.env` |
| File uploads | `setInputFiles(path)` with fixtures from `e2e/fixtures/*` | Inline base64 or manual clicks on hidden inputs |
| Dialog handling | Handle both "dialog appeared" and "step advanced" branches | Blind `click()` then `waitForTimeout` |

## Page Object Model

POMs live in `e2e/pages/<name>.page.ts`. One file per page or major form.

### Contract

```ts
import { type Page, expect } from "@playwright/test";

export class <Name>Page {
    constructor(private readonly page: Page) {}

    // 1. Stable accessors as getters — let callers assert without extra POM methods
    get submitBtn() {
        return this.page.getByRole("button", { name: /submit|保存/i });
    }

    // 2. goto() always ends with an expectLoaded assertion
    async goto() {
        await this.page.goto("/your-route");
        await this.expectLoaded();
    }

    // 3. Copy-stable landing signal. For authed routes prefer getByRole('main').
    //    For public routes with real meta() titles, toHaveTitle works.
    async expectLoaded() {
        await expect(this.page.getByRole("main")).toBeVisible({ timeout: 30_000 });
    }

    // 4. Action methods named by USER INTENT, not selector.
    //    GOOD: async submitContactForm(...)
    //    BAD:  async clickSubmit()
    async submitForm(payload: { email: string; body: string }) {
        await this.page.getByLabel("メールアドレス").fill(payload.email);
        await this.page.getByLabel("メッセージ").fill(payload.body);
        await this.submitBtn.click();
    }
}
```

### When to split a POM into multiple files

- **One page, multiple complex surfaces** — separate files: `job-form.page.ts`, `job-view.page.ts`, `job-list.page.ts`
- **Multi-step wizard** — one POM per wizard with private per-step helpers (`fillStep1`, `fillStep2`…) and a public `fillAllSteps(data)` entry point. See `pages/*-form.page.ts` patterns in the reference.

### Fixture registration

Every POM gets a fixture in `e2e/fixtures/index.ts` so specs inject via destructuring:

```ts
export const test = base.extend<Fixtures>({
    signinPage: async ({ page }, use) => {
        await use(new SigninPage(page));
    },
});
```

Specs then:

```ts
test("does the thing", async ({ signinPage, page }) => {
    await signinPage.goto();
    await signinPage.signIn(email, password);
});
```

## Flow Specs (Multi-Step Journeys)

Flow specs go under `e2e/specs/<area>/<journey>.spec.ts` (or any non-smoke folder — picked up by the `staging-catchall` project). They **must** be serial, write carefully, and never retry.

### Multi-phase template

```ts
import { type BrowserContext, type Page, expect, test } from "@playwright/test";
import { adminStorageStatePath } from "../../lib/storage-state";
import { generateTestEmail } from "../../lib/email";

test.describe.serial("<journey name>", () => {
    let adminContext: BrowserContext;
    let adminPage: Page;
    const testEmail = generateTestEmail();
    let entityId: string;  // shared state across phases

    test.beforeAll(async ({ browser }) => {
        adminContext = await browser.newContext({ storageState: adminStorageStatePath });
        adminPage = await adminContext.newPage();
    });

    test.afterAll(async () => {
        await adminContext?.close();
    });

    test.describe.serial("Phase 1: setup", () => {
        test("Step 1: create entity", async () => {
            test.setTimeout(60_000);
            // ... use adminPage ...
            entityId = await ...;
        });
    });

    test.describe.serial("Phase 2: public interaction", () => {
        test("Step 2: public submits something", async ({ browser }) => {
            test.setTimeout(60_000);
            const publicContext = await browser.newContext();
            const publicPage = await publicContext.newPage();
            try {
                // ... use publicPage ...
            } finally {
                await publicContext.close();
            }
        });
    });

    test.describe.serial("Phase 3: verify & cleanup", () => {
        test("Step 3: admin verifies result", async () => {
            await adminPage.goto(`/admin/entity/${entityId}`);
            // ... assertions ...
        });
    });
});
```

### Why phased sub-describes

- `test.describe.serial` on outer + inner means every step runs in order
- Inner describes group related steps **for reporting** — you can scan the run output and see "Phase 2 failed" without reading 15 step titles
- `beforeAll` / `afterAll` survive across phase boundaries, so shared state (`adminPage`, `entityId`) stays intact

### Why separate `publicContext`

- The storage state makes `adminPage` authed. To exercise the unauthed public flow you **need** a fresh context — a single page can't switch identities cleanly
- Always `try { ... } finally { publicContext.close() }` — unclosed contexts leak Chromium processes

### Retries on flow specs: always 0

```ts
// playwright.config.ts
{
    name: "staging-flow",
    retries: 0, // Serial suites retry from Step 1, creating orphan data
    fullyParallel: false,
    ...
}
```

If step 3 fails and Playwright retries, it re-runs steps 1–3. Steps 1–2 already wrote data. You now have orphan companies / jobs / applicants in shared staging.

## Selectors

See `references/selector-patterns.md` for full hierarchy. TL;DR:

1. `getByRole('button', { name })` — accessibility-first
2. `getByLabel('メールアドレス')` — best for form fields
3. `getByTestId('page-admin-dashboard')` — once `data-pw` lands in the app
4. `getByText(...)` — last resort
5. `page.locator('.css-class')` — **forbidden**

For alias routes (`/signin`, `/dashboard`) where `meta()` isn't re-exported, title is empty — use `getByRole('main')` or a form field instead.

## Waits

**Never** `page.waitForTimeout(ms)`. Three real tools:

### 1. Auto-waiting locators

`expect(locator).toBeVisible({ timeout })` auto-retries. Use liberally.

### 2. Response-wait for backend mutations

When an action triggers an API call you need to settle before asserting:

```ts
const responsePromise = page.waitForResponse(
    (resp) => resp.url().includes("/api/documents/applicant-info"),
    { timeout: 30_000 },
);
await submitBtn.click();
await responsePromise;
```

Set the promise **before** the triggering action — otherwise you race the request.

### 3. `expect.poll` for async backend processes

When a scanner / cron / pipeline moves the record into a new state asynchronously:

```ts
await expect
    .poll(
        async () => {
            const count = await page.getByText("クリーン").count();
            if (count >= 2) return count;
            await page.reload();
            return count;
        },
        {
            intervals: [15_000],   // check every 15s
            timeout: 540_000,       // give up at 9 minutes
            message: "Expected both documents to reach クリーン status",
        },
    )
    .toBeGreaterThanOrEqual(2);
```

## Dialog handling

Validation dialogs can appear on "Next" / "Save" clicks. Handle both outcomes:

```ts
async clickNextStep() {
    const dialog = this.page.getByRole("dialog");
    // Pre-click: close any stale dialog
    if ((await dialog.count()) > 0) {
        await dialog.locator("button").first().click();
        await expect(dialog).toBeHidden({ timeout: 3_000 });
    }
    await this.nextButton.click();
    // Post-click: dialog might appear OR step advances
    const dialogAppeared = await dialog
        .waitFor({ state: "visible", timeout: 1_500 })
        .then(() => true)
        .catch(() => false);
    if (dialogAppeared) {
        await dialog.locator("button").first().click();
        await expect(dialog).toBeHidden({ timeout: 3_000 });
    }
}
```

## File uploads

Binary fixtures go under `e2e/fixtures/*` (e.g. `test-photo.png`, `test.pdf`). Reference them via `fileURLToPath` in the spec:

```ts
import path from "node:path";
import { fileURLToPath } from "node:url";

const currentDir = path.dirname(fileURLToPath(import.meta.url));
const testPdf = path.resolve(currentDir, "../../fixtures/test.pdf");

await page.locator("#document").setInputFiles(testPdf);
```

For multi-file uploads:

```ts
const inputs = page.locator("input[type='file']");
const count = await inputs.count();
for (let i = 0; i < count; i++) {
    await inputs.nth(i).setInputFiles(testPdf);
}
```

## Test data generation

Always collision-free:

```ts
const workerIndex = process.env.TEST_PARALLEL_INDEX ?? "0";
const ts = `${Date.now()}-${workerIndex}`;
export const testEntity = {
    name: `E2E-Entity-${ts}`,
    email: `e2e-${ts}@mailsac.com`,
} as const;
```

For emails that need Mailsac polling, use `generateTestEmail()` from `lib/email.ts` — it already bakes in the worker index.

## Anti-patterns (reject in review)

- **CSS class selectors** — break on any style refactor
- **Positional selectors without semantic context** — `nth(3)` is meaningless
- **`waitForTimeout`** — fixed sleeps hide real timing problems
- **Shared state between tests in the same project (non-serial)** — leaks, order-dependence
- **Retries > 0 on flow specs** — orphan data in shared DB
- **Mutation-heavy smoke specs** — smoke must be idempotent and parallel-safe
- **`page.click()` before `expect(locator).toBeVisible()`** — skips auto-wait
- **Per-step sign-in/out** — use separate contexts instead

## Deep dives (references/)

- [`pom-patterns.md`](references/pom-patterns.md) — POM contract, multi-step wizard patterns, getter conventions
- [`flow-patterns.md`](references/flow-patterns.md) — multi-phase flow specs, role contexts, shared state lifetime
- [`selector-patterns.md`](references/selector-patterns.md) — full selector hierarchy, `data-pw` migration plan
- [`wait-patterns.md`](references/wait-patterns.md) — auto-wait, response-wait, expect.poll, dialog handling
