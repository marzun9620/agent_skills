# Design skills

Architecture-shaping skills for the layers above plain CRUD: domain modeling (DDD building blocks with Effect Schema) and frontend component design (Feature-Sliced Design).

| Skill | Description |
|---|---|
| [`domain-design`](skills/domain-design/) | Generate DDD building blocks (ValueObject, Error, Aggregate) using Effect + Schema. Use when creating new domain types, defining custom errors, or modeling aggregate lifecycles with invariant enforcement. |
| [`frontend-design`](skills/frontend-design/) | Generate Feature-Sliced Design (FSD) components. Use when creating pages, features, entities, widgets, or shared modules following FSD architecture with React Router v7 + Effect + Tailwind CSS. |

## Install just this plugin

```
/plugin marketplace add marzun9620/agent_skills
/plugin install design@marzun9620-skills
```

_See the [repo README](../README.md) for the full picture._
