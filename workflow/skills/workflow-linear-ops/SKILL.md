---
name: workflow-linear-ops
description: >
  Linear issue operations using @schpet/linear-cli — status updates,
  adding comments, PR linking.
  Triggers: Linear, issue update, status change, linear-comment,
  linear-update, progress report, In Review.
version: 1.0.0
---

# Linear 操作手順

`@schpet/linear-cli` を使って Linear issue を操作する。

## セットアップ

```bash
# インストール（pnpm devDependency）
pnpm add -D @schpet/linear-cli

# 認証（初回のみ）
npx linear auth login

# プロジェクト設定（初回のみ）
npx linear config
```

## タスク完了時のコメント追加

plan の各 task 完了後に Linear issue にコメントを追加:

```bash
npx linear issue comment add --issue {ISSUE_ID} --body "✅ {task description}"
```

例:
```bash
npx linear issue comment add --issue HW-42 --body "✅ Facility Entity を Schema.Class で定義"
```

## ステータス更新

plan 全体の完了時にステータスを更新:

```bash
# 実装完了 → レビュー待ち
npx linear issue update {ISSUE_ID} --status "In Review"

# マージ後
npx linear issue update {ISSUE_ID} --status "Done"
```

## Issue 参照

```bash
# 現在のブランチに紐づく issue を表示
npx linear issue view

# issue の詳細
npx linear issue view {ISSUE_ID}

# 自分にアサインされた未着手 issue 一覧
npx linear issue list
```

## PR 連携

```bash
# Linear issue から GitHub PR を作成
npx linear issue pr
```

## /run command での使い方

1. plan に `Linear: HW-42` と記載されていれば連携対象
2. 各 task 完了時: `npx linear issue comment add` で進捗報告
3. plan 全完了時: `npx linear issue update --status "In Review"`
4. PR body に `Linear: HW-42` を記載

## plan に Linear ID がない場合

Linear 連携をスキップ。コメント追加もステータス更新も行わない。
