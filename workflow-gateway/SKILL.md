---
name: workflow-gateway
description: >
  Gateway（外部 API クライアント）の実装手順。Port を Context.Tag で定義し、
  Infrastructure で Layer.effect 実装。GatewayError でラップ、externalApiRetryPolicy 適用。
  トリガー: gateway 作成、外部 API、Capsule、TableCheck、HTTP クライアント、
  外部サービス連携、API 呼び出し、webhook
version: 1.1.0
---

# Gateway 実装手順

ADR-0004 / ADR-0006 準拠。外部サービス（Capsule CRM, TableCheck 等）への呼び出しを担当。
Repository と同じ `Context.Tag + Layer.effect` パターンだが、エラー型と retry policy が異なる。

## Import ルール（重要）

全ての cross-directory import は **barrel（index.js）経由** でなければならない（ADR-0004 §7）:

```typescript
// ✅ 正しい
import { GatewayError } from "~/usecase/ports/index.js";
import { AppConfig } from "~/packages/config/index.js";
import { externalApiRetryPolicy, withRetryLogging } from "~/packages/resilience/index.js";

// ❌ 禁止
import { AppConfig } from "~/packages/config/appConfig.js";
import { GatewayError } from "~/usecase/ports/errors.js";
```

## Repository との違い

| | Repository | Gateway |
|---|---|---|
| エラー型 | `RepositoryError` | `GatewayError` |
| Retry | `dbRetryPolicy` (3回, 100ms) | `externalApiRetryPolicy` (2回, 500ms) |
| I/O | Drizzle ORM → PostgreSQL | HTTP client → 外部 API |
| Mapper | DB row → Domain entity | JSON response → Domain entity |
| テスト | Real DB (Testcontainers) | Mock HTTP (msw 等) or contract test |

## 1. Port 定義

ファイル: `apps/datahub/src/usecase/ports/{service}Gateway.ts`

```typescript
import { Context, Effect } from "effect";
import { GatewayError } from "./errors.js";
import { Customer } from "~/domain/customer/index.js";

export class CapsuleCrmGateway extends Context.Tag("CapsuleCrmGateway")<
  CapsuleCrmGateway,
  {
    readonly searchParties: (query: string) => Effect.Effect<ReadonlyArray<Customer>, GatewayError>;
    readonly updateParty: (id: string, data: CustomerUpdate) => Effect.Effect<void, GatewayError>;
  }
>() {}
```

- エラー型は `GatewayError`（`usecase/ports/errors.ts` に既存）
- `RepositoryError` ではなく `GatewayError` を使う

Port の barrel export: `usecase/ports/index.ts` に追加。

## 2. Infrastructure 実装

ファイル: `apps/datahub/src/infrastructure/gateway/{service}/{service}GatewayLive.ts`

```typescript
import { Effect, Layer } from "effect";
import { CapsuleCrmGateway } from "~/usecase/ports/index.js";
import { GatewayError } from "~/usecase/ports/index.js";
import { AppConfig } from "~/packages/config/index.js";
import { withRetryLogging, externalApiRetryPolicy } from "~/packages/resilience/index.js";
import { toDomain } from "./mappers/partyMapper.js";

export const CapsuleCrmGatewayLive = Layer.effect(
  CapsuleCrmGateway,
  Effect.gen(function* () {
    const config = yield* AppConfig;
    const apiKey = config.capsuleApiKey;

    return {
      searchParties: (query) =>
        withRetryLogging(
          Effect.tryPromise({
            try: () =>
              fetch(`https://api.capsulecrm.com/api/v2/parties/search?q=${encodeURIComponent(query)}`, {
                headers: { Authorization: `Bearer ${apiKey}` },
              }).then((r) => r.json()),
            catch: (cause) => new GatewayError({ cause }),
          }).pipe(
            Effect.map((response) => response.parties.map(toDomain)),
            Effect.withLogSpan("CapsuleCrmGateway.searchParties"),
          ),
          externalApiRetryPolicy,
          "CapsuleCrmGateway.searchParties",
        ),
    };
  }),
);
```

**重要な違い（Repository との比較）:**
- `Effect.tryPromise` の catch で `GatewayError`（`RepositoryError` ではない）
- `externalApiRetryPolicy`（2回, 500ms — `dbRetryPolicy` の3回, 100ms ではない）
- `AppConfig` から API キーを取得
- PII を含む外部レスポンスのログ出力禁止（ADR-0006）

## 3. Mapper 定義

ファイル: `apps/datahub/src/infrastructure/gateway/{service}/mappers/{entity}Mapper.ts`

```typescript
import { Customer, CustomerId } from "~/domain/customer/index.js";

type CapsuleParty = {
  id: number;
  firstName: string;
  lastName: string;
  // ...
};

export const toDomain = (party: CapsuleParty): Customer =>
  new Customer({
    id: CustomerId.make(String(party.id)),
    name: `${party.firstName} ${party.lastName}`,
    // ...
  });
```

- 外部 API のレスポンス型 → Domain Entity への変換
- PII フィールドをログに出さないこと

## 4. DI 登録

ファイル: `apps/datahub/src/di/appLayer.ts`

`InfraLayer` の `Layer.mergeAll` に `CapsuleCrmGatewayLive` を追加。

## 5. ディレクトリ構造

```
infrastructure/gateway/
├── capsuleCrm/
│   ├── index.ts                    # barrel export
│   ├── capsuleCrmGatewayLive.ts    # Layer.effect 実装
│   └── mappers/
│       └── partyMapper.ts          # 外部 JSON → Domain
└── tableCheck/
    ├── index.ts
    ├── tableCheckGatewayLive.ts
    └── mappers/
        └── bookingMapper.ts
```

## テスト踏襲ルール

- Gateway のテストは外部 API をモックする（msw 等）
- Usecase テストでは `Layer.succeed(GatewayTag, { method: mockImpl })` で mock
- `Effect.either` + table-driven + AAA パターンを踏襲
- 外部 API のタイムアウト・レート制限エラーのケースも含める

## チェックリスト

- [ ] Port は `Context.Tag` で定義
- [ ] エラーは `GatewayError`（`RepositoryError` ではない）
- [ ] `externalApiRetryPolicy` を適用
- [ ] `withRetryLogging` でラップ
- [ ] `Effect.withLogSpan` でスパン付与
- [ ] PII を含むデータをログに出力していない（ADR-0006）
- [ ] AppConfig から API キーを取得（ハードコード禁止）
- [ ] DI 層（`appLayer.ts`）に登録済み
- [ ] barrel export が存在
