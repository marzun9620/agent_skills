---
name: workflow-test-factory
description: >
  テスト用 Factory の作成手順。DB に insert するための Factory パターン。
  Drizzle ORM + Vitest 環境で使用。
  トリガー: Factory 作成、テストデータ、テストヘルパー、
  EntityFactory、create、build、テストフィクスチャ
version: 1.0.0
---

# テスト Factory 実装手順

ADR-0005 準拠。Integration test で使用するテストデータ生成用の Factory。

## ファイル配置

ファイル: `apps/datahub/tests/factories/{entity}Factory.ts`

## 既存の Factory を必ず読む

実装前に既存の Factory ファイルを読んでパターンを踏襲すること:

```bash
ls apps/datahub/tests/factories/
```

## Factory パターン

```typescript
import { randomUUID } from "node:crypto";
import type { DrizzleDb } from "~/infrastructure/db/index.js";
import { entitiesInHw } from "~/infrastructure/db/index.js";

type EntityInsert = typeof entitiesInHw.$inferInsert;

const defaults: EntityInsert = {
  publicId: randomUUID(),
  name: "Test Entity",
  status: "ACTIVE",
};

export const EntityFactory = {
  /**
   * DB に insert して返す（integration test 用）
   */
  create: async (db: DrizzleDb, overrides?: Partial<EntityInsert>) => {
    const data = { ...defaults, publicId: randomUUID(), ...overrides };
    const [row] = await db.insert(entitiesInHw).values(data).returning();
    return row;
  },

  /**
   * DB に insert せず、テストデータのみ生成（unit test 用）
   */
  build: (overrides?: Partial<EntityInsert>): EntityInsert => ({
    ...defaults,
    publicId: randomUUID(),
    ...overrides,
  }),
};
```

## 重要ルール

- `create` は毎回 `randomUUID()` で一意な `publicId` を生成（テスト間の干渉を防ぐ）
- `defaults` にデフォルト値を定義（テストケースは必要なフィールドだけ override）
- `create` は `returning()` で insert した行を返す
- `build` は DB に触らず、テストデータのみ返す（unit test 向け）
- import は barrel 経由: `~/infrastructure/db/index.js`

## テストでの使い方

```typescript
import { EntityFactory } from "../../factories/entityFactory.js";
import { getDb } from "../../helpers/db.js";

// Arrange
const db = getDb();
const entity = await EntityFactory.create(db);
const entityId = EntityId.make(entity.publicId);

// override 付き
const entity = await EntityFactory.create(db, { name: "Custom Name", status: "ARCHIVED" });

// unit test 用（DB なし）
const data = EntityFactory.build({ name: "Test" });
```

## チェックリスト

- [ ] `create` が毎回一意な publicId を生成
- [ ] `defaults` にデフォルト値を定義
- [ ] `create` が `returning()` で行を返す
- [ ] `build` が DB に触らない
- [ ] 既存の Factory パターンを踏襲
- [ ] import が barrel 経由
