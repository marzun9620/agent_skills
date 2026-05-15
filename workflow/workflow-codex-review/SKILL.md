---
name: workflow-codex-review
description: >
  Codex CLI にコードレビューを委譲するスキル。read-only sandbox で実行。
  Mode A: per-task review（git diff HEAD~1）、Mode B: PR review（gh pr diff）。
  トリガー: /run レビュー、/review、Codex レビュー委譲、コードレビュー
version: 1.0.0
---

# Codex Review — コードレビュー

Claude Code（orchestrator）が Codex にコードレビューを委譲するためのスキル。
`--sandbox read-only` で起動するため、Codex はファイルを変更できず指摘のみ行う。

## When to use

- `/run` の Per-Task Loop で、実装済み task の commit をレビューするとき → **Mode A**
- `/review` で PR 全体をレビューするとき → **Mode B**

---

## Mode A: Per-Task Review

直前の commit（1 task 分）をレビューする。`/run` の Per-Task Loop 内で使用。

```bash
pnpm codex exec --sandbox read-only \
  -m gpt-5.4 \
  -c model_reasoning_effort=medium \
  "直前の commit をレビューして。

   staff engineer として以下の観点でレビューしろ:
   1. git diff HEAD~1 で差分を取得しろ
   2. docs/adr/ の ADR に抵触する部分はないか
   3. docs/product-specs/ の仕様に抵触する部分はないか
   4. テストでカバーできていないユースケースはないか
   5. DDD 的な観点で better にできる箇所はあるか
   6. DRY / KISS 的な観点で修正すべき箇所はあるか
   7. .claude/skills/workflow/ の effect-ts skill パターンに沿っているか
   8. 以下のフォーマットで報告しろ:

   ## Review Result
   ### Critical（修正必須）
   - {issue}: {説明} → {修正コード or 修正方針}

   ### Warning（改善推奨）
   - {issue}: {説明}

   ### Info（参考）
   - {issue}: {説明}

   ### Verdict
   APPROVED / REVISE

   critical も warning もなければ APPROVED。1つでもあれば REVISE。
   Warning も修正対象として扱え。PR コメントに残して放置するな。

   ref: AGENTS.md, docs/adr/, docs/product-specs/" 2>/dev/null
```

---

## Mode B: PR Review

PR 全体の差分をレビューする。`/review` コマンドで使用。

```bash
pnpm codex exec --sandbox read-only \
  -m gpt-5.4 \
  -c model_reasoning_effort=medium \
  "PR {pr_number} をレビューして。

   staff engineer として以下の観点でレビューしろ:
   1. gh pr diff {pr_number} で差分を取得しろ（失敗したら git diff main...HEAD を使え）
   2. docs/adr/ の ADR に抵触する部分はないか
   3. docs/product-specs/ の仕様に抵触する部分はないか
   4. テストでカバーできていないユースケースはないか
   5. DDD 的な観点で better にできる箇所はあるか
   6. DRY / KISS 的な観点で修正すべき箇所はあるか
   7. .claude/skills/workflow/ の effect-ts skill パターンに沿っているか
   8. 以下のフォーマットで報告しろ:

   ## Review Result
   ### Critical（修正必須）
   - {issue}: {説明} → {修正コード or 修正方針}

   ### Warning（改善推奨だが修正必須）
   - {issue}: {説明} → {修正コード or 修正方針}

   ### Info（参考）
   - {issue}: {説明}

   ### Verdict
   APPROVED / REVISE

   critical も warning もなければ APPROVED。1つでもあれば REVISE。
   Warning も修正対象として扱え。PR コメントに残して放置するな。

   ref: AGENTS.md, docs/adr/, docs/product-specs/" 2>/dev/null
```

---

## 結果の処理（Claude Code 側）

Codex のレビュー出力を読み、Critical / Warning の有無に応じて分岐する:

### Critical または Warning あり → 修正ループ
1. Critical + Warning issues を全て抽出
2. **codex-implement skill の Resume** で修正を指示:
   - 「レビューで以下の issues が見つかった: {issues}。全て修正して task check 通過後 commit + push しろ。」
3. orchestrator が post-check（テスト実行 + task check）を実施
4. 修正後、再度レビュー（Mode A or B）を実行
5. Critical / Warning が消えるまでループ（最大5回）
6. 5回で解消しない → ユーザーに報告して判断を仰ぐ

**Warning を PR コメントに残して放置しない。** Warning も修正対象として扱うこと。

### Critical も Warning もなし → APPROVED
1. 次の task へ進む（`/run`）、またはサマリー報告（`/review`）

### Verdict の判定基準変更
- Critical **または** Warning が 1 つでもあれば → REVISE
- Critical も Warning もなし → APPROVED
