# Communication skills

Output-style skills that change how Claude writes responses, not what it does. Toggle on for a specific tone/density.

| Skill | Description |
|---|---|
| [`caveman`](skills/caveman/) | Ultra-compressed communication mode. Cuts token usage ~75% by dropping filler, articles, and pleasantries while keeping full technical accuracy. Use when user says "caveman mode", "talk like caveman", "use caveman", "less tokens", "be brief", or invokes /caveman. |
| [`zoom-out`](skills/zoom-out/) | Tell the agent to zoom out and give broader context or a higher-level perspective. Use when you're unfamiliar with a section of code or need to understand how it fits into the bigger picture. |

## Install just this plugin

```
/plugin marketplace add marzun9620/agent_skills
/plugin install communication@marzun9620-skills
```

_See the [repo README](../README.md) for the full picture._
