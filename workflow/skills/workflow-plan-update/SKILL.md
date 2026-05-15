---
name: workflow-plan-update
description: >
  Checkbox updates and status management for plan files (.planning/plans/).
  Update checkboxes as tasks complete; move the plan to done/ once all
  tasks are done.
  Triggers: plan update, task completion mark, checkbox,
  plan status, plan revision.
version: 1.0.0
---

# Plan 更新手順

`.planning/plans/{feature}.md` の状態を管理する。

## 1. Task 完了マーク

task が完了したら、plan ファイルのチェックボックスを更新:

```markdown
# Before
- [ ] 1. Schema.Class で Facility Entity を定義

# After
- [x] 1. Schema.Class で Facility Entity を定義
```

## 2. Status フィールド更新

plan ファイルの `Status:` 行を状態に応じて更新:

| 状態 | 意味 |
|------|------|
| `ready` | 作成済み、未着手 |
| `in-progress` | 実装中（最初の task 開始時） |
| `in-review` | PR 作成済み、レビュー待ち |
| `done` | マージ完了 |

## 3. Plan 完了時

全 task のチェックボックスが `[x]` になったら:

1. Status を `in-review` に更新（PR 作成前）
2. PR 作成後、Status を `in-review` のまま維持
3. マージ後、plan ファイルを `done/` に移動:

```bash
mv .planning/plans/{feature}.md .planning/plans/done/{feature}.md
```

Status を `done` に更新。

## ルール

- Status の遷移: `ready → in-progress → in-review → done`
- 逆方向の遷移はしない
- plan ファイル名はハイフン区切り（例: `facility-crud.md`）
