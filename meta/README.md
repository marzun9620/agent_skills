# Meta skills

Skills about skills — finding existing skills, authoring new ones, and bootstrapping a curated personal set.

| Skill | Description |
|---|---|
| [`find-skills`](skills/find-skills/) | Helps users discover and install agent skills when they ask questions like "how do I do X", "find a skill for X", "is there a skill that can...", or express interest in extending capabilities. This skill should be used when the user is looking for functionality that might exist as an installable skill. |
| [`prompt-refinement`](skills/prompt-refinement/) | Refines a rough instruction into a structured Agent Task Prompt before another agent executes. Use when the user is about to delegate work to a subagent, Codex CLI, Cursor, or another coding agent and wants a clear, complete brief with goal, context, files to inspect, constraints, deliverables, verification, and edge cases. Triggers - "/refine", "refine this prompt", "make this prompt better", "brief an agent", "structure this before running", "improve my instruction". |
| [`skill-router`](skills/skill-router/) | You MUST use this at the start of EVERY task the user describes. Identifies which installed Claude Code skill(s) best fit the user's task, surfaces the top match with reasoning, and if no skill matches with confidence, proposes a new skill (name + draft description) and scaffolds it via write-a-skill. Triggers - ANY task or work request, "which skill should I use", "is there a skill for", "do you have a skill that", "help me find the right skill", "how do I do X", "I want to", "I need to", "can you", "/skill-router", "/which-skill", "/route". |
| [`setup-matt-pocock-skills`](skills/setup-matt-pocock-skills/) | Sets up an `## Agent skills` block in AGENTS.md/CLAUDE.md and `docs/agents/` so the engineering skills know this repo's issue tracker (GitHub or local markdown), triage label vocabulary, and domain doc layout. Run before first use of `to-issues`, `to-prd`, `triage`, `diagnose`, `tdd`, `improve-codebase-architecture`, or `zoom-out` — or if those skills appear to be missing context about the issue tracker, triage labels, or domain docs. |
| [`write-a-skill`](skills/write-a-skill/) | Create new agent skills with proper structure, progressive disclosure, and bundled resources. Use when user wants to create, write, or build a new skill. |

## Install just this plugin

```
/plugin marketplace add marzun9620/agent_skills
/plugin install meta@marzun9620-skills
```

_See the [repo README](../README.md) for the full picture._
