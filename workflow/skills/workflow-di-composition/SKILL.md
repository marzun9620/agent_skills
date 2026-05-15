---
name: workflow-di-composition
description: >
  Layer registration in the DI layer (Composition Root). Covers adding to
  appLayer.ts, Layer dependency order, how to build test Layers, and using
  ManagedRuntime.
  Triggers: DI, Layer registration, appLayer, Composition Root,
  Layer.mergeAll, Layer.provide, test Layer, ManagedRuntime,
  dependency injection, service registration.
version: 1.0.0
---

# DI Composition（Composition Root）手順

ADR-0004 準拠。`src/di/appLayer.ts` が唯一の Composition Root。

## Layer 依存順

```
Level 1: Packages（config, db, observability, time）
    ↓
Level 2: DrizzleClient（DB接続）
    ↓
Level 3: Infrastructure（Repository, Gateway, Service）
    ↓
Level 4: AppLayer（全 Layer を統合）
```

ファイル: `apps/datahub/src/di/appLayer.ts`

```typescript
// Level 1: Packages
const PackagesLayer = Layer.mergeAll(
  AppConfig.Live,
  SqlClient.Live,
  ObservabilityLive,
  CurrentTime.Live,
).pipe(Layer.provideMerge(AppConfig.Live));

// Level 2: Database
const DrizzleLayer = DrizzleClient.Live.pipe(
  Layer.provide(PackagesLayer),
);

// Level 3: Infrastructure
const InfraLayer = Layer.mergeAll(
  UserRepositoryLive,
  IdGeneratorLive,
  // ← 新しい Repository/Gateway/Service はここに追加
).pipe(Layer.provide(DrizzleLayer));

// Level 4: Full application
const AppLayer = InfraLayer.pipe(
  Layer.provideMerge(DrizzleLayer),
  Layer.provideMerge(PackagesLayer),
);

type AppLayer = Layer.Layer.Success<typeof AppLayer>;
```

## 新しい Layer の追加手順

### 1. Repository を追加する場合

```typescript
// InfraLayer に追加
const InfraLayer = Layer.mergeAll(
  UserRepositoryLive,
  IdGeneratorLive,
  FacilityRepositoryLive,  // ← 追加
).pipe(Layer.provide(DrizzleLayer));
```

- DrizzleClient に依存する → `DrizzleLayer` を provide 済みの InfraLayer に追加

### 2. Gateway を追加する場合

```typescript
// InfraLayer に追加（AppConfig から API キーを取得するため PackagesLayer も必要）
const InfraLayer = Layer.mergeAll(
  UserRepositoryLive,
  IdGeneratorLive,
  CapsuleCrmGatewayLive,  // ← 追加
).pipe(
  Layer.provide(DrizzleLayer),
  // Gateway が AppConfig に依存する場合は明示的に provide
);
```

### 3. 技術サービスを追加する場合

```typescript
// 外部依存がない場合は Layer.succeed で直接追加
const IdGeneratorLive = Layer.succeed(IdGenerator, {
  randomUuid: Effect.try({
    try: () => randomUUID(),
    catch: (cause) => new IdGenerationError({ cause }),
  }),
});
```

## Layer の種類

| パターン | いつ使う | 例 |
|---------|---------|-----|
| `Layer.effect(Tag, Effect.gen(...))` | 依存サービスが必要 | Repository, Gateway |
| `Layer.succeed(Tag, impl)` | 依存なし、同期的 | IdGenerator |
| `Layer.scoped(Tag, Effect.gen(...))` | リソース管理が必要 | SqlClient |

## テスト用 Layer

### Unit Test（UseCase テスト）

Port を `Layer.succeed` で mock:

```typescript
const mockUserRepository = Layer.succeed(UserRepository, {
  findById: (id) => Effect.succeed(new User({ /* ... */ })),
  save: () => Effect.void,
});

// テストで使用
const result = await Effect.runPromise(
  Effect.either(
    usecase(args).pipe(Effect.provide(mockUserRepository)),
  ),
);
```

### Integration Test（Repository テスト）

本番と同じ Layer 構成だが、テスト用 DB を使用:

```typescript
// tests/helpers/ にテスト用 AppLayer を定義
const TestAppLayer = Layer.mergeAll(
  UserRepositoryLive,
  IdGeneratorLive,
).pipe(
  Layer.provide(TestDrizzleLayer),
  Layer.provideMerge(TestPackagesLayer),
);

const runtime = ManagedRuntime.make(TestAppLayer);
```

## ManagedRuntime

Adapter 層と Integration テストで使用:

```typescript
// Adapter（effectRuntime.ts）
const runtime = ManagedRuntime.make(appLayer);
const result = await runtime.runPromise(effect);

// テスト
const runtime = ManagedRuntime.make(TestAppLayer);
afterAll(async () => { await runtime.dispose(); });
```

- `ManagedRuntime.make()` で作成
- `runtime.runPromise()` で Effect を実行
- `runtime.dispose()` でリソース解放（テストの `afterAll` で必須）

## ObservabilityLive（環境別）

```typescript
// Production
const ObservabilityLive = Layer.mergeAll(
  GcpLoggerLive,
  LogLevelLive,
  TracingLive,
);

// Development
const ObservabilityLive = Layer.mergeAll(
  PrettyLoggerLive,
  LogLevelLive,
  TracingLive,
);
```

`packages/logging/index.ts` で環境変数に基づいて切り替え。

## チェックリスト

- [ ] 新しい Layer を `InfraLayer` の `Layer.mergeAll` に追加
- [ ] 依存順が正しい（Repository/Gateway → DrizzleLayer → PackagesLayer）
- [ ] `type AppLayer` の型が更新されている（自動推論）
- [ ] テスト用 Layer でも同じ Port を提供している
- [ ] `ManagedRuntime.dispose()` がテストの `afterAll` で呼ばれている

## 参照ファイル

- Composition Root: `apps/datahub/src/di/appLayer.ts`
- AppConfig: `apps/datahub/src/packages/config/appConfig.ts`
- SqlClient: `apps/datahub/src/packages/db/sqlClient.ts`
- DrizzleClient: `apps/datahub/src/infrastructure/db/drizzleClient.ts`
- Observability: `apps/datahub/src/packages/logging/index.ts`
- EffectRuntime: `apps/datahub/src/adapter/http/middleware/effectRuntime.ts`
