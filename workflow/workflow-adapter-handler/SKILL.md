---
name: workflow-adapter-handler
description: >
  HTTP Handler（Hono + OpenAPI）の実装手順。adapter 層のみ Effect.runPromise 許可。
  describeRoute で OpenAPI 定義、Presenter で Domain → DTO 変換。
  トリガー: API endpoint 作成、Hono handler、HTTP adapter、REST API、
  OpenAPI、describeRoute、ルーティング
version: 1.1.0
---

# HTTP Handler 実装手順

ADR-0004 / ADR-0006 準拠。adapter 層のみが Effect ↔ Promise のブリッジを担当。

## Import ルール（重要）

全ての cross-directory import は **barrel（index.js）経由**（ADR-0004 §7）:

```typescript
// ✅ 正しい
import { Entity, EntityId } from "~/domain/{module}/index.js";
import { findEntity } from "~/usecase/{module}/index.js";
import { notFound, internalServerError } from "~/packages/server/index.js";

// ❌ 禁止
import { findEntity } from "~/usecase/{module}/findEntity.js";
```

adapter/http 内部の import は submodule root barrel 経由:
```typescript
// ✅ adapter/http 内部
import type { EffectRuntimeEnv } from "~/adapter/http/middleware/index.js";
```

## 1. Response Schema 定義

ファイル: `apps/datahub/src/adapter/http/schemas/{resource}.ts`

```typescript
import { Schema } from "effect";
import { paginatedResponse } from "./common.js";

const EntityItemSchema = Schema.Struct({
  id: Schema.String,
  name: Schema.String,
  status: Schema.Literal("ACTIVE", "ARCHIVED"),
}).annotations({
  identifier: "EntityItem",
  description: "Entity summary",
});

export const EntityDetailResponse = Schema.standardSchemaV1(
  Schema.Struct({
    id: Schema.String,
    name: Schema.String,
    status: Schema.Literal("ACTIVE", "ARCHIVED"),
  }).annotations({
    identifier: "EntityDetailResponse",
    description: "Detailed entity",
  }),
);

export const EntityListResponse = paginatedResponse(EntityItemSchema, "EntityListResponse");
```

- `Schema.standardSchemaV1()` でラップ
- `.annotations({ identifier, description })` で OpenAPI 情報付与
- ページネーションは `paginatedResponse` ヘルパーを使用

## 2. Presenter 定義

ファイル: `apps/datahub/src/adapter/http/presenters/{resource}Presenter.ts`

```typescript
import { Entity } from "~/domain/{module}/index.js";

export const toEntityDetailResponse = (entity: Entity) => ({
  id: entity.id,
  name: entity.name,
  status: entity.status,
});

export const toEntityItemResponse = (entity: Entity) => ({
  id: entity.id,
  name: entity.name,
  status: entity.status,
});
```

- Domain Entity → HTTP DTO の変換
- snake_case のフィールド名（HTTP API 規約）

## 3. Route Handler 定義

ファイル: `apps/datahub/src/adapter/http/routes/{resource}.ts`

```typescript
import { Hono } from "hono";
import { describeRoute } from "hono-openapi";
import { resolver } from "hono-openapi/effect";
import type { EffectRuntimeEnv } from "~/adapter/http/middleware/index.js";
import { EntityDetailResponse } from "~/adapter/http/schemas/{resource}.js";
import { toEntityDetailResponse } from "~/adapter/http/presenters/{resource}Presenter.js";
import { findEntity } from "~/usecase/{module}/index.js";
import { EntityId } from "~/domain/{module}/index.js";
import { notFound, internalServerError } from "~/packages/server/index.js";

export const entitiesRoute = new Hono<EffectRuntimeEnv>()
  .get(
    "/entities/:id",
    describeRoute({
      summary: "Get entity by ID",
      tags: ["Entities"],
      security: [{ "X-User-Context": [] }],
      responses: {
        200: {
          description: "Entity found",
          content: { "application/json": { schema: resolver(EntityDetailResponse) } },
        },
        404: { description: "Entity not found" },
      },
    }),
    async (c) => {
      const id = EntityId.make(c.req.param("id"));
      const result = await c.var.runAuthenticated(
        findEntity(id).pipe(
          Effect.catchTags({
            EntityNotFoundError: () =>
              Effect.fail(notFound({ detail: "Entity not found", code: "ENTITY_NOT_FOUND" })),
            RepositoryError: () =>
              Effect.fail(internalServerError({ code: "INTERNAL_ERROR" })),
          }),
          Effect.map(toEntityDetailResponse),
        ),
      );
      return c.json(result);
    },
  );
```

- `c.var.runAuthenticated()` で認証済み Effect 実行
- `c.var.runHttp()` で認証不要の Effect 実行
- `Effect.catchTags` で domain/infra エラーを `HttpError` に変換
- HttpError の `code` は `ProblemInit.code` で直接指定（`extensions` は使わない）

## 4. Route 登録

ファイル: `apps/datahub/src/setup.ts`

```typescript
// privateRoutes に追加（認証が必要な場合）
privateRoutes.route("/api/v1", entitiesRoute);

// apiRoutes にも追加（OpenAPI spec 生成用）
apiRoutes.route("/api/v1", entitiesRoute);
```

## 5. Barrel Export

ファイル: `apps/datahub/src/adapter/http/routes/index.ts` に追加
ファイル: `apps/datahub/src/adapter/http/schemas/index.ts` に追加
ファイル: `apps/datahub/src/adapter/http/presenters/index.ts` に追加（必要に応じて作成）

## 6. HTTP Test

ファイル: `apps/datahub/tests/adapter/http/{resource}.test.ts`

```typescript
import { app } from "../../helpers/testApp.js";

describe("GET /api/v1/entities/:id", () => {
  it("returns 200 with entity detail", async () => {
    const entity = await EntityFactory.create(getDb());
    const res = await app.request(`/api/v1/entities/${entity.publicId}`, {
      headers: { "X-User-Id": testUserId },
    });
    expect(res.status).toEqual(200);
    const body = await res.json();
    expect(body.id).toEqual(entity.publicId);
  });

  it("returns 404 when entity not found", async () => {
    const res = await app.request("/api/v1/entities/non-existent", {
      headers: { "X-User-Id": testUserId },
    });
    expect(res.status).toEqual(404);
  });
});
```

## テスト踏襲ルール

実装前に、plan の **Ref test** に指定された既存テストファイルを読むこと:
- 基本: `tests/adapter/http/` 内の既存テストを参考にする
- `app.request()` でHTTPリクエストを送信するパターンを踏襲
- ステータスコード + レスポンスボディの両方を検証
- 認証ヘッダー（`X-User-Id`）の有無でケースを分ける
- `expect(res.status).toEqual(200)` を使う

## チェックリスト

- [ ] `Effect.runPromise` は adapter 層のみ（`c.var.runHttp` / `c.var.runAuthenticated` 経由）
- [ ] `describeRoute` で OpenAPI 定義
- [ ] Domain エラー → HttpError の変換が `Effect.catchTags` で行われている
- [ ] HttpError の `code` は `ProblemInit.code` で直接指定
- [ ] Presenter で Domain → DTO 変換
- [ ] `setup.ts` に route 登録
- [ ] barrel export が存在
- [ ] PII がログに含まれていない（ADR-0006）
