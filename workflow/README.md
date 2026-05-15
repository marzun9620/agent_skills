# Workflow skills

Clean-architecture and Codex-CLI workflow skills, geared toward Effect-TS + Drizzle + Hono backends with layered domain/usecase/infrastructure separation. Many descriptions are in Japanese — the skills themselves drive bilingual implementation steps.

| Skill | Description |
|---|---|
| [`workflow-adapter-handler`](workflow-adapter-handler/) | HTTP Handler（Hono + OpenAPI）の実装手順。adapter 層のみ Effect.runPromise 許可。 describeRoute で OpenAPI 定義、Presenter で Domain → DTO 変換。 トリガー: API endpoint 作成、Hono handler、HTTP adapter、REST API、 OpenAPI、describeRoute、ルーティング |
| [`workflow-close-plan`](workflow-close-plan/) | 完了した plan を done/ に移動し、lessons learned を記録して commit + push する。 /run 完了後や /review APPROVED 後に呼ぶ。 トリガー: /close-plan, plan完了, planをdoneに, lessons記録 |
| [`workflow-codex-implement`](workflow-codex-implement/) | Codex CLI に plan の 1 task を TDD 実装させるスキル。 `codex exec --full-auto` の呼び出しパターン、Resume（修正指示）、Post-check を定義。 トリガー: /run、Codex 実装委譲、TDD 実装、plan task 実行 |
| [`workflow-codex-plan-review`](workflow-codex-plan-review/) | Codex CLI にプランレビューを委譲するスキル。ユーザー提示前に致命的問題を検出。 Initial Review + Re-review（resume --last）の反復パターン。最大5回ループ。 トリガー: /plan レビュー、Codex プランレビュー、plan 品質チェック |
| [`workflow-codex-review`](workflow-codex-review/) | Codex CLI にコードレビューを委譲するスキル。read-only sandbox で実行。 Mode A: per-task review（git diff HEAD~1）、Mode B: PR review（gh pr diff）。 トリガー: /run レビュー、/review、Codex レビュー委譲、コードレビュー |
| [`workflow-di-composition`](workflow-di-composition/) | DI 層（Composition Root）の Layer 登録手順。appLayer.ts への追加方法、 Layer 依存順、テスト用 Layer の作り方、ManagedRuntime の使い方。 トリガー: DI、Layer 登録、appLayer、Composition Root、 Layer.mergeAll、Layer.provide、テスト Layer、ManagedRuntime、 依存注入、サービス登録 |
| [`workflow-domain-entity`](workflow-domain-entity/) | Domain Entity の実装手順。Schema.Class + Brand で Entity 定義、Value Object、 Domain Error（Schema.TaggedError）、barrel export。 トリガー: domain entity 作成、Schema.Class、Brand型、ドメインモデル、 Value Object、ドメインエラー、domain層実装 |
| [`workflow-execlog-write`](workflow-execlog-write/) | 実行ログ（.execlog/）への記録手順。各 task 完了後にエントリ追加。 Final Handoff エントリは plan 完了時。 トリガー: execlog、実行ログ、進捗記録、タスク完了記録、 night-run ログ、handoff |
| [`workflow-gateway`](workflow-gateway/) | Gateway（外部 API クライアント）の実装手順。Port を Context.Tag で定義し、 Infrastructure で Layer.effect 実装。GatewayError でラップ、externalApiRetryPolicy 適用。 トリガー: gateway 作成、外部 API、Capsule、TableCheck、HTTP クライアント、 外部サービス連携、API 呼び出し、webhook |
| [`workflow-linear-ops`](workflow-linear-ops/) | Linear issue の操作手順。@schpet/linear-cli を使った issue の ステータス更新、コメント追加、PR 連携。 トリガー: Linear、issue 更新、ステータス変更、linear-comment、 linear-update、進捗報告、In Review |
| [`workflow-observability`](workflow-observability/) | ログ・トレース・メトリクスの実装ルール。Effect.withLogSpan、Effect.fn、 withRetryLogging、ログ分類（access/application/audit）、PII 非出力、 メッセージコード規約、RequestContext、W3C trace。 トリガー: ログ、トレース、observability、logging、telemetry、 Effect.logInfo、Effect.withLogSpan、PII、監査ログ、audit、 Cloud Trace、RequestContext |
| [`workflow-plan-update`](workflow-plan-update/) | Plan ファイル（.planning/plans/）のチェックボックス更新と Status 管理。 task 完了時に checkbox を更新し、全 task 完了で done/ に移動。 トリガー: plan更新、タスク完了マーク、チェックボックス、 plan status、計画更新 |
| [`workflow-pr-create`](workflow-pr-create/) | PR 作成手順。task check 全通過を確認し、gh pr create で PR を作成。 plan の Linear ID があれば Linear 更新。 トリガー: PR作成、プルリクエスト、ship、gh pr create、 マージリクエスト、コードレビュー依頼 |
| [`workflow-repository`](workflow-repository/) | Repository（Port + Infrastructure）の実装手順。Port を Context.Tag で定義し、 Drizzle ORM で Layer.effect 実装。Integration test は real DB。 トリガー: repository 作成、Drizzle実装、port定義、DB操作、 infrastructure実装、Layer.effect、findById、データベース |
| [`workflow-test-factory`](workflow-test-factory/) | テスト用 Factory の作成手順。DB に insert するための Factory パターン。 Drizzle ORM + Vitest 環境で使用。 トリガー: Factory 作成、テストデータ、テストヘルパー、 EntityFactory、create、build、テストフィクスチャ |
| [`workflow-usecase`](workflow-usecase/) | UseCase の実装手順。Effect<A, E, R> で定義し、Port 経由で infrastructure に依存。 E channel に全エラー型を明示。Unit test は Port を mock Layer で差し替え。 トリガー: usecase 作成、ビジネスロジック、ユースケース実装、 Effect.gen、Effect.fn、ドメインロジック |

_See the [repo README](../README.md) for install instructions._
