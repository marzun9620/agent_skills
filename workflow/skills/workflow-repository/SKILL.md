---
name: workflow-repository
description: >
  Repository (Port + Infrastructure) implementation guide. Define the Port
  as a Context.Tag and implement with Drizzle ORM via Layer.effect.
  Integration tests use a real DB.
  Triggers: repository creation, Drizzle implementation, port definition,
  DB operation, infrastructure implementation, Layer.effect, findById, database.
version: 1.1.0
---

# Repository 実装手順

ADR-0004 / ADR-0005 準拠。Port → Infrastructure → Test の順で実装。

## Import ルール（重要）

全ての cross-directory import は **barrel（index.js）経由** でなければならない（ADR-0004 §7）:

```typescript
// ✅ 正しい
import { EntityRepository } from "~/usecase/ports/index.js";
import { DrizzleClient } from "~/infrastructure/db/index.js";
import { AppConfig } from "~/packages/config/index.js";

// ❌ 禁止 — 直接ファイル import
import { EntityRepository } from "~/usecase/ports/entityRepository.js";
import { AppConfig } from "~/packages/config/appConfig.js";
```

同一ディレクトリ内（`./`）の import は barrel 不要。

## 1. Port 定義

ファイル: `apps/datahub/src/usecase/ports/{entity}Repository.ts`

```typescript
import { Context, Effect } from "effect";
import { EntityId, Entity, EntityNotFoundError } from "~/domain/{module}/index.js";
import { RepositoryError } from "./errors.js";

export class EntityRepository extends Context.Tag("EntityRepository")<
  EntityRepository,
  {
    readonly findById: (id: EntityId) => Effect.Effect<Entity, EntityNotFoundError | RepositoryError>;
    readonly save: (entity: Entity) => Effect.Effect<void, RepositoryError>;
  }
>() {}
```

- `Context.Tag(name)<Tag, Interface>()` パターン
- E channel に全エラー型を明示
- `RepositoryError` は `usecase/ports/errors.ts` に既存
- **`save` の戻り値は `Effect<void, RepositoryError>`** — Entity を返さない。保存操作は副作用のみ。`Effect.asVoid` でラップすること

Port の barrel export: `usecase/ports/index.ts` に追加。

## 2. Mapper 定義

ファイル: `apps/datahub/src/infrastructure/db/mappers/{entity}Mapper.ts`

```typescript
import { Entity, EntityId } from "~/domain/{module}/index.js";
import { type entitiesInHw } from "~/infrastructure/db/index.js";

type EntityRow = typeof entitiesInHw.$inferSelect;

export const toDomain = (row: EntityRow): Entity =>
  new Entity({
    id: EntityId.make(row.publicId),
    name: row.name,
    status: row.status,
  });

export const toRow = (entity: Entity): EntityInsertRow => ({
  publicId: entity.id,
  name: entity.name,
  status: entity.status,
});
```

- 関数名は `toDomain` / `toRow`（エンティティ名をプレフィクスにしない）
- barrel export: `infrastructure/db/mappers/index.ts` に追加（ただし mapper は同一パッケージ内の直接 import も可）

## 3. Infrastructure 実装

ファイル: `apps/datahub/src/infrastructure/repository/{entity}RepositoryLive.ts`

```typescript
import { Effect, Layer } from "effect";
import { eq } from "drizzle-orm";
import { EntityRepository, RepositoryError } from "~/usecase/ports/index.js";
import { DrizzleClient, entitiesInHw } from "~/infrastructure/db/index.js";
import { EntityNotFoundError } from "~/domain/{module}/index.js";
import { toDomain, toRow } from "~/infrastructure/db/mappers/{entity}Mapper.js";
import { dbRetryPolicy, withRetryLogging } from "~/packages/resilience/index.js";

export const EntityRepositoryLive = Layer.effect(
  EntityRepository,
  Effect.gen(function* () {
    const { db } = yield* DrizzleClient;
    return {
      findById: (id) =>
        withRetryLogging(
          Effect.tryPromise({
            try: () => db.query.entitiesInHw.findFirst({ where: eq(entitiesInHw.publicId, id) }),
            catch: (cause) => new RepositoryError({ cause }),
          }).pipe(
            Effect.flatMap((row) =>
              row
                ? Effect.succeed(toDomain(row))
                : Effect.fail(new EntityNotFoundError({ entityId: id })),
            ),
            Effect.withLogSpan("EntityRepository.findById"),
          ),
          dbRetryPolicy,
          "EntityRepository.findById",
        ),

      save: (entity) =>
        withRetryLogging(
          Effect.tryPromise({
            try: () =>
              db.insert(entitiesInHw).values(toRow(entity)).onConflictDoUpdate({
                target: entitiesInHw.publicId,
                set: toRow(entity),
              }),
            catch: (cause) => new RepositoryError({ cause }),
          }).pipe(
            Effect.asVoid,
            Effect.withLogSpan("EntityRepository.save"),
          ),
          dbRetryPolicy,
          "EntityRepository.save",
        ),
    };
  }),
);
```

