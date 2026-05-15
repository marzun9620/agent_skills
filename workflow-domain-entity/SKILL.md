---
name: workflow-domain-entity
description: >
  Domain Entity の実装手順。Schema.Class + Brand で Entity 定義、Value Object、
  Domain Error（Schema.TaggedError）、barrel export。
  トリガー: domain entity 作成、Schema.Class、Brand型、ドメインモデル、
  Value Object、ドメインエラー、domain層実装
version: 1.1.0
---

# Domain Entity 実装手順

ADR-0001 / ADR-0004 準拠。domain 層は純粋なデータ定義のみ。I/O 禁止。

## ファイル構成（必ずこの構造に従う）

```
apps/datahub/src/domain/{module}/
├── {entity}Id.ts         # Brand 型 ID
├── {entity}Status.ts     # Enum（必要な場合）
├── {entity}.ts           # Entity 本体（Schema.Class）
├── errors.ts             # Domain Error（Schema.TaggedError）
└── index.ts              # Barrel export（全 public 型）
```

ファイル名は **camelCase**。1ファイル1責務。

## Import ルール（重要）

- 同一ディレクトリ内: `./` で直接 import OK
- cross-directory（他の domain module 等）: barrel（`index.js`）経由のみ

```typescript
// ✅ 同一ディレクトリ内
import { EntityId } from "./entityId.js";

// ✅ 他の domain module
import { UserId } from "~/domain/user/index.js";

// ❌ 禁止
import { UserId } from "~/domain/user/userId.js";
```

## 1. Entity 定義

ファイル: `apps/datahub/src/domain/{module}/{entity}.ts`

```typescript
import { Schema } from "effect";
import { EntityId } from "./entityId.js";

export class Entity extends Schema.Class<Entity>("Entity")({
  id: EntityId,
  name: Schema.String,
  status: EntityStatus,
  // nested value objects OK
}) {}
```

- `Schema.Class<T>(name)({fields})` で定義
- メソッドなし、純粋なデータコンテナ
- ネストされた Value Object / Enum を参照可能

## 2. Value Object（ID）

ファイル: `apps/datahub/src/domain/{module}/{entity}Id.ts`

```typescript
import { Schema } from "effect";

export const EntityId = Schema.String.pipe(Schema.brand("EntityId"));
export type EntityId = typeof EntityId.Type;
```

## 3. Enum（Status / Role / Kind）

ファイル: `apps/datahub/src/domain/{module}/{entity}Status.ts`

```typescript
import { Schema } from "effect";

export const EntityStatus = Schema.Literal("ACTIVE", "ARCHIVED");
export type EntityStatus = typeof EntityStatus.Type;
```

命名: `*Status`, `*Role`, `*Kind` を使う。`*Type` は避ける。

## 4. Domain Error

ファイル: `apps/datahub/src/domain/{module}/errors.ts`

```typescript
import { Schema } from "effect";
import { EntityId } from "./entityId.js";

export class EntityNotFoundError extends Schema.TaggedError<EntityNotFoundError>()(
  "EntityNotFoundError",
  { entityId: EntityId },
) {}
```

- `Schema.TaggedError` を使う（`Data.TaggedError` は domain 層で禁止）
- Brand にしない

## 5. Domain Service（必要な場合のみ）

ファイル: `apps/datahub/src/domain/services/{serviceName}.ts`

```typescript
import { Match, Option } from "effect";

// 純粋関数のみ。Effect を返す場合も I/O なし
export const checkPermission = (role: SystemRole) =>
  Match.value(role).pipe(
    Match.when("SYSTEM_ADMIN", () => Effect.void),
    Match.when("USER", () => Effect.fail(new InsufficientPermissionError({}))),
    Match.exhaustive,
  );
```

- nullable は `Option.fromNullable` + `Option.match` で処理
- `Match.value()` + `Match.exhaustive` でパターンマッチ

## 6. Barrel Export

ファイル: `apps/datahub/src/domain/{module}/index.ts`

```typescript
export { Entity } from "./entity.js";
export { EntityId } from "./entityId.js";
export type { EntityId as EntityIdType } from "./entityId.js";
export { EntityStatus } from "./entityStatus.js";
export { EntityNotFoundError } from "./errors.js";
```

cross-directory import はこの barrel 経由のみ。同一ディレクトリ内は `./` OK。

## テスト踏襲ルール

実装前に、plan の **Ref test** に指定された既存テストファイルを読むこと:
- 同モジュールのテストがあればそれを踏襲
- なければ `tests/domain/` 内の別モジュールのテストを参考にする
- 構造を合わせる: type 定義（`XxxCase`）、table-driven（`.each()`）、AAA パターン
- `expect(result).toEqual(expected)` を使う（`toBe` ではなく `toEqual`）

## チェックリスト

- [ ] `type` を使っている（`interface` 禁止 — ADR-0001）
- [ ] `Schema.TaggedError` を使っている（`Data.TaggedError` 禁止）
- [ ] I/O なし（postgres, drizzle, hono, node:fs, node:net の import なし）
- [ ] `_tag` への直接アクセスなし（`Schema.is()` / `Match.tag()` を使用）
- [ ] barrel export が存在する
- [ ] `any` を使っていない
- [ ] named export のみ（default export 禁止）
