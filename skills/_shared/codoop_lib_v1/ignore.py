"""Shared filter for build-generated noise.

Engines run tests during build (e.g. pytest), which produces artifacts like
__pycache__/*.pyc. These are not the engine's intended edits, so they must be
excluded from the review diff (and any tooling that inspects changed files)
— otherwise every Python ticket gets spuriously flagged.
"""

from __future__ import annotations

import fnmatch

# Glob patterns matched against repo-relative paths.
GENERATED_GLOBS: tuple[str, ...] = (
    "**/__pycache__/**",
    "*.pyc",
    "*.pyo",
    "**/.pytest_cache/**",
    "**/node_modules/**",
    "**/.DS_Store",
    "**/*.egg-info/**",
)

# git pathspecs (for `:(exclude)...`) covering the same artifacts.
GENERATED_PATHSPECS: tuple[str, ...] = (
    "**/__pycache__/**",
    "*.pyc",
    "*.pyo",
    "**/.pytest_cache/**",
    "**/node_modules/**",
    ".DS_Store",
    "**/*.egg-info/**",
)


def is_generated(path: str) -> bool:
    return any(fnmatch.fnmatch(path, g) for g in GENERATED_GLOBS)
