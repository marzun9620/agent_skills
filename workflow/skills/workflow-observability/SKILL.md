---
name: workflow-observability
description: >
  Logging, tracing, and metrics implementation rules. Covers Effect.withLogSpan,
  Effect.fn, withRetryLogging, log classification (access/application/audit),
  no-PII output, message code conventions, RequestContext, W3C trace.
  Triggers: logging, tracing, observability, telemetry,
  Effect.logInfo, Effect.withLogSpan, PII, audit log,
  Cloud Trace, RequestContext.
version: 1.0.0
---

# Observability 実装ルール

ADR-0006 準拠。Effect Logger + @effect/opentelemetry → GCP Cloud Logging/Trace。

## ログ分類（3種類）

| 種類 | 用途 | 保持期間 |
|------|------|---------|
| **access** | HTTP リクエストログ | 標準 |
| **application** | ビジネスロジックイベント | 標準 |
| **audit** | 機密操作（顧客データ変更等） | 5年（GCS） |

定数: `apps/datahub/src/packages/logging/constants.ts`

## ログスパン（Effect.withLogSpan）

**Infrastructure 層**: 全ての I/O 操作にスパン付与。

```typescript
// Repository
Effect.tryPromise({ ... }).pipe(
  Effect.withLogSpan("UserRepository.findById"),
)

// Gateway
Effect.tryPromise({ ... }).pipe(
  Effect.withLogSpan("CapsuleCrmGateway.searchParties"),
)
```

命名規約: `{ClassName}.{methodName}`

## Effect.fn（UseCase 層）

UseCase は `Effect.fn` でラップ。自動的に Cloud Trace スパンが生成される。

```typescript
export const buildUserContext = Effect.fn("buildUserContext")(
  (userId: UserId): Effect.Effect<UserContext, UserNotFoundError | RepositoryError, UserRepository> =>
    Effect.gen(function* () {
      const repo = yield* UserRepository;
      return yield* repo.findById(userId);
    }),
);
```

- Domain 層では使わない（純粋関数のみ）
- Infrastructure 層では `Effect.withLogSpan` を使う（`Effect.fn` ではない）

## withRetryLogging

`packages/resilience/withRetryLogging.ts` のヘルパー。リトライ時に WARN ログを出力。

```typescript
import { withRetryLogging, dbRetryPolicy, externalApiRetryPolicy } from "~/packages/resilience/index.js";

// Repository
withRetryLogging(effect, dbRetryPolicy, "UserRepository.findById")

// Gateway
withRetryLogging(effect, externalApiRetryPolicy, "CapsuleCrmGateway.searchParties")
```

| Policy | リトライ | バックオフ | 用途 |
|--------|---------|----------|------|
| `dbRetryPolicy` | 3回 | 100ms exponential | DB 操作 |
| `externalApiRetryPolicy` | 2回 | 500ms exponential | 外部 API |

## PII 非出力ルール（厳守）

以下のフィールドをログに出力してはならない:

- email, password, phone, name (firstName, lastName)
- ssn, address, dateOfBirth
- Capsule API レスポンスの raw data

```typescript
// ❌ 禁止
Effect.logInfo("User found").pipe(
  Effect.annotateLogs("email", user.email),
)

// ✅ OK
Effect.logInfo("User found").pipe(
  Effect.annotateLogs("userId", user.id),
)
```

sg-rules `adr0006-no-pii-in-log-annotations.yml` で自動検出。

## メッセージコード規約

`DH-{MODULE}-{E|W}{NNN}` 形式:

```typescript
Effect.logError("DH-AUTH-E001: User not found for given Firebase UID").pipe(
  Effect.annotateLogs("firebaseUid", uid),
)
```

- E = Error, W = Warning
- MODULE: AUTH, SYNC, IMPORT, USER, RESERVE, etc.

## RequestContext（トレース伝搬）

`packages/logging/requestContext.ts` で定義:

```typescript
class RequestContext extends Context.Tag("RequestContext")<
  RequestContext,
  {
    readonly requestId: string;
    readonly serviceIdentity: string;
    readonly traceContext: Option<{
      readonly traceId: string;
      readonly spanId: string;
      readonly traceSampled: boolean;
    }>;
  }
>() {}
```

- Adapter middleware が W3C `traceparent` ヘッダーからパース
- `effectRuntime.ts` で `Tracer.externalSpan()` に変換
- 全 Effect が Cloud Trace の子スパンになる

## Domain 層でのログ禁止

Domain 層（`src/domain/`）では `Effect.log*` / `console.log` 禁止。
sg-rules `adr0006-no-logging-in-domain.yml` で自動検出。

エラーは `Schema.TaggedError` で表現し、呼び出し元でログ出力する。

## 新機能追加時のチェックリスト

- [ ] Infrastructure の I/O に `Effect.withLogSpan` 付与
- [ ] UseCase を `Effect.fn` でラップ
- [ ] `withRetryLogging` で DB/外部 API 操作をラップ
- [ ] ログに PII を含めていない
- [ ] エラーログにメッセージコード付与（`DH-{MODULE}-{E|W}{NNN}`）
- [ ] Domain 層にログ呼び出しがない
- [ ] Adapter で `catchTags` → HttpError 変換時にエラーログ出力

## 参照ファイル

- ADR: `docs/adr/ADR-0006-datahub-logging-and-telemetry.md`
- GCP Logger: `apps/datahub/src/packages/logging/gcpLogger.ts`
- Tracing: `apps/datahub/src/packages/logging/tracingLayer.ts`
- RequestContext: `apps/datahub/src/packages/logging/requestContext.ts`
- Retry: `apps/datahub/src/packages/resilience/`
