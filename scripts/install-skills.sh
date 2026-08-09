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
    -h|--help)   echo "Usage: install-skills.sh [--agent codex|claude|all] [--dry-run]"; exit 0 ;;
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

==> Other agents (Cursor / Gemini / etc.)
Copy each skill directory into your agent's rules/skills location:

  cp -R skills/codoop-discover                <agent-skills-dir>/
  cp -R skills/codoop-init                    <agent-skills-dir>/
  cp -R skills/grilling                       <agent-skills-dir>/
  cp -R skills/codoop-ticket                  <agent-skills-dir>/
  cp -R skills/spec-driven-development        <agent-skills-dir>/
  cp -R skills/planning-and-task-breakdown    <agent-skills-dir>/
  cp -R skills/definition-of-done             <agent-skills-dir>/
  cp -R skills/codoop-ux-walkthrough          <agent-skills-dir>/
  cp -R skills/codoop-execute                 <agent-skills-dir>/
  cp -R skills/incremental-implementation     <agent-skills-dir>/
  cp -R skills/debugging-and-error-recovery   <agent-skills-dir>/
  cp -R skills/test-driven-development        <agent-skills-dir>/
  cp -R runtime/codoop-flow                   <agent-home>/runtime/

Cursor: place each SKILL.md in .cursor/rules/, or point the agent at skills/.
Gemini CLI: see ~/.gemini/skills/ or the agent's documented path.
EOF

echo ""
echo "Done. Re-run at any time to update skills in place."
