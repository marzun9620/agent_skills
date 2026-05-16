#!/usr/bin/env python3
"""
CI validator for marzun9620/agent_skills.

Tier 1 (critical):
  - marketplace.json + every plugin.json is valid JSON
  - every SKILL.md has parseable YAML frontmatter
  - every SKILL.md has a non-empty `description:` field
  - every plugin source path in marketplace.json resolves to a directory with
    .claude-plugin/plugin.json and a skills/ subdirectory
  - SKILL.md name field (if present) matches its containing directory name

Tier 2 (quality):
  - description ≤ 1536 chars (Anthropic's truncation limit)
  - SKILL.md body < 500 lines (CONTRIBUTING.md rule)
  - skill directory names are lowercase-kebab-case
  - every plugin in marketplace.json is mentioned in NOTICE.md
  - install.sh --list discovers every SKILL.md (and nothing else)

Exit code 0 on all-pass, 1 on any failure. Designed to be run locally too:

    ./scripts/validate.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("missing dependency: pyyaml. run `pip install pyyaml`.", file=sys.stderr)
    sys.exit(2)


REPO = Path(__file__).resolve().parent.parent
ERRORS: list[str] = []

KEBAB_RE = re.compile(r"^[a-z][a-z0-9-]*$")
DESC_CHAR_LIMIT = 1536
BODY_LINE_LIMIT = 500

# Skills that legitimately exceed BODY_LINE_LIMIT. These are upstream content
# (Andrue Anderson's effect-ts skills, the original Japanese playwright-test)
# that we redistribute as-is per their MIT licenses; we don't modify them to
# fit our internal style rule. Add a new entry only after considering whether
# a long skill should be split or moved to a sibling reference file instead.
LARGE_BODY_EXCEPTIONS: set[str] = {
    "effect-ts-code-style",
    "effect-ts-pattern-matching",
    "effect-ts-schema",
    "effect-ts-testing",
    "playwright-test",
}


def err(msg: str) -> None:
    ERRORS.append(msg)


def find_skills() -> list[tuple[Path, str]]:
    """Return (skill_dir, skill_name) for every SKILL.md, skipping _-prefixed and .git paths."""
    skills: list[tuple[Path, str]] = []
    for skill_md in REPO.rglob("SKILL.md"):
        rel_parents = skill_md.relative_to(REPO).parents
        if any(p.name.startswith("_") or p.name == ".git" for p in rel_parents):
            continue
        if skill_md.parent == REPO:
            # _template/SKILL.md is excluded above; this catches anything else
            # accidentally at root that we don't want treated as a skill.
            continue
        skills.append((skill_md.parent, skill_md.parent.name))
    return sorted(skills, key=lambda x: x[1])


def parse_frontmatter(text: str) -> tuple[dict | None, str | None]:
    if not text.startswith("---"):
        return None, "no leading ---"
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, "no closing ---"
    try:
        meta = yaml.safe_load(parts[1])
        return (meta or {}), None
    except yaml.YAMLError as e:
        return None, f"YAML parse error: {e}"


# ---------- Tier 1 ----------


def check_json_files() -> None:
    """marketplace.json + every plugin.json must be valid JSON."""
    paths: list[Path] = [REPO / ".claude-plugin/marketplace.json"]
    paths.extend(REPO.rglob(".claude-plugin/plugin.json"))
    for path in paths:
        rel = path.relative_to(REPO)
        if not path.exists():
            err(f"MISSING JSON: {rel}")
            continue
        try:
            json.loads(path.read_text())
        except json.JSONDecodeError as e:
            err(f"INVALID JSON: {rel}: {e}")


def check_skills_tier1(skills: list[tuple[Path, str]]) -> None:
    """Frontmatter parses, has description, name matches directory."""
    for skill_dir, skill_name in skills:
        skill_md = skill_dir / "SKILL.md"
        rel = skill_md.relative_to(REPO)
        text = skill_md.read_text()

        meta, parse_err = parse_frontmatter(text)
        if parse_err:
            err(f"FRONTMATTER {rel}: {parse_err}")
            continue

        desc = meta.get("description")
        if not desc:
            err(f"FRONTMATTER {rel}: missing required 'description'")

        name_field = meta.get("name")
        if name_field and name_field != skill_name:
            err(
                f"NAME MISMATCH {rel}: frontmatter name='{name_field}' "
                f"but directory is '{skill_name}'"
            )


def check_marketplace() -> None:
    """Every plugin source path resolves to a real plugin directory."""
    mkt_path = REPO / ".claude-plugin/marketplace.json"
    if not mkt_path.exists():
        return  # already reported by check_json_files
    try:
        mkt = json.loads(mkt_path.read_text())
    except json.JSONDecodeError:
        return  # already reported

    for plugin in mkt.get("plugins", []):
        name = plugin.get("name", "<unnamed>")
        source = plugin.get("source")

        if isinstance(source, str):
            path = (REPO / source).resolve()
        elif isinstance(source, dict):
            # External git source — skip filesystem check
            continue
        else:
            err(f"MARKETPLACE plugin '{name}': unrecognized source format")
            continue

        if not path.is_dir():
            err(f"MARKETPLACE plugin '{name}': source path '{source}' not a directory")
            continue
        if not (path / ".claude-plugin/plugin.json").exists():
            err(f"MARKETPLACE plugin '{name}': missing .claude-plugin/plugin.json at {source}")
        if not (path / "skills").is_dir():
            err(f"MARKETPLACE plugin '{name}': missing skills/ subdir at {source}")


# ---------- Tier 2 ----------


def check_skills_tier2(skills: list[tuple[Path, str]]) -> None:
    """Description length, body size, lowercase-kebab name."""
    for skill_dir, skill_name in skills:
        skill_md = skill_dir / "SKILL.md"
        rel = skill_md.relative_to(REPO)
        text = skill_md.read_text()

        if not KEBAB_RE.match(skill_name):
            err(f"NAME NOT KEBAB-CASE: '{skill_name}' (must match {KEBAB_RE.pattern})")

        meta, parse_err = parse_frontmatter(text)
        if parse_err:
            continue  # already reported by tier 1

        desc = meta.get("description", "")
        if isinstance(desc, str) and len(desc) > DESC_CHAR_LIMIT:
            err(f"DESC TOO LONG {rel}: {len(desc)} chars > {DESC_CHAR_LIMIT}")

        line_count = text.count("\n") + (0 if text.endswith("\n") else 1)
        if line_count > BODY_LINE_LIMIT and skill_name not in LARGE_BODY_EXCEPTIONS:
            err(
                f"BODY TOO LONG {rel}: {line_count} lines > {BODY_LINE_LIMIT}. "
                f"Either split the skill or add '{skill_name}' to "
                f"LARGE_BODY_EXCEPTIONS in scripts/validate.py with a comment "
                f"explaining why."
            )


def check_notice() -> None:
    """NOTICE.md must mention every plugin name."""
    notice_path = REPO / "NOTICE.md"
    if not notice_path.exists():
        err("NOTICE.md missing")
        return
    notice_lower = notice_path.read_text().lower()

    mkt_path = REPO / ".claude-plugin/marketplace.json"
    if not mkt_path.exists():
        return
    try:
        mkt = json.loads(mkt_path.read_text())
    except json.JSONDecodeError:
        return

    for plugin in mkt.get("plugins", []):
        name = plugin.get("name", "")
        if not name:
            continue
        if name.lower() not in notice_lower:
            err(
                f"NOTICE: plugin '{name}' not mentioned in NOTICE.md "
                f"(add it under 'Original to this repo' or attribute its upstream)"
            )


def check_install_sh(skills: list[tuple[Path, str]]) -> None:
    """install.sh --list output must equal the discovered skill set."""
    install_sh = REPO / "install.sh"
    if not install_sh.exists():
        err("install.sh missing")
        return
    if not install_sh.stat().st_mode & 0o100:
        err("install.sh is not executable")
        return

    try:
        proc = subprocess.run(
            [str(install_sh), "--list"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except subprocess.TimeoutExpired:
        err("install.sh --list timed out")
        return

    if proc.returncode != 0:
        err(f"install.sh --list exited {proc.returncode}: {proc.stderr.strip()}")
        return

    listed = {ln.strip() for ln in proc.stdout.splitlines() if ln.strip()}
    discovered = {name for _, name in skills}

    for name in sorted(discovered - listed):
        err(f"install.sh --list missed skill: '{name}'")
    for name in sorted(listed - discovered):
        err(f"install.sh --list returned unknown name: '{name}'")


# ---------- entrypoint ----------


def main() -> None:
    skills = find_skills()
    print(f"discovered {len(skills)} skills")

    print("\n[tier 1]")
    check_json_files()
    check_skills_tier1(skills)
    check_marketplace()

    print("[tier 2]")
    check_skills_tier2(skills)
    check_notice()
    check_install_sh(skills)

    if ERRORS:
        print(f"\n{len(ERRORS)} error(s):", file=sys.stderr)
        for e in ERRORS:
            print(f"  ✗ {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n✓ all checks passed ({len(skills)} skills validated)")


if __name__ == "__main__":
    main()
