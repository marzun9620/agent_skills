---
name: workflow-codex-implement
description: >
  Delegate one plan task to Codex CLI for TDD implementation. Defines the
  `codex exec --full-auto` invocation pattern, Resume (corrections), and Post-check.
  Triggers: /run, Codex implementation delegation, TDD implementation, plan task execution.
version: 1.0.0
---

# Codex Implement — 1 Task TDD 実装

Claude Code（orchestrator）が Codex に plan の 1 task だけを TDD 実装させるためのスキル。
Codex は `AGENTS.md` を自動読み込みするが `.claude/` は見えないため、プロンプトでスキルファイルのパスを明示する。

## When to use

`/run` の Per-Task Loop で、次の未完了 task を Codex に委譲するとき。

## Parameters

| Name | Example | Description |
|------|---------|-------------|
| `branch` | `feat/capsule-gateway` | ブランチ名（plan 検索 + execlog 用） |
| `task_number` | `3` | plan 内の task 番号 |
| `task_description` | `CapsuleCRM Gateway port definition` | task の1行要約（プロンプトに埋め込む） |

## Invocation

```bash
pnpm codex exec --full-auto \
  -m gpt-5.4 \
  -c model_reasoning_effort=medium \
  "ブランチ {branch} の plan から task {task_number} だけを実装して。
   task: {task_description}

   手順:
   1. .planning/plans/ から Branch: {branch} の plan を読め
   2. task {task_number} の Schema / Tests / Ref test を確認しろ
   3. AGENTS.md の Implementation Skills テーブルから該当レイヤーのスキルファイルを読め
   4. TDD で実装しろ:
      a. Schema 定義
      b. テスト作成（RED）— plan の Ref test を読んで構造を踏襲
      c. 最小実装（GREEN）
   5. task check を実行して全チェック通過を確認
   6. .execlog/{branch}.md にエントリ追加（日時 JST / Task / Changed / Test / Next）
   7. plan の task {task_number} の checkbox を - [x] に更新
   8. git commit + git push
   9. この task が完了したら停止。次の task には絶対に進むな

   ref: AGENTS.md, SURVIVAL.md" 2>/dev/null
```

## Resume（修正指示）

`task check` 失敗やレビュー指摘を受けて修正させるとき。
前回セッションの文脈を `resume --last` で引き継ぐ。

```bash
pnpm codex exec resume --last --full-auto \
  -m gpt-5.4 \
  -c model_reasoning_effort=medium \
  "{修正内容}。修正して task check 通過後 commit + push しろ。" 2>/dev/null
```

## Post-check（Claude Code 側）

Codex 完了後、orchestrator が **必ず** 実施する検証ステップ:

1. `pnpm -r --filter @your-org/<package> test` 実行 — **全テスト pass を確認**
   - Codex sandbox は localhost DB に接続できないため、integration test は実行されていない前提で動くこと
   - 0 failures 以外は修正が必要
2. `task check` 実行（lint + typecheck + archgate + format）
3. `git log --oneline -3` — commit が作られたか確認
4. `.execlog/{branch}.md` の末尾 — エントリが追加されたか確認
5. plan の checkbox — `- [x]` に更新されたか確認
6. `git push` — Codex sandbox はネットワーク制限で push できないため、orchestrator が実行
7. いずれか失敗 → Resume を実行（最大2回リトライ）
8. 2回リトライしても解消しない → ユーザーに報告して判断を仰ぐ
