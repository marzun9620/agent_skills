# Contributing

Thanks for thinking about contributing. This is a personal collection of Claude Code skills I use day-to-day, but the goal is for anyone to pick up what's useful and contribute back what they've built. The bar is low — if it's useful to more than one project and isn't a thin SaaS wrapper, it probably fits.

A few conventions to keep the repo consistent:

1. **General applicability.** A skill should be useful to more than one project. Things tied to a specific repo, ADR, or internal stack belong in a private fork.
2. **English-first.** `description:` frontmatter must be in English so trigger-matching works for the broadest audience. Skill bodies can include other languages, but the description has to be readable to everyone.
3. **One job per skill.** If your skill is doing three things, split it. Each `SKILL.md` should be invocable on its own.
4. **Concise.** Skill bodies stay loaded in context, so every line is a recurring token cost. Aim for under ~500 lines. Move long reference material into sibling files and link to them — those are loaded on demand.

## How to add a skill

1. Fork the repo.
2. Pick the category folder it belongs in (`effect-ts/`, `testing/`, etc.) — or create a new one if nothing fits.
3. Create your skill under that category's `skills/` subdirectory:

   ```
   <category>/skills/<your-skill-name>/SKILL.md
   ```

4. Use the `_template/SKILL.md` as a starting point. Required frontmatter: `description`. See [Anthropic's frontmatter reference](https://code.claude.com/docs/en/skills#frontmatter-reference) for optional fields.
5. Test it locally:

   ```bash
   ./install.sh <your-skill-name>
   # then open Claude Code in any project and type /<your-skill-name>
   ```

6. Run the validator (same one CI runs):

   ```bash
   pip install pyyaml          # one-time
   ./scripts/validate.py
   ```

   It checks frontmatter, JSON manifests, plugin-source paths, NOTICE.md attribution, naming conventions, description length, body size, and that `install.sh` discovers your skill. CI runs this on every PR and **blocks the merge** if it fails.

7. Open a PR with a short summary of what the skill does and why it's general-purpose.

## How to fix or improve an existing skill

PRs welcome. Keep the change focused — one skill per PR if possible. Tweaks to `description:` wording, adding trigger phrases, fixing factual errors, and adding examples are all good.

## Style

- Lowercase, hyphenated skill names (`my-skill`, not `MySkill` or `my_skill`).
- Put the most important use case first in `description:` — Anthropic truncates at 1,536 chars and trims from the end.
- Don't write multi-paragraph preambles in `SKILL.md` bodies. State what to do, link to references for the rest.

## What gets rejected

- Skills tied to a single private codebase.
- Skills that duplicate something already in the repo without a clear improvement.
- Anything that publishes secrets, customer data, or other content that wasn't yours to share.
- Marketing or self-promotional skills.

If you're unsure whether your skill is a good fit, open an issue first — happy to discuss before you write it.
