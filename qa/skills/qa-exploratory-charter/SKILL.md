---
name: qa-exploratory-charter
description: Writes a Session-Based Test Management (SBTM) charter for an exploratory testing session — mission, areas, tactics (heuristics + attacks), time-box, oracle, setup data, and PROOF debrief template. Use when the user says "exploratory testing", "exploratory charter", "session-based testing", "SBTM", "exploratory test session for", or wants to design a focused exploration session for a feature.
---

# QA Exploratory Charter (SBTM)

Produce a Session-Based Test Management charter that guides 60–120 minutes of focused exploratory testing. The charter is a guardrail, not a script — the tester improvises within it.

## Process

### 1. Pick a clear mission

A charter has one mission. If the user wants to explore two unrelated areas, write two charters.

Mission template: **"Explore `<area>` with `<tactics>` to discover `<information>`."**

Example:
> *"Explore the CSV export with attacks on data shape (empty, 1M rows, special characters, multilingual) and concurrent download conditions to discover failures in download integrity, performance regressions, and UI feedback gaps."*

### 2. Produce the charter in this format

```md
# Exploratory Charter: <one-line mission summary>

## Mission
<Full mission statement using the template above>

## Areas
- **Primary**: <the feature/surface under exploration>
- **Adjacent**: <related areas that share state or could regress>
- **Out of scope**: <explicitly excluded — keeps the session focused>

## Tactics (test ideas)
Group by heuristic. Pick 3–6 heuristics relevant to the mission.

**Boundary attacks**: <ideas>
**State attacks**: <ideas — interrupt, refresh mid-action, navigate away>
**Error guessing**: <ideas based on similar bugs seen elsewhere>
**Combination**: <ideas combining inputs that may interact>
**Resource attacks**: <ideas — slow network, offline, low memory>
**Concurrency**: <ideas — two users, two tabs, two sessions>
**Time-based**: <ideas — clock change, timezone, DST, leap second>

Drop heuristics that don't apply. Add domain-specific ones.

## Oracles (how you'll know it's broken)
- <Spec or AC says X — anything else is a fault>
- <Existing user behaviour Y — regression>
- <Similar feature Z does it differently — inconsistency worth flagging>
- <Common sense: data loss, security exposure, performance regression > 2x>

## Setup
- **Environment**: <staging URL, branch deployed, build hash>
- **Test data**: <accounts, fixtures, seed data needed>
- **Tools open**: <browser devtools, network capture, log tail command, screen recorder>
- **Reset procedure**: <how to return to a known state between attacks>

## Time-box
- Mission start: __:__
- Mission end (planned): __:__  (typically +60 to +120 min)
- Hard stop if: <condition that ends the session early — e.g. critical bug found and reproduced>

## Debrief — PROOF
Fill in immediately after the session.

**P — Past activities** (what you did)
- <bullet list of attacks you actually ran — not what you planned, what you ran>

**R — Results** (what you found)
- <bug-like behaviours, with severity rough cut>
- <surprising-but-not-bug observations>

**O — Obstacles** (what slowed you down)
- <env issues, data setup issues, missing tooling, spec ambiguities>

**O — Outlook** (what to do next)
- <follow-up charters needed>
- <bugs to file via qa-bug-report>
- <test cases to add to the regression suite>
- <questions for PM / dev>

**F — Feelings** (what your gut tells you)
- <confidence level in this area: Low / Medium / High>
- <hunches about where more bugs are hiding>
- <user-experience concerns that aren't bugs but feel wrong>
```

### 3. Apply SBTM principles

- **Time-box matters.** Sessions ≥ 2 hours degrade attention. If the area needs more, write multiple charters.
- **No checklist.** A charter lists *ideas*, not *steps*. The tester explores based on what they find.
- **Debrief is mandatory.** A session without PROOF debrief produces nothing useful for the next person.
- **One mission per charter.** "Test everything about CSV export" is too broad — split into "explore CSV data integrity" and "explore CSV download UX" if both matter.

## Worked example

**Input**: *"Help me explore the new CSV export feature for any issues."*

**Output charter excerpt** (just the Mission + Tactics):

> **Mission**: Explore the CSV export with attacks on data shape (empty, large, special-char, multilingual) and timing (slow network, concurrent downloads, mid-download navigation) to discover failures in download integrity, performance under load, and UI feedback gaps.
>
> **Tactics**:
> - *Boundary attacks*: empty dataset, 1 row, ~10K rows, ~1M rows, dataset that exceeds memory.
> - *Content attacks*: emoji, RTL languages, CSV special chars (`,`, `"`, `\n`), SQL-injection-shaped strings (verify properly escaped), nulls.
> - *State attacks*: navigate away mid-download, refresh tab, browser back, close laptop and reopen.
> - *Concurrency*: two browser tabs both downloading; two users downloading the same query.
> - *Resource*: Chrome DevTools throttling to 3G; offline after initiating download.
> - *Time-based*: cross-DST boundary (if dates in export); leap year.

## Anti-patterns to avoid

- Charter that reads like a test script (numbered steps with expected results). That's a test case, not a charter.
- No oracle. Without an oracle, the tester can't tell what's a bug.
- Mission too broad ("test the whole app"). Charters are sessions, not phases.
- Skipping the debrief. The value of SBTM is the debrief, not the session itself.
- Filing bugs inside the charter. Bugs go through `qa-bug-report` and are linked back to the charter's "Results" section.
