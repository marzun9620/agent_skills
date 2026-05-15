#!/usr/bin/env bash
# Symlink skill directories from this repo into ~/.claude/skills/.
# Safe to re-run: skips existing correct symlinks, warns on conflicts.
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
  sed -n '2,9p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

list_available() {
  for skill_path in "${REPO_DIR}"/*/; do
    skill_name="$(basename "${skill_path}")"
    case "${skill_name}" in _*|.*) continue ;; esac
    [[ -f "${skill_path}SKILL.md" ]] && echo "${skill_name}"
  done
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
skipped=0
conflicts=0
missing=0

for skill_name in "${requested[@]}"; do
  skill_path="${REPO_DIR}/${skill_name}/"

  if [[ ! -d "${skill_path}" ]]; then
    echo "MISSING: no directory '${skill_name}' in repo; skipping" >&2
    missing=$((missing + 1))
    continue
  fi
  if [[ ! -f "${skill_path}SKILL.md" ]]; then
    echo "MISSING: '${skill_name}' has no SKILL.md; skipping" >&2
    missing=$((missing + 1))
    continue
  fi

  link="${TARGET_DIR}/${skill_name}"
  target="${skill_path%/}"

  if [[ -L "${link}" ]]; then
    current="$(readlink "${link}")"
    if [[ "${current}" == "${target}" ]]; then
      skipped=$((skipped + 1))
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
echo "Done. linked=${linked} already-ok=${skipped} conflicts=${conflicts} missing=${missing}"