**重要ルール:**
- Repository メソッドは Layer 内で定義する（standalone 関数禁止）
- `save` は `Effect.asVoid` で void に変換（Entity を返さない）
- 全メソッドに `withRetryLogging` + `dbRetryPolicy` を適用
- 全メソッドに `Effect.withLogSpan("{ClassName}.{methodName}")` を付与
- barrel export: `infrastructure/repository/index.ts` に追加

## 4. DI 登録

ファイル: `apps/datahub/src/di/appLayer.ts`

`InfraLayer` の `Layer.mergeAll` に `EntityRepositoryLive` を追加。
詳細は **di-composition skill** を参照。

## 5. Integration Test

ファイル: `apps/datahub/tests/infrastructure/repository/{entity}Repository.test.ts`

```typescript
import { randomUUID } from "node:crypto";
import { it } from "@effect/vitest";
import { Effect, Either, ManagedRuntime, Schema } from "effect";
import { afterAll, beforeEach, describe, expect } from "vitest";
import { AppLayer } from "~/di/index.js";
import { Entity, EntityId, EntityNotFoundError } from "~/domain/{module}/index.js";
import { EntityRepository } from "~/usecase/ports/index.js";
import { EntityFactory } from "../../factories/entityFactory.js";
import { getDb } from "../../helpers/db.js";
import { truncateAll } from "../../helpers/truncate.js";

const runtime = ManagedRuntime.make(AppLayer);

beforeEach(async () => { await truncateAll(); });
afterAll(async () => { await runtime.dispose(); });

// --- findById ---

type FindByIdCase = {
  scenario: string;
  arrange: () => Promise<{ entityId: EntityId }>;
  assert: (result: Either.Either<unknown, unknown>) => void;
};

const findByIdCases: FindByIdCase[] = [
  {
    scenario: "returns entity when it exists",
    arrange: async () => {
      const db = getDb();
      const entity = await EntityFactory.create(db);
      return { entityId: EntityId.make(entity.publicId) };
    },
    assert: (result) => {
      expect(Either.isRight(result)).toEqual(true);
    },
  },
  {
    scenario: "returns EntityNotFoundError when entity does not exist",
    arrange: async () => ({ entityId: EntityId.make(randomUUID()) }),
    assert: (result) => {
      expect(Either.isLeft(result)).toEqual(true);
      if (Either.isLeft(result)) {
        expect(Schema.is(EntityNotFoundError)(result.left)).toEqual(true);
      }
    },
  },
];

describe("EntityRepositoryLive", () => {
  it.each(findByIdCases)("findById $scenario", async ({ arrange, assert }) => {
    const { entityId } = await arrange();
    const result = await runtime.runPromise(
      Effect.either(
        EntityRepository.pipe(Effect.flatMap((repo) => repo.findById(entityId))),
      ),
    );
    assert(result);
  });
});
```

## テスト踏襲ルール

実装前に、plan の **Ref test** に指定された既存テストファイルを読むこと:
- 基本: `tests/infrastructure/repository/userRepository.test.ts` を参考にする
- 構造を合わせる: type 定義（`FindByIdCase` 等）、table-driven（`.each()`）、AAA パターン
- `arrange` で Factory + real DB、`assert` で Either チェック
- `runtime.runPromise(Effect.either(...))` パターンを踏襲
- `expect(result).toEqual(expected)` を使う（`toBe` ではない）
- エラー型チェックは `Schema.is(ErrorClass)(result.left)` を使う

## チェックリスト

- [ ] Port は `Context.Tag` で定義
- [ ] `save` の戻り値は `Effect<void, RepositoryError>` — Entity を返さない
- [ ] Infrastructure は `Layer.effect` 内で定義（standalone 関数禁止）
- [ ] `Effect.tryPromise` で DB 操作をラップ
- [ ] `RepositoryError` で catch（`GatewayError` ではない）
- [ ] `withRetryLogging` + `dbRetryPolicy` を全メソッドに適用
- [ ] `Effect.withLogSpan` を全メソッドに付与
- [ ] Mapper の関数名は `toDomain` / `toRow`
- [ ] 全ての cross-directory import が barrel（index.js）経由
- [ ] DI 層（`appLayer.ts`）に登録済み
- [ ] Integration test が real DB で動作
- [ ] barrel export が存在（ports/index.ts, repository/index.ts）
