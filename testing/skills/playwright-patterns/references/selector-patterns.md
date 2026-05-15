# Selector Patterns (Reference)

## Hierarchy (use the first option that works)

| # | Selector | Example | When |
|---|---|---|---|
| 1 | `getByRole(role, { name })` | `page.getByRole("button", { name: "Save" })` | Buttons, links, headings with accessible names |
| 2 | `getByLabel(text)` | `page.getByLabel("メールアドレス")` | Form inputs — label↔input association is a contract |
| 3 | `getByTestId('…')` | `page.getByTestId("page-admin-dashboard")` | **Once `data-pw` attributes land.** Config sets `testIdAttribute: 'data-pw'` |
| 4 | `getByPlaceholder(text)` | `page.getByPlaceholder("検索...")` | When no label exists |
| 5 | `getByText(text)` | `page.getByText("Welcome")` | Visible copy, scoped by role when possible |
| 6 | `page.locator(css)` | `page.locator("#firstName")` | **Last resort.** Leave a `// TODO: replace with data-pw` comment |
| — | `page.locator('.css-class')` | — | **Forbidden.** Breaks on style refactor |

## Common traps

### shadcn `CardTitle` is a `<div>`, not a heading

`getByRole("heading", { name: "ログイン" })` **does not match** a `CardTitle` — the primitive renders a styled div. Use:

- `toHaveTitle(/ログイン/)` — if the route has `meta()`
- Form-field presence — `expect(page.getByLabel("メールアドレス")).toBeVisible()`

### Alias routes have empty titles

`/signin`, `/dashboard`, `/accounts` re-export their canonical route without copying `meta()`. `toHaveTitle()` returns `""`. Switch to `getByRole('main')` (authed layout wraps in `<main>`) or a form-field signal.

### Radix Select needs label → parent traversal

Radix combobox buttons don't have accessible labels tying them to the form label. Pattern:

```ts
const natSection = page.locator("label[for='nationality']").locator("..");
await natSection.locator("button").first().click();
await page.getByRole("option", { name: /Vietnam|ベトナム/i }).click();
```

### Row-scoped assertions

Filter `getByRole("row")` by text to scope without relying on column indices:

```ts
const row = page.getByRole("row").filter({ hasText: email }).first();
await expect(row).toBeVisible();
await expect(row.getByText("応募受付")).toBeVisible();
```

### Case-insensitive + multi-locale

```ts
page.getByRole("button", { name: /submit|送信|保存/i })
```

Regex on `name` handles EN + JP in one matcher — useful when the copy flips with `?lng=en`.

## `data-pw` migration plan

Config is pre-wired:

```ts
// playwright.config.ts
use: {
    testIdAttribute: "data-pw",
    ...
}
```

Once your app starts adding `data-pw` attributes, replace selectors in **new** POM code with `getByTestId(...)`. Existing POMs can migrate opportunistically.

### Naming convention to recommend to frontend

```
data-pw="<page>-<element>"
```

Examples:
- `data-pw="page-admin-dashboard"` — page root, asserted by smoke specs
- `data-pw="signin-email"`, `data-pw="signin-password"`, `data-pw="signin-submit"`
- `data-pw="applicant-search-input"`, `data-pw="applicant-search-button"`
- `data-pw="job-card"`, `data-pw="job-create-btn"`

Keep lowercase kebab-case, page-scoped so global uniqueness isn't required.

### Page-root test ID idiom

Every full page should have `data-pw="page-<area>-<name>"` on its root element. Lets smoke specs use a uniform helper:

```ts
export async function gotoAndExpectPage(
    page: Page,
    url: string,
    pageRootTestId: string,
) {
    await page.goto(url);
    await expect(page.getByTestId(pageRootTestId)).toBeVisible({ timeout: 30_000 });
}

// In smoke specs:
await gotoAndExpectPage(page, "/admin/job", "page-admin-job-list");
await gotoAndExpectPage(page, "/admin/applicants", "page-admin-applicants");
```

This is the cleanest smoke assertion — no per-page POM needed for render checks.

## Anti-patterns (reject on review)

- `page.locator(".btn-primary")` — brittle
- `page.locator("button").nth(2)` — meaningless positional
- `getByText("Save")` when `getByRole("button", { name: "Save" })` would scope correctly
- `page.locator("#id")` when there's an accessible label or role that would match
