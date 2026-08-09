"""Ticket lease (runner ownership) — the "one worker per room" key.

The problem this solves: `pick` prevents claiming a *new* ticket twice, but it
did not prevent two runners from both *resuming* the same in_progress ticket and
concurrently writing the same worktree. A lease gives each in_progress ticket an
owner: `pick` mints a random `token` for the first runner, and every later
command must present that token to prove ownership. A runner without the token is
turned away (blocked_by_active_runner).

Deliberately simple (see docs/design-runner-lease.md):
  - No TTL, no heartbeat, no background process, no auto-takeover. Liveness is a
    human's call — the human sees "this room's work isn't finished" at review
    time (a ticket still under in_progress/ is by definition unfinished) and runs
    `takeover` to hand it to a fresh runner.
  - Lease files live in a RUNTIME dir (under worktree_root), never inside the
    target repo's docs/tickets/ (which may get `git add`-ed).
"""

from __future__ import annotations

import json
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

LEASE_DIRNAME = ".codoop-leases"


@dataclass
class Lease:
    ticket_id: str
    token: str
    worktree: str
    acquired_at: str
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "ticket_id": self.ticket_id,
            "token": self.token,
            "worktree": self.worktree,
            "acquired_at": self.acquired_at,
            "note": self.note,
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def leases_dir(worktree_root: Path) -> Path:
    return worktree_root / LEASE_DIRNAME


def _lease_path(worktree_root: Path, ticket_id: str) -> Path:
    return leases_dir(worktree_root) / f"{ticket_id}.json"


def read_lease(worktree_root: Path, ticket_id: str) -> Lease | None:
    """Return the current lease for a ticket, or None if the room has no owner.

    A malformed lease file is treated as "no owner" (safe degrade): the ticket
    can then be resumed/rebuilt rather than being permanently locked.
    """
    path = _lease_path(worktree_root, ticket_id)
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return Lease(
            ticket_id=raw["ticket_id"],
            token=raw["token"],
            worktree=raw.get("worktree", ""),
            acquired_at=raw.get("acquired_at", ""),
            note=raw.get("note", ""),
        )
    except (json.JSONDecodeError, KeyError, OSError):
        return None


def mint_lease(worktree_root: Path, ticket_id: str, worktree: Path, note: str = "") -> Lease:
    """Create (or replace) the lease for a ticket and return it, token included.

    Used by both `pick` (first claim / resume of an unowned ticket) and
    `takeover` (human hands the room to a fresh runner, invalidating the old
    token).
    """
    d = leases_dir(worktree_root)
    d.mkdir(parents=True, exist_ok=True)
    lease = Lease(
        ticket_id=ticket_id,
        token=secrets.token_hex(16),
        worktree=str(worktree),
        acquired_at=_now_iso(),
        note=note or "",
    )
    _lease_path(worktree_root, ticket_id).write_text(
        json.dumps(lease.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return lease


def release_lease(worktree_root: Path, ticket_id: str) -> None:
    """Delete a ticket's lease (room emptied). Best-effort; missing = no-op."""
    try:
        _lease_path(worktree_root, ticket_id).unlink()
    except FileNotFoundError:
        pass


def token_matches(worktree_root: Path, ticket_id: str, token: str | None) -> bool:
    """True iff a lease exists and the presented token matches it."""
    if not token:
        return False
    lease = read_lease(worktree_root, ticket_id)
    return lease is not None and secrets.compare_digest(lease.token, token)


# --- pipeline lock: serialize the pick critical section (fixes double-pick) ---
#
# `pick` reads in_progress + moves a pending dir + writes a lease. That sequence
# is not atomic: two concurrent first-picks could both pass the empty check. A
# short-held, atomically-created lock file serializes just the bookkeeping (held
# for milliseconds, NOT for the whole build). Keyed by target_repo so multiple
# targets sharing one worktree_root don't block each other.


class PipelineLock:
    """Context manager: atomic O_CREAT|O_EXCL lock around the pick bookkeeping.

    On a stale lock (holder pid gone), reclaims it — this is the millisecond
    pick-level lock, NOT ticket-level liveness (which is a human's call).
    """

    def __init__(self, worktree_root: Path, target_repo: Path):
        import hashlib
        key = hashlib.sha1(str(target_repo).encode("utf-8")).hexdigest()[:12]
        self._dir = leases_dir(worktree_root)
        self._path = self._dir / f".pipeline.{key}.lock"

    def __enter__(self) -> "PipelineLock":
        self._dir.mkdir(parents=True, exist_ok=True)
        self._acquire()
        return self

    def __exit__(self, *exc) -> None:
        try:
            self._path.unlink()
        except FileNotFoundError:
            pass

    def _acquire(self) -> None:
        for _ in range(500):  # ~5s worst case; pick bookkeeping is sub-ms
            try:
                fd = os.open(str(self._path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode("ascii"))
                os.close(fd)
                return
            except FileExistsError:
                if self._reclaim_if_stale():
                    continue
                import time
                time.sleep(0.01)
        # Give up waiting and force-reclaim: the holder is wedged.
        self._reclaim_if_stale(force=True)
        fd = os.open(str(self._path), os.O_CREAT | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode("ascii"))
        os.close(fd)

    def _reclaim_if_stale(self, force: bool = False) -> bool:
        try:
            holder = int(self._path.read_text(encoding="ascii").strip() or "0")
        except (OSError, ValueError):
            holder = 0
        if not force and holder and _pid_alive(holder):
            return False
        try:
            self._path.unlink()
        except FileNotFoundError:
            pass
        return True


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True
