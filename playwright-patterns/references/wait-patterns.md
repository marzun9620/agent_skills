# Wait Patterns (Reference)

## Rule 0: never `page.waitForTimeout(ms)`

Fixed sleeps paper over real timing issues. They make specs flaky on slow runners and wasteful on fast ones. Every wait should be tied to a real condition.

## Auto-waiting locators

The default. `expect(locator).toBeVisible({ timeout })` retries until the condition holds or the timeout fires:

```ts
await expect(page.getByRole("button", { name: "Save" })).toBeVisible({ timeout: 10_000 });
await expect(page.getByText("成功")).toBeVisible({ timeout: 30_000 });
```

Pair with `.toBeHidden({ timeout })` / `.toBeEnabled()` / `.toHaveText()` etc. for other conditions.

## Response-wait for backend mutations

When a click triggers an API call you need settled before the next assertion:

```ts
const responsePromise = page.waitForResponse(
    (resp) => resp.url().includes("/api/documents/applicant-info"),
    { timeout: 30_000 },
);
await submitBtn.click();
await responsePromise;

// Now safe to assert on post-response UI state:
await expect(successDialog).toBeVisible();
```

**Critical:** set the promise **before** the triggering action. If you `click()` first and then `waitForResponse`, you race — if the response came back fast, you miss it and hang until timeout.

### Matching the response URL

- Substring match: `resp.url().includes("/api/documents")`
- Regex: `/\/api\/documents\//.test(resp.url())`
- Status filter: `resp.url().includes("/api/x") && resp.status() === 200`

## `expect.poll` for async backend processes

When the UI state only flips after an out-of-band process (scanner, cron, job queue):

```ts
await expect
    .poll(
        async () => {
            const count = await page.getByText("クリーン").count();
            if (count >= 2) return count;
            // Reload to refetch data
            await page.reload();
            await page.getByText("提出書類").first().click();
            await expect(page.getByText("提出済").first()).toBeVisible({ timeout: 10_000 });
            return count;
        },
        {
            intervals: [15_000],   // poll cadence
            timeout: 540_000,       // give up
            message: "Expected both documents to reach クリーン status",
        },
    )
    .toBeGreaterThanOrEqual(2);
```

### When to use it vs response-wait

| Situation | Use |
|---|---|
| Next button click triggers the API call you care about | `waitForResponse` |
| API call happens inside a scheduled job or webhook (not tied to a UI click) | `expect.poll` |
| State transitions gated by a cron running every N minutes | `expect.poll` with `timeout = N * 60 * 1000 * 1.5` |

### Intervals array

`intervals: [15_000]` means "check every 15s". You can pass multiple values for backoff:

```ts
intervals: [1_000, 1_000, 2_000, 5_000, 10_000]
// checks at 1s, 2s, 4s, 9s, 19s, then 29s, 39s, 49s, ...
```

## Dialog handling with both branches

Validation dialogs can appear or not, depending on input. Handle both:

```ts
async clickNextStep() {
    const dialog = this.page.getByRole("dialog");

    // Pre-click: dismiss any stale dialog left from a prior step
    if ((await dialog.count()) > 0) {
        await dialog.locator("button").first().click();
        await expect(dialog).toBeHidden({ timeout: 3_000 });
    }

    // The action itself
    const nextButton = this.page
        .locator("button")
        .filter({ hasText: /Next Step|Next|次へ/i })
        .last();
    await expect(nextButton).toBeVisible({ timeout: 5_000 });
    await nextButton.click();

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

### Why the `.then(() => true).catch(() => false)` dance

`waitFor` throws on timeout, which Playwright will surface as a test failure. Catching it converts the timeout into a boolean, so "dialog didn't appear" is a normal branch, not a failure.

## `waitForURL` for navigation

After a submit that redirects:

```ts
await submitBtn.click();
await page.waitForURL("**/admin/job", { timeout: 30_000 });
```

Glob patterns match the same way as Playwright's test selection. For regex:

```ts
await page.waitForURL(/\/admin\/applicants\/[^/]+\/edit/, { timeout: 15_000 });
```

## Composition: settle multiple things

For a step that clicks, triggers an API call, and ends on a new URL:

```ts
const responsePromise = page.waitForResponse(/\/api\/jobs\/create/);
await submitBtn.click();
await Promise.all([
    responsePromise,
    page.waitForURL("**/admin/job/*/edit"),
]);
```

`Promise.all` with multiple waits is rarely wrong — better to over-specify than race.

## Anti-patterns (reject on review)

```ts
// Don't do any of these:
await page.waitForTimeout(5000);              // fixed sleep
await new Promise(r => setTimeout(r, 5000));   // same, dressed up
await page.locator("button").click();          // skips auto-wait
await expect(loc).toBeVisible({ timeout: 1 }); // suspiciously short — flaky
```
