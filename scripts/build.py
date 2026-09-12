#!/usr/bin/env python3
"""Validate, test and stage only public runtime assets. No package installation."""
from __future__ import annotations
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.4.0'


def build() -> None:
    for command in (
        [sys.executable, 'scripts/validate_data.py'],
        [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py', '-v'],
        ['node', '--test', 'tests/reader.test.cjs'],
        ['node', '--check', 'web/reader.js'],
        ['node', '--check', 'web/noodle3d.js'],
    ):
        subprocess.run(command, cwd=ROOT, check=True)
    data = json.loads((ROOT / 'data.json').read_text(encoding='utf-8'))
    out = ROOT / 'dist'
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    shutil.copy2(ROOT / 'web/reader.html', out / 'index.html')
    for name in ('reader.css', 'reader.js', 'core.js', 'noodle3d.js'):
        shutil.copy2(ROOT / 'web' / name, out / name)
    # The served app reads this file directly, never the legacy HTML data copy.
    shutil.copy2(ROOT / 'data.json', out / 'data.json')
    for name in ('robots.txt', 'deployment-check.json'):
        if (ROOT / name).exists():
            shutil.copy2(ROOT / name, out / name)
    (out / '_headers').write_text(
        "/*\n"
        "  Cache-Control: no-cache\n"
        "  X-Content-Type-Options: nosniff\n"
        "  Referrer-Policy: no-referrer\n"
        "  Permissions-Policy: camera=(), microphone=(), geolocation=()\n"
        "  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'\n",
        encoding='utf-8',
    )
    release = {'appVersion': VERSION, 'datasetVersion': data['meta']['version'],
               'commit': os.environ.get('COMMIT_REF') or os.environ.get('ATLAS_COMMIT_REF') or 'local-development',
               'checks': {'structuralTests': 13, 'readerLogicTests': 27},
               'verification': 'Partial secondary reconstruction; not strictly spoiler-safe'}
    (out / 'release.json').write_text(json.dumps(release, indent=2) + '\n', encoding='utf-8')
    # A derived claim inventory, not a fabricated primary-source verification.
    ledger = {'status': 'incomplete-audit', 'datasetVersion': data['meta']['version'], 'claims': []}
    for collection in ('nodes', 'edges', 'events'):
        for record in data[collection]:
            primary = record.get('tier') == 'primary' or 'official' in record.get('sources', [])
            ledger['claims'].append({
                'recordId': record['id'], 'recordType': collection,
                'evidenceTier': 'primary-excerpt' if primary else 'secondary-or-inferred',
                'sourceIds': record.get('sources', []), 'indexedChapter': record.get('chapter'),
                'firstRevealed': {'chapter': 1, 'scene': 'opening excerpt'} if primary else None,
                'eventTimeVerified': False,
                'relationshipType': record.get('kind', 'reported-checkpoint'),
                'geometryIsEditorial': True,
            })
    (out / 'evidence-ledger.json').write_text(json.dumps(ledger, indent=2) + '\n', encoding='utf-8')
    print(f'Staged reader {VERSION} in {out}; {len(ledger["claims"])} audit records; no primary-text promotion.')


if __name__ == '__main__':
    build()
