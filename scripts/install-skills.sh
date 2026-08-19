#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"
RUNTIME_DIR="$REPO_ROOT/runtime/codoop-flow"

SKILLS=(
  codoop-init
  grilling
  codoop-discover
  codoop-ticket
  spec-driven-development
  planning-and-task-breakdown
  definition-of-done
  codoop-ux-walkthrough
  codoop-execute
  incremental-implementation
  debugging-and-error-recovery
  test-driven-development
)

DRY_RUN=0
AGENT="auto"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)   DRY_RUN=1 ;;
    --agent)     AGENT="$2"; shift ;;
    --agent=*)   AGENT="${1#--agent=}" ;;
    -h|--help)   echo "Usage: install-skills.sh [--agent codex|claude|cursor|all] [--dry-run]"; exit 0 ;;
    *)           echo "Unknown option: $1" >&2; exit 1 ;;
  esac
  shift
done

TARGETS=()
if [[ "$AGENT" == "auto" || "$AGENT" == "codex"  || "$AGENT" == "all" ]]; then
  TARGETS+=("codex:${CODEX_HOME:-$HOME/.codex}/skills")
fi
if [[ "$AGENT" == "auto" || "$AGENT" == "claude" || "$AGENT" == "all" ]]; then
  TARGETS+=("claude:${CLAUDE_HOME:-$HOME/.claude}/skills")
fi
if [[ "$AGENT" == "auto" || "$AGENT" == "cursor" || "$AGENT" == "all" ]]; then
  TARGETS+=("cursor:${CURSOR_HOME:-$HOME/.cursor}/skills")
fi

_install_to() {
  local label="$1" dest_base="$2"
  local agent_home dest_runtime
  agent_home="$(dirname "$dest_base")"
  dest_runtime="$agent_home/runtime/codoop-flow"
  echo ""
  echo "==> $label  →  $dest_base"
  [[ $DRY_RUN -eq 0 ]] && mkdir -p "$dest_base"

  if [[ $DRY_RUN -eq 1 ]]; then
    echo "  [dry-run] runtime/codoop-flow"
  else
    mkdir -p "$agent_home/runtime"
    rm -rf "$dest_runtime" && cp -R "$RUNTIME_DIR" "$dest_runtime"
    echo "  + runtime/codoop-flow"
  fi

  for skill in "${SKILLS[@]}"; do
    local src="$SKILLS_DIR/$skill"
    if [[ ! -d "$src" ]]; then echo "  WARN: $src not found — skipping"; continue; fi
    if [[ $DRY_RUN -eq 1 ]]; then echo "  [dry-run] $skill"; else
      rm -rf "$dest_base/$skill" && cp -R "$src" "$dest_base/$skill"
      echo "  + $skill"
    fi
  done
}

for entry in "${TARGETS[@]}"; do
  _install_to "${entry%%:*}" "${entry#*:}"
done

cat <<'EOF'

==> Cursor (plugin install, preferred)
Cursor reads the same SKILL.md format and ships a plugin system. Prefer
installing the whole plugin so skills and the Runtime stay adjacent:

  # local development: symlink the repo, then reload Cursor
  ln -s "$(pwd)" ~/.cursor/plugins/local/codoop-flow

The manifest lives at .cursor-plugin/plugin.json. The script's --agent cursor
copy above ($HOME/.cursor/skills + runtime) is a fallback for when the plugin
system is unavailable.

==> Other agents (Gemini / etc.)
Copy each skill directory plus the Runtime, keeping them adjacent:

  cp -R skills/<name>       <agent-skills-dir>/    # for each of the 12 skills
  cp -R runtime/codoop-flow <agent-home>/runtime/

Gemini CLI: see ~/.gemini/skills/ or the agent's documented path.
EOF

echo ""
echo "Done. Re-run at any time to update skills in place."
