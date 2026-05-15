---
name: workflow-pr-create
description: >
  PR creation flow. Verify all task checks pass, then create the PR with
  `gh pr create`. If the plan has a Linear ID, update Linear too.
  Triggers: PR creation, pull request, ship, gh pr create,
  merge request, code review request.
version: 1.0.0
---

# PR 作成手順

`task check` 通過 → PR 作成 → Linear 更新。

## 1. 品質ゲート確認

```bash
task check
```

いずれかが失敗したら修正してから PR 作成。PR に失敗を含めない。

## 2. 変更内容の確認

```bash
git diff main...HEAD --stat
```

## 3. PR 作成

```bash
gh pr create \
  --title "{concise description, max 70 chars}" \
  --body "$(cat <<'EOF'
## Summary
{bullet points of changes}

## Test
- `task check`: PASS (lint + typecheck + test + archgate)

Linear: {ID or "N/A"}
EOF
)"
```

- タイトルは 70 文字以内
- Summary はバレットポイント
- Test セクションに `task check` の結果を記載
- Linear ID があれば記載

## 4. Linear 更新（Linear ID がある場合）

Plan に Linear ID が記載されている場合:
- Status を "In Review" に更新

## 5. Plan 更新

- plan-update skill で Status を `in-review` に更新

## ルール

- `task check` が全通過するまで PR を作成しない
- main にpush しない（PR 経由のみ）
- force push しない
