# Dev-process skills

Engineering-process skills that sit alongside coding: capturing decisions, diagnosing bugs systematically, and finding architecture-level refactor opportunities.

| Skill | Description |
|---|---|
| [`adr-drafter`](adr-drafter/) | A skill for interactively creating Architecture Decision Records (ADRs). Act as a world-class software architect, facilitating collaborative discussions with the user to explore technology choices and design decisions, then generate ADR documents. Use this skill whenever the user brings up topics like "ADR", "technology selection", "design decision", "architecture decision", "I'm torn between X and Y", "which technology should I use", or "I want to discuss whether this design is right". Also handles updating and deprecating existing ADRs. |
| [`diagnose`](diagnose/) | Disciplined diagnosis loop for hard bugs and performance regressions. Reproduce → minimise → hypothesise → instrument → fix → regression-test. Use when user says "diagnose this" / "debug this", reports a bug, says something is broken/throwing/failing, or describes a performance regression. |
| [`improve-codebase-architecture`](improve-codebase-architecture/) | Find deepening opportunities in a codebase, informed by the domain language in CONTEXT.md and the decisions in docs/adr/. Use when the user wants to improve architecture, find refactoring opportunities, consolidate tightly-coupled modules, or make a codebase more testable and AI-navigable. |

_See the [repo README](../README.md) for install instructions._
