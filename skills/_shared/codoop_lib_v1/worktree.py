"""Git worktree lifecycle for isolated per-ticket development.

Flow (per design section 6.3):
  1. `git worktree prune` — clear stale worktree refs.
  2. branch dev/[ticket_id] exists  -> reuse: add worktree + reset --hard (retry).
     branch missing                 -> fresh: add worktree with -b (first run).
  3. on completion -> `git worktree remove --force`.
"""

from __future__ import annotations

from pathlib import Path

from .gitutil import branch_exists, git


class Worktree:
    def __init__(self, target_repo: Path, worktree_root: Path, ticket_id: str):
        self.target_repo = target_repo
        self.ticket_id = ticket_id
        self.branch = f"dev/{ticket_id}"
        self.path = worktree_root / ticket_id

    def create(self) -> Path:
        git("worktree", "prune", cwd=self.target_repo)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # If a worktree path already lingers, remove it first.
        if self.path.exists():
            self._safe_remove()

        if branch_exists(self.target_repo, self.branch):
            # Retry scenario: attach to existing branch, then scrub clean.
            git("worktree", "add", str(self.path), self.branch, cwd=self.target_repo)
            git("reset", "--hard", "HEAD", cwd=self.path)
        else:
            # First run: create branch + isolated worktree.
            git("worktree", "add", "-b", self.branch, str(self.path), cwd=self.target_repo)

        return self.path

    def remove(self) -> None:
        self._safe_remove()

    def _safe_remove(self) -> None:
        try:
            git("worktree", "remove", "--force", str(self.path), cwd=self.target_repo)
        except Exception:
            # Best-effort; prune will reconcile refs on the next create().
            pass
