#!/usr/bin/env bash
# Symlink skill directories from this repo into ~/.claude/skills/.
# Safe to re-run: skips existing correct symlinks, auto-repairs stale ones
# pointing into this repo, warns on external conflicts.
#
# Usage:
#   ./install.sh                       # install every skill in this repo
#   ./install.sh <skill-name> [more…]  # install only the named skills
#   ./install.sh --list                # list available skills and exit
#   ./install.sh --help                # show this help

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${HOME}/.claude/skills"

usage() {
  sed -n '2,10p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

# Find every SKILL.md, derive its directory name as the skill name.
# Skip _-prefixed segments (e.g. _template/, _helpers/) and .git.
list_available() {
  find "${REPO_DIR}" -type f -name SKILL.md \
    -not -path "*/_*" -not -path "*/.git/*" \
    -exec dirname {} \; \
  | while read -r dir; do basename "$dir"; done \
  | sort -u
}

# Locate a skill's source dir by name (used by selective install).
# Returns empty if not found.
find_skill_path() {
  find "${REPO_DIR}" -type d -name "$1" \
    -not -path "*/_*" -not -path "*/.git/*" \
    2>/dev/null | head -1
}

# Argument parsing
case "${1:-}" in
  --help|-h) usage; exit 0 ;;
  --list|-l) list_available; exit 0 ;;
esac

# Build the list of skills to install
declare -a requested
if [[ $# -eq 0 ]]; then
  while IFS= read -r name; do requested+=("$name"); done < <(list_available)
else
  requested=("$@")
fi

mkdir -p "${TARGET_DIR}"

linked=0
updated=0
skipped=0
conflicts=0
missing=0

for skill_name in "${requested[@]}"; do
  skill_path="$(find_skill_path "${skill_name}")"

  if [[ -z "${skill_path}" || ! -d "${skill_path}" ]]; then
    echo "MISSING: no directory '${skill_name}' in repo; skipping" >&2
    missing=$((missing + 1))
    continue
  fi
  if [[ ! -f "${skill_path}/SKILL.md" ]]; then
    echo "MISSING: '${skill_name}' has no SKILL.md; skipping" >&2
    missing=$((missing + 1))
    continue
  fi

  link="${TARGET_DIR}/${skill_name}"
  target="${skill_path}"

  if [[ -L "${link}" ]]; then
    current="$(readlink "${link}")"
    if [[ "${current}" == "${target}" ]]; then
      skipped=$((skipped + 1))
      continue
    fi
    if [[ "${current}" == "${REPO_DIR}/"* ]]; then
      # Stale symlink pointing into this repo at a different path
      # (e.g. pre-reorg flat path) — update it.
      ln -sfn "${target}" "${link}"
      echo "updated: ${skill_name}  (was: ${current#${REPO_DIR}/})"
      updated=$((updated + 1))
      continue
    fi
    echo "WARN: ${link} -> ${current} (expected ${target}); leaving alone" >&2
    conflicts=$((conflicts + 1))
    continue
  fi

  if [[ -e "${link}" ]]; then
    echo "WARN: ${link} exists and is not a symlink; leaving alone" >&2
    conflicts=$((conflicts + 1))
    continue
  fi

  ln -s "${target}" "${link}"
  echo "linked: ${skill_name}"
  linked=$((linked + 1))
done

echo
echo "Done. linked=${linked} updated=${updated} already-ok=${skipped} conflicts=${conflicts} missing=${missing}"
