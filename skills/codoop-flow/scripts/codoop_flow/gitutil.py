"""Thin subprocess wrapper around git. No intelligence — just deterministic
plumbing the guardrail CLI relies on.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


class GitError(Exception):
    pass


def git(*args: str, cwd: Path) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise GitError(
            f"git {' '.join(args)} (cwd={cwd}) failed [{proc.returncode}]:\n{proc.stderr}"
        )
    return proc.stdout


def branch_exists(repo: Path, branch: str) -> bool:
    proc = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"],
        cwd=str(repo),
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0
