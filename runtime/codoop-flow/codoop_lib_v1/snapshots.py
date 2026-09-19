"""Read-only checks for agent-authored UI baselines; no rendering or API access."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

SNAPSHOT_DIR = Path('.codoop-flow/ui-snapshots')


def _file(repo: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError('expected a repository-relative file path')
    path = repo / relative
    if '..' in Path(relative).parts or not path.resolve().is_relative_to(repo.resolve()):
        raise ValueError(f'path escapes repository: {relative}')
    if not path.is_file():
        raise ValueError(f'file missing: {relative}')
    return path


def fingerprints(repo: Path, paths: list[str]) -> dict[str, str]:
    return {path: hashlib.sha256(_file(repo, path).read_bytes()).hexdigest()
            for path in sorted(set(paths))}


def check_page(repo: Path, page_id: str) -> dict:
    """A valid hash is necessary, not proof of visual fidelity or full dependencies."""
    result = {'page_id': page_id, 'reusable': False, 'reasons': []}
    try:
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', page_id):
            raise ValueError('page ID must contain lowercase words separated by hyphens')
        index = json.loads(_file(repo, str(SNAPSHOT_DIR / 'index.json')).read_text())
        if not isinstance(index, dict) or index.get('schema_version') != 1 or not isinstance(index.get('pages'), dict):
            raise ValueError('invalid snapshot index; preserve it and rebuild from source')
        page = index['pages'].get(page_id)
        if not isinstance(page, dict):
            raise ValueError('page not indexed')
        if page.get('status') != 'verified':
            raise ValueError(f"page is not verified: {page.get('reason') or page.get('status')}")
        for field in ('name', 'entry', 'revision', 'evidence'):
            if not isinstance(page.get(field), str) or not page[field].strip():
                raise ValueError(f'page missing {field}')
        if page.get('project') not in ('web', 'desktop', 'mobile'):
            raise ValueError('invalid UI project type')
        viewport = page.get('viewport')
        if not isinstance(viewport, list) or len(viewport) != 2 or any(type(n) is not int or n <= 0 for n in viewport):
            raise ValueError('viewport must be [width, height]')
        sources = page.get('sources')
        if not isinstance(sources, dict) or not sources:
            raise ValueError('page must fingerprint source files and shared dependencies')
        html = str(SNAPSHOT_DIR / 'pages' / f'{page_id}.html')
        if page.get('snapshot') != html:
            raise ValueError(f'snapshot must be {html}')
        expected = {**sources, html: page.get('snapshot_sha256')}
        if any(not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value) for value in expected.values()):
            raise ValueError('invalid SHA-256 fingerprint')
        actual = fingerprints(repo, list(expected))
        result['reasons'] = [f'changed: {path}' for path in expected if expected[path] != actual[path]]
        result['reusable'] = not result['reasons']
    except (OSError, ValueError, TypeError) as exc:
        result['reasons'] = [str(exc)]
    return result
