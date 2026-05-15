---
name: workflow-usecase
description: >
  UseCase implementation guide. Define as Effect<A, E, R>; depend on
  infrastructure through Ports. Make all error types explicit in the E channel.
  In unit tests, swap Ports via mock Layers.
  Triggers: usecase creation, business logic, usecase implementation,
  Effect.gen, Effect.fn, domain logic.
version: 1.1.0
---

# UseCase 実装手順

ADR-0004 準拠。usecase 層は domain と ports のみに依存。infrastructure/adapter の直接 import 禁止。

## Import ルール（重要）

```typescript
// ✅ 正しい — barrel 経由 + domain/ports のみ
import { Entity, EntityId } from "~/domain/{module}/index.js";
import { EntityRepository, RepositoryError } from "~/usecase/ports/index.js";

// ❌ 禁止 — 直接ファイル import
import { EntityRepository } from "~/usecase/ports/entityRepository.js";

// ❌ 禁止 — infrastructure/adapter への依存
import { DrizzleClient } from "~/infrastructure/db/index.js";
import { usersRoute } from "~/adapter/http/index.js";
```

## 1. UseCase 定義

ファイル: `apps/datahub/src/usecase/{module}/{usecaseName}.ts`

```typescript
import { Effect } from "effect";
import { Entity, EntityNotFoundError } from "~/domain/{module}/index.js";
import { EntityRepository } from "~/usecase/ports/index.js";
import { RepositoryError } from "~/usecase/ports/index.js";

export const findEntity = Effect.fn("findEntity")(
  (id: EntityId): Effect.Effect<Entity, EntityNotFoundError | RepositoryError, EntityRepository> =>
    Effect.gen(function* () {
      const repo = yield* EntityRepository;
      return yield* repo.findById(id);
    }),
);
```

- `Effect.fn(name)` でラップ（observability 対応）
- E channel に全エラー型を明示（型推論に頼らない）
- R channel に必要な Context.Tag を明示
- `yield* PortTag` で DI 取得

## 2. Context Tag（usecase 固有のコンテキストが必要な場合）

ファイル: `apps/datahub/src/usecase/{module}/{contextName}.ts`

```typescript
import { Context } from "effect";

export class SomeContext extends Context.Tag("SomeContext")<
  SomeContext,
  {
    readonly someField: string;
    readonly anotherField: number;
  }
>() {}
```

## 3. Barrel Export

ファイル: `apps/datahub/src/usecase/{module}/index.ts`

```typescript
export { findEntity } from "./findEntity.js";
export { SomeContext } from "./someContext.js";
```

`usecase/index.ts` にもモジュールの re-export を追加。

## 4. Unit Test

ファイル: `apps/datahub/tests/usecase/{module}/{usecaseName}.test.ts`

```typescript
import { Effect, Either, Layer } from "effect";
import { EntityRepository } from "~/usecase/ports/index.js";
import { findEntity } from "~/usecase/{module}/index.js";
import { Entity, EntityId, EntityNotFoundError } from "~/domain/{module}/index.js";
import { RepositoryError } from "~/usecase/ports/index.js";

type FindEntityCase = {
  scenario: string;
  entityId: EntityId;
  mockFindById: (id: EntityId) => Effect.Effect<Entity, EntityNotFoundError | RepositoryError>;
  expected: Either.Either<Entity, EntityNotFoundError | RepositoryError>;
};

const successCases: FindEntityCase[] = [
  {
    scenario: "returns entity when found",
    entityId: EntityId.make("test-id"),
    mockFindById: () => Effect.succeed(new Entity({ /* ... */ })),
    expected: Either.right(new Entity({ /* ... */ })),
  },
];

const failureCases: FindEntityCase[] = [
  {
    scenario: "returns error when not found",
    entityId: EntityId.make("missing-id"),
    mockFindById: (id) => Effect.fail(new EntityNotFoundError({ entityId: id })),
    expected: Either.left(new EntityNotFoundError({ entityId: EntityId.make("missing-id") })),
  },
];

it.each([...successCases, ...failureCases])("$scenario", async ({ entityId, mockFindById, expected }) => {
  const layer = Layer.succeed(EntityRepository, { findById: mockFindById });
  const result = await Effect.runPromise(
    Effect.either(findEntity(entityId).pipe(Effect.provide(layer))),
  );
  expect(result).toEqual(expected);
});
```

- Port を `Layer.succeed` で mock
- `Effect.either` で Either に変換
- `expect(result).toEqual(expected)` で比較
- Table-driven（`.each()`）
- AAA パターン

## テスト踏襲ルール

実装前に、plan の **Ref test** に指定された既存テストファイルを読むこと:
- 基本: `tests/usecase/` 内の既存テストを参考にする
- 構造を合わせる: type 定義、table-driven（`.each()`）、AAA パターン
- Port は `Layer.succeed(PortTag, { method: mockImpl })` で mock
- `Effect.either(usecase(...).pipe(Effect.provide(layer)))` パターンを踏襲
- `expect(result).toEqual(expected)` を使う

## チェックリスト

- [ ] domain と usecase/ports のみに依存（infrastructure/adapter の import なし）
- [ ] E channel に全エラー型を明示
- [ ] R channel に必要な Context.Tag を明示
- [ ] `Effect.fn(name)` でラップ
- [ ] Unit test で Port を mock Layer で差し替え
- [ ] barrel export が存在
- [ ] `any` を使っていない
