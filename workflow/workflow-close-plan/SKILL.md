---
name: workflow-close-plan
description: >
  完了した plan を done/ に移動し、lessons learned を記録して commit + push する。
  /run 完了後や /review APPROVED 後に呼ぶ。
  トリガー: /close-plan, plan完了, planをdoneに, lessons記録
version: 1.0.0
user_invocable: true
---

# Close Plan — Plan 完了 + Lessons 記録

## Arguments

`/close-plan {plan-name-or-branch}` — plan ファイル名 or branch 名

## Protocol

### 1. Plan 特定
1. `.planning/plans/` から引数に一致する plan を探す（部分一致OK）
2. plan が見つからなければ `.planning/plans/done/` も確認（既に移動済みかもしれない）

### 2. Lessons 抽出
1. `.execlog/{branch}.md` を読む
2. 直近の /run セッションで発生した修正パターンを振り返る:
   - Codex review で出た Critical / Warning
   - post-check で直した integration test の失敗
   - Mode B review で指摘された cross-cutting issue
3. `.planning/lessons.md` を読み、既存の lessons と重複しないものだけを抽出
4. 新規 lessons を適切なセクションに追記:
   - 既存セクションに該当するものはそこに追加
   - 該当セクションがなければ新セクションを作成
   - 各 lesson は `- {rule}。Why: {reason}` のフォーマット

### 3. Plan 移動
1. Plan の Status を `done` に更新
2. Plan ファイルを `.planning/plans/done/` に移動

### 4. Commit + Push
```bash
git add .planning/plans/done/{plan}.md .planning/plans/{plan}.md .planning/lessons.md
git commit -m "chore: close {plan-name}, add lessons learned"
git push
```

## Rules

- lessons.md に重複する内容を追加しない
- lessons は将来の実装に役立つもののみ（一時的なバグ修正の詳細は不要）
- plan が既に done/ にある場合は lessons 追記のみ行う
