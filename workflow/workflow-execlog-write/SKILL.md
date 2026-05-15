---
name: workflow-execlog-write
description: >
  実行ログ（.execlog/）への記録手順。各 task 完了後にエントリ追加。
  Final Handoff エントリは plan 完了時。
  トリガー: execlog、実行ログ、進捗記録、タスク完了記録、
  night-run ログ、handoff
version: 1.0.0
---

# 実行ログ記録手順

`.execlog/{branch}.md` に各 task の完了記録を追記する。

## 1. Task 完了エントリ

各 task 完了後に以下を `.execlog/{branch}.md` に追記:

```markdown
## [YYYY-MM-DD HH:MM JST]
**Task:** {task description from plan}
**Changed:** {changed files, comma-separated}
**Test:** PASS
**Next:** {next task description, or "Final Handoff"}
```

- 日時は JST（日本標準時）
- **Test** は `task check` の結果（PASS/FAIL）
- FAIL の場合は修正してから記録（FAIL のまま進めない）

## 2. Final Handoff エントリ

plan 内の全 task 完了後に追記:

```markdown
## Final Handoff
**Completed:** {list of all completed tasks}
**Test status:** all passing
**Risks:** {remaining concerns, or "none"}
**Review:** {key files for reviewer to check}
```

## 3. ファイルが存在しない場合

新規作成。ヘッダーを追加:

```markdown
# Execution Log: {branch-name}

## [YYYY-MM-DD HH:MM JST]
...
```

## ルール

- エントリは追記のみ（既存エントリを編集しない）
- compaction/restart 後はこのログの末尾を読んで再開位置を特定する
- branch 名はハイフン区切り（例: `dh-facility-crud`）
