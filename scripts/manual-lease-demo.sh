#!/usr/bin/env bash
# Manual end-to-end demo of the ticket-lease concurrency fix.
#
# Reproduces the original bug scenario ("two runners resume the same
# in_progress ticket") and shows it is now blocked. Uses a throwaway target
# repo in a temp dir and cleans up on exit — it never touches your real repos.
#
#   bash scripts/manual-lease-demo.sh
#
# Each step prints EXPECT (what should happen) then the actual CLI JSON.
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOLS="$ROOT/skills/codoop-execute/scripts/codoop_tools.py"
PY="${PYTHON:-python3}"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

TARGET="$TMP/target_repo"
WORKTREES="$TMP/worktrees"
CFG="$TMP/codoop_flow.toml"

hr()  { printf '\n\033[1m=== %s ===\033[0m\n' "$1"; }
exp() { printf '\033[36mEXPECT:\033[0m %s\n' "$1"; }
run() { printf '\033[33m$ %s\033[0m\n' "$*"; "$@"; echo; }

# --- scaffold a throwaway target repo + one pending ticket -------------------
hr "setup: throwaway target repo + pending ticket"
mkdir -p "$TARGET/backend" "$TARGET/script"
: > "$TARGET/backend/.keep"
git -C "$TARGET" init -q
git -C "$TARGET" config user.email demo@codoop.local
git -C "$TARGET" config user.name "codoop demo"
git -C "$TARGET" add -A
git -C "$TARGET" commit -qm init
mkdir -p "$TARGET/docs/tickets/"{pending,in_progress,done,failed}

TID="demo-ticket"
PDIR="$TARGET/docs/tickets/pending/$TID"
mkdir -p "$PDIR"
cat > "$PDIR/metadata.json" <<JSON
{
  "ticket_id": "$TID",
  "title": "lease demo",
  "modules": ["backend"],
  "files_to_edit": ["backend/**"],
  "max_healing_attempts": 3
}
JSON
printf '# PRD\nbuild a thing\n' > "$PDIR/module_prd.md"
printf '# Todo\n- [x] step one\n- [ ] step two\n- [ ] step three\n' > "$PDIR/todo.md"

cat > "$CFG" <<TOML
target_repo = "$TARGET"
worktree_root = "$WORKTREES"
TOML
echo "target repo: $TARGET"
echo "config:      $CFG"

TOOL() { "$PY" "$TOOLS" --config "$CFG" "$@"; }

# --- 1. first runner picks + gets a lease token ------------------------------
hr "1. runner A picks the ticket"
exp "picked:true, plus a lease_token"
FIRST="$(TOOL pick --runner-note runner-A)"
echo "$FIRST"
TOKEN="$("$PY" -c 'import sys,json;print(json.load(sys.stdin).get("lease_token",""))' <<<"$FIRST")"
WT="$("$PY" -c 'import sys,json;print(json.load(sys.stdin).get("worktree",""))' <<<"$FIRST")"
echo
echo "captured lease_token = $TOKEN"

# Runner A does some work in its worktree.
echo "runner-A-was-here" > "$WT/backend/work.txt"

# --- 2. THE BUG: a second runner tries to resume without the token -----------
hr "2. runner B tries to resume WITHOUT the token (the original bug)"
exp "reason:blocked_by_active_runner, exit code != 0, worktree NOT rebuilt"
if TOOL pick --runner-note runner-B; then
  echo ">>> exit code 0  (BAD — B was let in!)"
else
  echo ">>> exit code $?  (GOOD — B was blocked)"
fi
echo
if [ "$(cat "$WT/backend/work.txt" 2>/dev/null)" = "runner-A-was-here" ]; then
  echo ">>> runner A's work is intact (GOOD)"
else
  echo ">>> runner A's work was clobbered (BAD)"
fi

# --- 3. runner A resumes WITH its token --------------------------------------
hr "3. runner A resumes WITH its token"
exp "reason:resumed, same lease_token, exit 0"
run TOOL pick --lease "$TOKEN"

# --- 4. status shows how far the room got ------------------------------------
hr "4. status: how far did the room get?"
exp "in_progress[0] shows held_by=runner-A, todo=1/3, worktree_dirty=true"
run TOOL status

# --- 5. human hand-off: takeover rotates the token ---------------------------
hr "5. human runs takeover -> new token; old token now rejected"
exp "takeover ok:true with a NEW lease_token"
NEW="$(TOOL takeover "$TID" --runner-note runner-C)"
echo "$NEW"
NEWTOKEN="$("$PY" -c 'import sys,json;print(json.load(sys.stdin).get("lease_token",""))' <<<"$NEW")"
echo
exp "verify with the OLD token is rejected (lease_token_mismatch, exit != 0)"
if TOOL verify "$TID" --lease "$TOKEN"; then
  echo ">>> exit 0 (BAD — stale token accepted)"
else
  echo ">>> exit $? (GOOD — stale token rejected)"
fi
echo
exp "verify with the NEW token passes"
run TOOL verify "$TID" --lease "$NEWTOKEN"

# --- 6. finish releases the lease --------------------------------------------
hr "6. finish releases the lease"
exp "state:done; lease file removed"
run TOOL finish "$TID" --lease "$NEWTOKEN" --message "feat(backend): demo [$TID]"
if [ -f "$WORKTREES/.codoop-leases/$TID.json" ]; then
  echo ">>> lease file still present (BAD)"
else
  echo ">>> lease file removed (GOOD)"
fi

hr "done — temp dir will be cleaned up"
