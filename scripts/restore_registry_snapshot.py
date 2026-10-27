#!/usr/bin/env python3
"""Rehydrate the committed snapshot without drifting to a newer main revision."""
import json
import hashlib
from pathlib import Path
from restore_data import fetch, sha256_file
ROOT = Path(__file__).resolve().parents[1]

def main():
    man = json.loads((ROOT/'registry/focus_registry_manifest.json').read_text())
    for row in man['rasters']:
        if row['status'] != 'ok':
            raise ValueError('snapshot contains failed sources')
        path = ROOT/row['local']
        if not path.exists() or sha256_file(path) != row['sha256']:
            fetch(f"buffedlizard55-lab/{row['repo']}", row['ref'], row['path'], path)
        if sha256_file(path) != row['sha256']:
            path.unlink()
            raise ValueError(f'SHA256 mismatch: {row["path"]}')
    print(f"Verified {len(man['rasters'])} pinned registry files")

if __name__ == '__main__': main()
