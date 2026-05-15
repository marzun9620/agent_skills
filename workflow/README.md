# Codex-Effect Workflows (niche)

[NICHE] Skills for Codex CLI workflows in a layered Effect-TS + Drizzle + Hono architecture. Most of the bodies are in Japanese (originally written for an internal team). Useful only if you've adopted this specific stack — otherwise, the other plugins are a better fit.

| Skill | Description |
|---|---|
| [`workflow-adapter-handler`](skills/workflow-adapter-handler/) | HTTP Handler implementation guide (Hono + OpenAPI). Only the adapter layer is allowed to call Effect.runPromise. Use describeRoute for OpenAPI definitions and Presenter for Domain → DTO conversion. Triggers: API endpoint creation, Hono handler, HTTP adapter, REST API, OpenAPI, describeRoute, routing. |
| [`workflow-close-plan`](skills/workflow-close-plan/) | Move a completed plan to done/, record lessons learned, then commit + push. Call after /run completes or /review is APPROVED. Triggers: /close-plan, plan completion, move plan to done, record lessons. |
| [`workflow-codex-implement`](skills/workflow-codex-implement/) | Delegate one plan task to Codex CLI for TDD implementation. Defines the `codex exec --full-auto` invocation pattern, Resume (corrections), and Post-check. Triggers: /run, Codex implementation delegation, TDD implementation, plan task execution. |
| [`workflow-codex-plan-review`](skills/workflow-codex-plan-review/) | Delegate plan review to Codex CLI. Detects critical issues before showing the plan to the user. Iterative Initial Review + Re-review (resume --last) pattern; up to 5 loops. Triggers: /plan review, Codex plan review, plan quality check. |
| [`workflow-codex-review`](skills/workflow-codex-review/) | Delegate code review to Codex CLI in a read-only sandbox. Mode A: per-task review (git diff HEAD~1). Mode B: PR review (gh pr diff). Triggers: /run review, /review, Codex review delegation, code review. |
| [`workflow-di-composition`](skills/workflow-di-composition/) | Layer registration in the DI layer (Composition Root). Covers adding to appLayer.ts, Layer dependency order, how to build test Layers, and using ManagedRuntime. Triggers: DI, Layer registration, appLayer, Composition Root, Layer.mergeAll, Layer.provide, test Layer, ManagedRuntime, dependency injection, service registration. |
| [`workflow-domain-entity`](skills/workflow-domain-entity/) | Domain Entity implementation guide. Define entities with Schema.Class + Brand, plus Value Objects, Domain Errors (Schema.TaggedError), and barrel exports. Triggers: domain entity creation, Schema.Class, Brand types, domain model, Value Object, domain error, domain layer implementation. |
| [`workflow-execlog-write`](skills/workflow-execlog-write/) | Recording entries to the execution log (.execlog/). Append an entry after each task completes; write the Final Handoff entry when the plan completes. Triggers: execlog, execution log, progress recording, task completion log, night-run log, handoff. |
| [`workflow-gateway`](skills/workflow-gateway/) | Gateway (external API client) implementation guide. Define the Port as a Context.Tag and implement with Layer.effect in Infrastructure. Wrap errors in GatewayError and apply externalApiRetryPolicy. Triggers: gateway creation, external API, Capsule, TableCheck, HTTP client, external service integration, API call, webhook. |
| [`workflow-linear-ops`](skills/workflow-linear-ops/) | Linear issue operations using @schpet/linear-cli — status updates, adding comments, PR linking. Triggers: Linear, issue update, status change, linear-comment, linear-update, progress report, In Review. |
| [`workflow-observability`](skills/workflow-observability/) | Logging, tracing, and metrics implementation rules. Covers Effect.withLogSpan, Effect.fn, withRetryLogging, log classification (access/application/audit), no-PII output, message code conventions, RequestContext, W3C trace. Triggers: logging, tracing, observability, telemetry, Effect.logInfo, Effect.withLogSpan, PII, audit log, Cloud Trace, RequestContext. |
| [`workflow-plan-update`](skills/workflow-plan-update/) | Checkbox updates and status management for plan files (.planning/plans/). Update checkboxes as tasks complete; move the plan to done/ once all tasks are done. Triggers: plan update, task completion mark, checkbox, plan status, plan revision. |
| [`workflow-pr-create`](skills/workflow-pr-create/) | PR creation flow. Verify all task checks pass, then create the PR with `gh pr create`. If the plan has a Linear ID, update Linear too. Triggers: PR creation, pull request, ship, gh pr create, merge request, code review request. |
| [`workflow-repository`](skills/workflow-repository/) | Repository (Port + Infrastructure) implementation guide. Define the Port as a Context.Tag and implement with Drizzle ORM via Layer.effect. Integration tests use a real DB. Triggers: repository creation, Drizzle implementation, port definition, DB operation, infrastructure implementation, Layer.effect, findById, database. |
| [`workflow-test-factory`](skills/workflow-test-factory/) | Test Factory authoring guide — Factory pattern for inserting rows into the database. Used in Drizzle ORM + Vitest environments. Triggers: Factory creation, test data, test helper, EntityFactory, create, build, test fixture. |
| [`workflow-usecase`](skills/workflow-usecase/) | UseCase implementation guide. Define as Effect<A, E, R>; depend on infrastructure through Ports. Make all error types explicit in the E channel. In unit tests, swap Ports via mock Layers. Triggers: usecase creation, business logic, usecase implementation, Effect.gen, Effect.fn, domain logic. |

## Install just this plugin

```
/plugin marketplace add marzun9620/agent_skills
/plugin install codex-effect-workflows@marzun9620-skills
```

_See the [repo README](../README.md) for the full picture._
