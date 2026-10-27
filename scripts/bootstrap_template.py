#!/usr/bin/env python3
"""Restore the pinned shared template and core mirror, then prepare its feature cache.

This does NOT run a geological experiment or generate a submission. Mirror bytes
are checksum-pinned but NOT authenticated organizer downloads. Large data and the
upstream archive live in ignored scratch storage and may need to be regenerated.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from restore_references import digest  # noqa: E402

CONFIG = ROOT / "registry" / "template_tools.json"
CACHE = ROOT / ".cache"
TEMPLATE = CACHE / "template32"


def verify(config: dict, directory: Path = TEMPLATE) -> None:
    for name, expected in config["files"].items():
        path = directory / name
        if not path.is_file() or digest(path) != expected:
            raise ValueError(f"Missing or changed pinned template file: {path}")


def extract_archive(archive: Path, directory: Path) -> None:
    """Extract regular files and directories only, disallowing traversal or links."""
    with tarfile.open(archive, "r:gz") as tf:
        for member in tf:
            parts = PurePosixPath(member.name).parts
            if not parts or len(parts) == 1:
                continue
            relative = PurePosixPath(*parts[1:])
            if relative.is_absolute() or any(p in ("..", "") for p in relative.parts):
                raise ValueError(f"Unsafe template archive path: {member.name}")
            out = directory.joinpath(*relative.parts)
            if member.isdir():
                out.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                out.parent.mkdir(parents=True, exist_ok=True)
                src = tf.extractfile(member)
                if src is None:
                    raise ValueError(f"Cannot extract {member.name}")
                with src, out.open("wb") as dst:
                    shutil.copyfileobj(src, dst, 1024 * 1024)
            else:
                raise ValueError(f"Unexpected link or special file in template archive: {member.name}")


def ensure_template(config: dict) -> None:
    if TEMPLATE.exists():
        verify(config)
        return
    CACHE.mkdir(parents=True, exist_ok=True)
    archive = CACHE / "template32.tar.gz.partial"
    temporary = CACHE / "template32.extracting"
    if temporary.exists():
        raise ValueError(f"Incomplete prior extraction exists: {temporary}")
    try:
        api = f"repos/{config['upstream']}/tarball/{config['commit']}"
        with archive.open("wb") as out:
            subprocess.run(["gh", "api", api], stdout=out, check=True, timeout=300)
        temporary.mkdir()
        extract_archive(archive, temporary)
        verify(config, temporary)
        temporary.rename(TEMPLATE)
    finally:
        archive.unlink(missing_ok=True)
        if temporary.exists():
            shutil.rmtree(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true", help="Only check already-restored critical template files")
    parser.add_argument("--skip-stack", action="store_true", help="Restore and prepare data but do not build the larger shared stack")
    args = parser.parse_args()
    try:
        config = json.loads(CONFIG.read_text())
        if args.verify_only:
            verify(config)
            print("Pinned critical template files verified; this is not an organizer or model validation.")
            return 0
        ensure_template(config)
        env = os.environ.copy()
        env["GEMS_DATA_DIR"] = str(CACHE / "data")
        env["GEMS_WORK_DIR"] = str(CACHE / "work")
        shared = TEMPLATE / "scripts"
        subprocess.run([sys.executable, str(shared / "restore_data.py"), "--group", "core",
                        "--target-dir", env["GEMS_DATA_DIR"]], check=True, cwd=ROOT, env=env)
        subprocess.run([sys.executable, str(shared / "prepare_data.py")], check=True, cwd=ROOT, env=env)
        if not args.skip_stack:
            subprocess.run([sys.executable, str(shared / "build_features.py"), "--receipt",
                            str(CACHE / "work" / "feature_receipt.json")], check=True, cwd=ROOT, env=env)
        verify(config)
        print("Prepared shared scratch data. No model, holdout, or submission was created.")
    except (OSError, ValueError, subprocess.SubprocessError, tarfile.TarError) as exc:
        print(f"Bootstrap failed closed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
