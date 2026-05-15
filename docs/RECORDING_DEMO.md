# Recording the README demo GIF

The README has a placeholder for `docs/demo.gif`. Recording a real one is the single highest-impact polish for star conversion — research consistently finds a screencap or GIF in the README outperforms badge walls for first-time visitors.

## What to capture (~15 seconds)

1. Inside a real Claude Code session in any project
2. Type `/plugin marketplace add marzun9620/agent_skills` — show the catalogue appearing
3. Type `/plugin install dev-process@marzun9620-skills`
4. Then ask Claude something natural like _"Help me diagnose why our login flow started failing yesterday"_ and show the `diagnose` skill auto-loading

The point of the GIF: a stranger should understand in 15 seconds what installing a plugin from this repo *does*.

## Tools

- **macOS**: [Kap](https://getkap.co/) (free, simple), or QuickTime → record screen → export → convert to GIF with `ffmpeg`
- **Linux/Windows**: [Peek](https://github.com/phw/peek) or [LICEcap](https://www.cockos.com/licecap/)
- **Terminal-only**: [vhs](https://github.com/charmbracelet/vhs) for scripted recordings

## Targets

- Size: under 5 MB (GitHub renders it inline; larger files load slowly)
- Resolution: 1280×720 or smaller
- Loop: yes
- Duration: 12–20 seconds

## After recording

1. Save as `docs/demo.gif`
2. In `README.md`, uncomment the lines:
   ```html
   <!-- ![demo](docs/demo.gif) -->
   ```
3. Commit + push.

That's it. The GIF starts working the moment the README references it; no extra config needed.
