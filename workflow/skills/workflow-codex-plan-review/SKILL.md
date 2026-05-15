---
name: workflow-codex-plan-review
description: >
  Delegate plan review to Codex CLI. Detects critical issues before showing
  the plan to the user. Iterative Initial Review + Re-review (resume --last)
  pattern; up to 5 loops.
  Triggers: /plan review, Codex plan review, plan quality check.
version: 1.0.0
---

# Codex Plan Review — プランレビュー

Claude Code（orchestrator）が `/plan` で作成した plan を、ユーザーに提示する前に
Codex にレビューさせるためのスキル。致命的な問題だけを指摘させ、瑣末な点は無視させる。

## When to use

`/plan` コマンドの Step 5（ユーザー提示前レビュー）および Step 7（ユーザー修正後の再レビュー）。

---

## Initial Review

plan を新規作成した直後、ユーザーに見せる前に実施。

```bash
pnpm codex exec \
  -m gpt-5.4 \
  -c model_reasoning_effort=medium \
  "このプランをレビューして。瑣末な点へのクソリプはしないで。致命的な点だけ指摘して: \
   .planning/plans/{feature}.md

   レビュー観点:
   - docs/adr/ の ADR に抵触する部分はないか
   - docs/product-specs/ の仕様に抵触する部分はないか
   - テストでカバーできていないユースケースはないか
   - DDD 的な観点で better にできる箇所はあるか
   - DRY / KISS 的な観点で修正すべき箇所はあるか
   - .claude/skills/workflow/ のスキルパターンに沿っているか

   ref: CLAUDE.md" 2>/dev/null
```

---

## Re-review（修正後）

指摘を反映した後、前回セッションの文脈を引き継いで再レビュー。

```bash
pnpm codex exec resume --last \
  -m gpt-5.4 \
  -c model_reasoning_effort=medium \
  "プランを更新したからレビューして。瑣末な点へのクソリプはしないで。致命的な点だけ指摘して: \
   .planning/plans/{feature}.md

   ref: CLAUDE.md" 2>/dev/null
```

---

## ループ制御（Claude Code 側）

Codex の指摘と plan 修正を繰り返すフロー:

1. Initial Review を実行
2. 致命的な指摘があれば → plan を修正 → Re-review
3. 指摘が消えるまで **最大5回** ループ
4. 5回で解消しない場合:
   - 残っている指摘をユーザーに提示
   - ユーザーの判断を仰ぐ（無視して進める or 追加修正）
5. 指摘なし or ユーザー承認 → plan をユーザーに提示

### ユーザー修正後の再レビュー

ユーザーが plan に修正を入れた後も、同じループを実施する:
1. Re-review を実行（`resume --last` で文脈引き継ぎ）
2. 致命的指摘 → 修正 → Re-review（最大5回）
3. 解消 → 完了
