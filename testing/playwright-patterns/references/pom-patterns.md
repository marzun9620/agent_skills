# POM Patterns (Reference)

## Getter-based accessors

Expose interactive elements as getters on the POM. Callers assert on them directly without extra wrapper methods:

```ts
export class JobFormPage {
    constructor(private readonly page: Page) {}

    get titleInput()       { return this.page.locator("#title"); }
    get salaryMin()        { return this.page.locator("#salaryMin"); }
    get salaryMax()        { return this.page.locator("#salaryMax"); }
    get saveBtn()          { return this.page.getByRole("button", { name: "保存" }); }
    get saveDraftBtn()     { return this.page.getByRole("button", { name: "下書き保存" }); }
    get hasOvertime()      { return this.page.locator("input[name='hasOvertime']"); }
}
```

Benefit: callers can write `await expect(jobForm.salaryMin).toHaveValue("280000")` without polluting the POM with an `expectSalaryMin(value)` method.

## Multi-step wizard

For wizards that can't sensibly be exposed field-by-field, use **private per-step helpers + a public entry point**:

```ts
export class ApplicantInfoFormPage {
    async fillAllStepsAndUpload(data: ApplicantInfoFormData) {
        await this.fillBasicInfo(data);
        await this.clickNextStep();
        await this.fillEducation();
        await this.clickNextStep();
        // ... 5 more steps ...
        await this.fillHealthAndSubmit();
        await this.uploadDocuments(data.pdfPath);
    }

    private async fillBasicInfo(data: ApplicantInfoFormData) { /* ... */ }
    private async fillEducation()                            { /* ... */ }
    private async clickNextStep()                            { /* ... */ }
}
```

- Private steps keep the test readable (one call vs. 50 lines inline)
- The public method takes a **typed data object**, not positional args
- Types for the data object live in the POM file or a sibling `types.ts`

## Action methods named by user intent

```ts
// GOOD — tells you what the user is doing
async submitContactForm(payload: ContactFormData) { ... }
async inviteUser(email: string) { ... }
async changeStatus(status: ApplicantStatus) { ... }

// BAD — describes clicks, not intent
async clickSubmit() { ... }
async fillEmailAndClick() { ... }
```

The spec should read like a user story:

```ts
await signinPage.goto();
await signinPage.signIn(email, password);
await dashboardPage.expectLoaded();
await contactPage.goto();
await contactPage.submitContactForm({ subject: "Test", body: "..." });
```

Not:

```ts
await signinPage.gotoPage();
await signinPage.clickEmail();
await signinPage.fillEmail(email);
// ... etc
```

## `goto()` always asserts load

Every POM's `goto()` should end with a load assertion so callers don't need to remember to check after navigation:

```ts
async goto() {
    await this.page.goto("/admin/applicants");
    await this.expectLoaded();
}

async expectLoaded() {
    await expect(this.page.getByTestId("page-admin-applicants")).toBeVisible({
        timeout: 30_000,
    });
}
```

Benefit: if the page fails to load, the failure points at the POM method, not at the first assertion deep in the spec.

## Search-then-open helper

Common pattern for list → detail navigation:

```ts
async searchAndOpen(email: string) {
    await this.page.goto("/admin/applicants");
    await this.page.getByTestId("applicant-search-input").fill(email);
    await this.page.getByTestId("applicant-search-button").click();

    const row = this.page.getByRole("row").filter({ hasText: email }).first();
    await expect(row).toBeVisible({ timeout: 10_000 });
    await row.click();
    await this.page.waitForURL(/\/admin\/applicants\/.*\/edit/, { timeout: 15_000 });
}
```

Filter by text on `getByRole('row')` is stable — it survives column reorders and styling changes.

## Assert values

For edit forms, pair `fill(data)` with `assertValues(data)`:

```ts
async fill(data: JobFormData)         { /* fill every field from data */ }
async assertValues(data: JobFormData) { /* assert every field matches data */ }
```

Then a round-trip test becomes:

```ts
await jobForm.fill(DRAFT_DATA);
await jobForm.saveDraftBtn.click();
await page.waitForURL("**/admin/job");
await page.goto(`/admin/job/${id}/edit`);
await jobForm.assertValues(DRAFT_DATA);
```

Proves persistence without hand-writing per-field assertions in every spec.
