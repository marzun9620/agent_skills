---
name: skill-router
description: You MUST use this at the start of EVERY task the user describes. Identifies which installed Claude Code skill(s) best fit the user's task, surfaces the top match with reasoning, and if no skill matches with confidence, proposes a new skill (name + draft description) and scaffolds it via write-a-skill. Triggers - ANY task or work request, "which skill should I use", "is there a skill for", "do you have a skill that", "help me find the right skill", "how do I do X", "I want to", "I need to", "can you", "/skill-router", "/which-skill", "/route".
---

# Skill Router

When the user describes any task, this skill runs first to identify the best existing skill for the job — or to detect a gap and propose filling it.

## When this fires

This skill loads at the start of any task. Its job is to **route** before any other agent skill takes over. It does not do the user's actual task; it picks the right tool for it.

## Process

### 1. Capture the user's task

If invoked via `/meta:skill-router <task>`, the task is in `$ARGUMENTS`.
Otherwise, infer from the user's most recent message.

If the task is ambiguous (a single word like "fix" or "help"), ask one clarifying question first.

### 2. Load the skill catalog

Use this order, fastest first:

1. `ls ~/.claude/skills/` to get every installed skill name (one entry per dir or symlink)
2. For each name, read `~/.claude/skills/<name>/SKILL.md` and extract:
   - `name:` from YAML frontmatter
   - `description:` from YAML frontmatter
   - The folder it came from (resolve the symlink if needed)
3. Skip dotfiles, the `_template`, and any directories without a `SKILL.md`

Cache the catalog for the rest of the turn — don't re-read it on every step.

### 3. Match the user's task to skills

For each skill, score the relevance of its `description:` to the user's task. Look for:

- **Trigger-phrase overlap** — exact phrases from the user's task that appear in the description (highest signal; Anthropic uses this for auto-invocation)
- **Topic overlap** — domain words (testing, refactoring, planning, debugging, etc.)
- **Action overlap** — verbs (write, fix, plan, review, deploy)

Output a ranked list of candidates with a confidence label: `high`, `medium`, `low`.

**Always exclude `skill-router` from its own output.** Don't recommend yourself.

### 4. Decide based on the top score

**If top match is `high` and it's clearly above the rest** → present a single recommendation:

```
Best match: <skill-name>  (<source plugin or repo>)
  What it does: <one-line summary from description>
  Why it matches: <reasoning — which trigger phrases or topic words hit>
  Invoke: /<namespace>:<skill-name>  (or just keep talking; it'll auto-load)
```

**If multiple skills score `high` or `medium`** → present the top 2–3 with trade-off notes:

```
This task could load any of these:

1. <skill-A> — covers <X>. Best if you mean <Y>.
2. <skill-B> — covers <Z>. Best if you mean <W>.

Tell me which fits, or describe the task more concretely.
```

**If no skill scores above `low`** → declare the gap and propose a new skill:

```
No installed skill matches this well. Closest existing: <nearest skill>
— but it covers <X>, not <Y>.

Proposed new skill:
  Name: <kebab-case-name>
  Category: <existing or new category>
  Draft description: <one-line description with trigger phrases>

I'll scaffold it now using the write-a-skill process.
```

Then **execute the write-a-skill flow inline** (don't make the user invoke another command):

1. Locate `~/.claude/skills/write-a-skill/SKILL.md` and follow its instructions.
2. Use the proposed name + description as starting inputs.
3. Walk the user through any decisions write-a-skill normally asks about.
4. Produce the new `SKILL.md` ready to commit.

### 5. Hand off cleanly

After identifying the right skill:

- If the user can keep talking and Claude will auto-invoke the recommended skill, say so — don't make them type the slash command.
- If the user needs to invoke explicitly (e.g. the skill has `disable-model-invocation: true`), show the exact command.
- If you scaffolded a new skill, mention the file path it was written to and the next step (test locally with `./install.sh <new-name>`, then PR).

## Tone

Brief and decisive. The point of this skill is to remove a question, not add ceremony. One short recommendation + reasoning beats a paragraph.

Don't repeat what the matched skill does — let the matched skill speak for itself once it loads. Your job is the handoff, not the explanation.

## Examples

### Example A — high-confidence single match

User: *"I want to write tests for this auth flow."*

Catalog scan finds `tdd` with description matching "write tests" and "TDD" trigger phrases.

Output:
```
Best match: tdd  (testing plugin)
  Test-driven development with red-green-refactor loop.
  Why: matches "write tests" trigger + general TDD topic.
  Just keep talking — tdd will load automatically.
```

### Example B — multiple matches

User: *"Help me debug this performance regression."*

Catalog scan finds both `diagnose` and `tdd` (regression tests).

Output:
```
Two skills could apply:

1. diagnose (dev-process) — disciplined diagnosis loop (reproduce → minimise → hypothesise → instrument → fix → regression-test). Best if you don't yet know what's wrong.
2. tdd (testing) — write a regression test that fails first, then fix. Best if you already know roughly where the bug is.

Which fits the situation?
```

### Example C — no match

User: *"Set up a Terraform module for our staging environment."*

Catalog scan returns no skill with matching trigger phrases.

Output:
```
No installed skill matches Terraform / infra-as-code work.
Closest existing: dev-process:adr-drafter (could document the decision, but doesn't generate Terraform).

Proposed new skill:
  Name: terraform-module
  Category: dev-process (or new infra/ category)
  Draft description: Scaffolds a Terraform module with standard variables, outputs, README, and pre-commit checks. Use when the user says "set up Terraform for X", "create a TF module", "infra for staging/prod", or asks for IaC patterns.

I'll scaffold it now via write-a-skill — answering its prompts using the proposal above as defaults. You'll review the result before commit.
```

Then run write-a-skill's process inline.

## Edge cases

- **Self-reference**: if the user asks "what helps me find skills?", `find-skills` and `skill-router` are both candidates. Show `find-skills` (the answer), not `skill-router` (this skill is the asker, not the answer).
- **Task needs multiple skills sequentially** (e.g. "refactor this and write tests"): recommend invoking them in order, not pretending one covers both.
- **User invoked another skill explicitly first**: don't override. If they typed `/dev-process:diagnose ...`, they made the routing decision; step aside.
- **Skill matches but isn't installed locally**: still surface it, with the exact install command. Don't hide useful options.
- **Tied confidence across skills from different sources** (this repo vs `~/.agents/skills/` symlinks vs plugin marketplaces): break the tie toward whatever the user has touched recently (`git log` or symlink mtime).

## What this skill is NOT

- It is not `find-skills`. `find-skills` searches the **open ecosystem** (skills.sh, awesome-claude-skills lists, third-party repos). `skill-router` matches against **what's installed locally**.
- It is not `prompt-refinement`. `prompt-refinement` rewrites a vague instruction into a structured Agent Task Prompt for delegation. `skill-router` decides which skill should handle a task in the first place.
- It is not `write-a-skill`. `write-a-skill` scaffolds a new skill from a brief. `skill-router` invokes `write-a-skill` only as a fallback when no existing skill fits.
